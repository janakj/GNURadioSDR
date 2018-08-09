#!/usr/bin/env python2
from __future__ import print_function

import os
import sys
import site
import math
import argparse
import logging

from gnuradio import gr
from gnuradio import blocks
from gnuradio import vocoder
from gnuradio import filter
from gnuradio import analog
from gnuradio import digital

from p25_config import DEFAULT_PORT, IF_RATE, MTU
import p25
import op25_repeater


class p25_tx(gr.top_block):

    def __init__(self, ip, port, wavfile):
        gr.top_block.__init__(self)
        self.ip = ip
        self.port = port

        # Produces float samples with values within [-1, 1]
        wav_source = blocks.wavfile_source(wavfile, True)
        throttle = blocks.throttle(gr.sizeof_float * 1, 8000 *4, True)

        trx = p25.c4fm_transmitter_fc(48000 * 20)

        # Convert a fixed number of symbols into a PDU and transmit
        # the PDU to the receiver via UDP.
        stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, MTU / gr.sizeof_gr_complex, "packet_len")
        tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len')
        socket_pdu = blocks.socket_pdu("TCP_CLIENT", ip, port, MTU, True)
        self.msg_connect((tagged_stream_to_pdu, 'pdus'), (socket_pdu, 'pdus'))

        self.connect(
            wav_source,
            throttle,
            trx
        )

        self.connect(
            trx,
            stream_tagger,
            tagged_stream_to_pdu
        )




def main():
    #Arguments: ip address and port for UDP client
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest = 'ip', default = '127.0.0.1', nargs = '?', help = 'Receiver IP address')
    parser.add_argument('-p', dest = 'port', default = DEFAULT_PORT, nargs = '?', help = 'Receiver UDP port')
    parser.add_argument('-f', dest='wavfile', default='%s/Downloads/sentence2.wav' % os.environ['HOME'], nargs='?', help='WAV file')
    args = parser.parse_args()

    print("Transmitting file %s" % args.wavfile)
    print("Streaming to udp:%s:%s" % (args.ip, args.port))

    p25_tx(args.ip, args.port, args.wavfile).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
