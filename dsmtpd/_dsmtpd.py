#!/usr/bin/env python
"""
Usage:
    dsmtpd [-i <iface>] [-p <port>]

Options:
    -p <port>      Specify the port for the SMTP server [default: 1025]
    -i <iface>     Specify the interface [default: 127.0.0.1]
    -h --help
    --version
"""
import sys
import smtpd
import asyncore
import logging
import email.message
import email.parser

import docopt

from dsmtpd import __version__
from dsmtpd import __name__

LOGGERNAME = 'dsmtpd'

log = logging.getLogger(LOGGERNAME)


class DebugServer(smtpd.DebuggingServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        headers = email.parser.Parser().parsestr(data)
        values = {
            'peer': ':'.join(map(str, peer)),
            'mailfrom': mailfrom,
            'rcpttos': ', '.join(rcpttos),
            'subject': headers.get('subject'),
        }
        log.info('%(peer)s: %(mailfrom)s -> %(rcpttos)s [%(subject)s]', values)


def main():
    logging.basicConfig(format='%(asctime)-15s %(levelname)s: %(message)s',
                        level=logging.INFO)
    opts = docopt.docopt(__doc__, version=__version__)

    address, port = (opts['-i'], int(opts['-p']),)

    log.info('Starting {0} {1} at {2}:{3}'.format(__name__, __version__, address, port))
    DebugServer((address, port), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        log.info('Cleaning up')

    return 0

if __name__ == '__main__':
    sys.exit(main())
