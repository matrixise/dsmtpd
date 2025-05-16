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

from dsmtpd import __name__
from dsmtpd import __version__

LOGGERNAME = "dsmtpd"

DEFAULT_INTERFACE = "127.0.0.1"
DEFAULT_PORT = 1025

log = logging.getLogger(LOGGERNAME)


# the default logging (all in level INFO) is too verbose
logging.getLogger('mail.log').level = logging.WARNING


@contextlib.contextmanager
def create_maildir(maildir, create=True):
    mbox = mailbox.Maildir(maildir, create=create)
    try:
        mbox.lock()
        yield mbox

    finally:
        mbox.unlock()


class DsmtpdHandler(Mailbox):
    async def handle_DATA(self, server, session, envelope):
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
        "--interface", "-i", help="Specify the interface", default=DEFAULT_INTERFACE,
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
    parser.add_argument("--version", action="version", version=__version__)

    return parser.parse_args()


def main():
    logging.basicConfig(
        format="%(asctime)-15s %(levelname)s: %(message)s", level=logging.INFO
    )
    opts = parse_args()

    try:
        log.info(
            "Starting {0} {1} at {2}:{3} size limit {4}".format(
                __name__, __version__, opts.interface, opts.port, None if opts.max_size == 0 else opts.max_size
            )
        )

        if opts.directory:
            try:
                with create_maildir(opts.directory) as maildir:
                    if len(maildir) > 0:
                        log.info(
                            "Found a Maildir storage with {} mails".format(len(maildir))
                        )
            except:
                log.fatal(
                    "{} must be either non-existing (at a place where "
                    "it can be created) or an existing Maildir "
                    "storage".format(opts.directory)
                )
                raise

            log.info("Storing the incoming emails into {}".format(opts.directory))
        controller = Controller(DsmtpdHandler(opts.directory), hostname=opts.interface, port=opts.port, data_size_limit=opts.max_size)
        controller.start()
        asyncio.get_event_loop().run_forever()
        controller.stop()

    except KeyboardInterrupt:
        log.info("Cleaning up")

    return 0


if __name__ == "__main__":
    sys.exit(main())
