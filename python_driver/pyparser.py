#!/usr/bin/env python3

import io
import abc
import sys
import json
import signal
import logging
import msgpack
import pydetector.detector as detector
from pprint import pformat, pprint
from traceback import format_exc
from python_driver.processor_configs import ProcessorConfigs

logging.basicConfig(filename="pyparser.log", level=logging.WARNING)


class RequestInstantiationException(Exception): pass


# Gracefully handle control c without adding another try-except on top of the loop
def ctrlc_signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, ctrlc_signal_handler)


def get_processor_instance(format_, custom_inbuffer=None, custom_outbuffer=None):
    """
    Get a processor instance. The class and buffers will be selected based on the
    python_driver.ProcessorConfigs dictionary. The input and output buffers can
    be overriden using the custom_inbuffer and custom_outbuffer parameters. This
    is mainly useful for unittesting.
    """
    conf = ProcessorConfigs.get(format_)
    if not conf:
        raise RequestInstantiationException('No RequestProcessor found for format {}'
                .format(format_))

    outbuffer = custom_outbuffer if custom_outbuffer else conf['outbuffer']
    inbuffer = custom_inbuffer if custom_inbuffer else conf['inbuffer']

    instance = conf['class'](outbuffer)
    return instance, inbuffer


def main():
    """
    If you pass the --json command line parameter the replies will be
    printed using pprint without wrapping them in the msgpack format which
    can be handy when debugging.
    """

    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        format_ = 'json'
    else:
        format_ = 'msgpack'

    processor, inbuffer = get_processor_instance(format_)
    processor.process_requests(inbuffer)


if __name__ == '__main__':
    main()
