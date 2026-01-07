#!/usr/bin/env python
"""
dsmtpd/_dsmtpd.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Stephane Wirtel <stephane@wirtel.be>
:license: BSD, see LICENSE for more details
"""

import argparse
import asyncio
import contextlib
import email.parser
import logging
import mailbox
import os
import sys
from email import policy

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox

from dsmtpd import __name__, __version__

LOGGERNAME = "dsmtpd"

DEFAULT_INTERFACE = "127.0.0.1"
DEFAULT_PORT = 1025

log = logging.getLogger(LOGGERNAME)


# the default logging (all in level INFO) is too verbose
logging.getLogger("mail.log").level = logging.WARNING


@contextlib.contextmanager
def create_maildir(maildir, create=True):
    mbox = mailbox.Maildir(maildir, create=create)
    try:
        mbox.lock()
        yield mbox

    finally:
        mbox.unlock()


def ensure_maildir(path):
    """
    Ensure that *path* is a valid Maildir root.
    If *path* does not exist, create a fresh Maildir (tmp/new/cur).
    If *path* exists, create any missing subfolders without wiping content.
    """
    # If path doesn't exist at all → let mailbox.Maildir create the full layout.
    if not os.path.exists(path):
        mailbox.Maildir(path, create=True)
        return

    for sub in ("tmp", "new", "cur"):
        os.makedirs(os.path.join(path, sub), exist_ok=True)


def is_maildir(path):
    "Quick structural check for a Maildir root."
    return all(os.path.isdir(os.path.join(path, sub)) for sub in ("tmp", "new", "cur"))


class DsmtpdHandler(Mailbox):
    async def handle_DATA(self, server, session, envelope):  # noqa: N802
        if isinstance(envelope.content, bytes):  # python 3.13
            headers = email.parser.BytesHeaderParser(policy=policy.compat32).parsebytes(
                envelope.content
            )
        else:
            # in python 3.5 instance(envelope.content, str) is True -> we use the old code
            headers = email.parser.Parser().parsestr(envelope.content)

        values = {
            "peer": ":".join(map(str, session.peer)),
            "mail_from": envelope.mail_from,
            "rcpttos": ", ".join(envelope.rcpt_tos),
            "subject": headers.get("subject"),
        }
        log.info("%(peer)s: %(mail_from)s -> %(rcpttos)s [%(subject)s]", values)

        return await super().handle_DATA(server, session, envelope)


def parse_args():
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="A small SMTP server for the smart developer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--interface",
        "-i",
        help="Specify the interface",
        default=DEFAULT_INTERFACE,
    )
    parser.add_argument("--port", "-p", help="Specify the port", default=DEFAULT_PORT, type=int)
    parser.add_argument(
        "--directory",
        "-d",
        help="Specify a Maildir directory to save the incoming emails",
        default=os.getcwd(),
    )
    parser.add_argument(
        "--max-size",
        "-s",
        help="Maximum message size (default 32 Mebibyte). 0 means no limit.",
        default=33554432,  # default of aiosmtpd
        type=int,
    )
    parser.add_argument(
        "--disable-smtputf8",
        action="store_true",
        help="Disable SMTPUTF8 extension (enabled by default)",
    )
    parser.add_argument("--version", action="version", version=__version__)

    return parser.parse_args()


def main():
    logging.basicConfig(format="%(asctime)-15s %(levelname)s: %(message)s", level=logging.INFO)
    opts = parse_args()

    try:
        size_limit = None if opts.max_size == 0 else opts.max_size
        log.info(
            f"Starting {__name__} {__version__} at {opts.interface}:{opts.port} "
            f"size limit {size_limit}"
        )

        if opts.directory:
            # Make sure it's a valid Maildir, whether or not the path already exists.
            ensure_maildir(opts.directory)

            # Double-check structure (defensive) and log a helpful error if not OK.
            if not is_maildir(opts.directory):
                log.fatal(
                    "%s must be either non-existing (so it can be created) "
                    "or an existing Maildir (tmp/new/cur).",
                    opts.directory,
                )
                return 2

            # Safely open and count messages (no crash if the dir previously lacked subdirs).
            with create_maildir(opts.directory, create=False) as maildir:
                try:
                    counter = len(maildir)
                except FileNotFoundError as exc:
                    # Extremely defensive: repair and retry once.
                    log.warning("Repairing Maildir layout after FileNotFoundError: %s", exc)
                    ensure_maildir(opts.directory)
                    counter = len(maildir)

                if counter > 0:
                    log.info(f"Found a Maildir storage with {counter} mails")

            log.info(f"Storing the incoming emails into {opts.directory}")
        controller = Controller(
            DsmtpdHandler(opts.directory),
            hostname=opts.interface,
            port=opts.port,
            data_size_limit=opts.max_size,
            enable_SMTPUTF8=not opts.disable_smtputf8,
        )
        controller.start()
        asyncio.get_event_loop().run_forever()
        controller.stop()

    except KeyboardInterrupt:
        log.info("Cleaning up")

    return 0


if __name__ == "__main__":
    sys.exit(main())
