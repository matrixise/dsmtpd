#!/usr/bin/env python
"""
    dsmtpd/_dsmtpd.py
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Stephane Wirtel <stephane@wirtel.be>
    :license: BSD, see LICENSE for more details
"""

DOCOPT = """
dsmtpd: A small SMTP server for the smart developer

Usage:
    dsmtpd [-i <iface>] [-p <port>] [-d <directory>]

Options:
    -p <port>      Specify the port for the SMTP server [default: 1025]
    -i <iface>     Specify the interface [default: 127.0.0.1]
    -d <directory> Specify a Maildir directory to save the incoming emails
    -h --help
    --version
"""
import asyncore
import contextlib
from email import policy
import email.message
import email.parser
import email.utils
import logging
import mailbox
import smtpd
import sys
import collections

import docopt

from dsmtpd import __version__
from dsmtpd import __name__

LOGGERNAME = 'dsmtpd'

Config = collections.namedtuple('Config', 'interface port directory')

log = logging.getLogger(LOGGERNAME)

@contextlib.contextmanager
def create_maildir(maildir, create=True):
    mbox = mailbox.Maildir(maildir, create=create)
    try:
        mbox.lock()
        yield mbox

    finally:
        mbox.unlock()


class DebugServer(smtpd.DebuggingServer):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        smtpd.DebuggingServer.__init__(self, (self.config.interface, self.config.port), None)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        if isinstance(data, bytes):
            headers = email.parser.BytesHeaderParser(policy=policy.compat32
                      ).parsebytes(data)
        else:
             # in python 3.5 instance(data, str) is True -> we use the old code
             headers = email.parser.Parser().parsestr(data)

        values = {
            'peer': ':'.join(map(str, peer)),
            'mailfrom': mailfrom,
            'rcpttos': ', '.join(rcpttos),
            'subject': headers.get('subject'),
        }
        log.info('%(peer)s: %(mailfrom)s -> %(rcpttos)s [%(subject)s]', values)

        if self.config.directory:
            with create_maildir(self.config.directory, create=False) as mbox:
                mbox.add(mailbox.mboxMessage(data))


def main():
    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=logging.INFO)
    opts = docopt.docopt(DOCOPT, version=__version__)

    config = Config(opts['-i'], int(opts['-p']), opts['-d'])

    try:
        DebugServer(config)
        log.info('Starting {0} {1} at {2}:{3}'.format(__name__, __version__, config.interface, config.port))

        if config.directory:
            try:
                with create_maildir(config.directory) as maildir:
                    if len(maildir) > 0:
                        log.info('Found a Maildir storage with {} mails'.format(
                                 len(maildir)))
            except:
                log.fatal('{} must be either non-existing (at a place where '
                          'it can be created) or an existing Maildir '
                          'storage'.format(config.directory))
                raise

            log.info('Storing the incoming emails into {}'.format(config.directory))
        asyncore.loop()
    except KeyboardInterrupt:
        log.info('Cleaning up')

    return 0

if __name__ == '__main__':
    sys.exit(main())
