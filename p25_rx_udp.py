#!/usr/bin/env python2
from __future__ import print_function

import sys
import argparse
import numpy

from gnuradio import gr
from gnuradio import blocks
from gnuradio import audio
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, IF_RATE, MTU
import op25_repeater
import p25


class p25_rx(gr.top_block):
    def __init__(self, port):
        gr.top_block.__init__(self)

        socket_pdu = blocks.socket_pdu("TCP_SERVER", '0.0.0.0', port, MTU, True)
        input = blocks.pdu_to_tagged_stream(blocks.complex_t, 'packet_len')
        self.msg_connect((socket_pdu, 'pdus'), (input, 'pdus'))

        receiver = p25.c4fm_receiver_cf(48000 * 20)

        audio_sink = audio.sink(8000, '', True)

        self.connect(
            input,
            receiver,
            audio_sink
        )


def main():
    #Arguments: ip address and port for UDP client
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest = 'port', default = DEFAULT_PORT, nargs = '?', help = 'port for UDP server')
    args = parser.parse_args()

    print("Listening on UDP port %s" % args.port)

    p25_rx(args.port).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
