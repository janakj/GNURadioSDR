#!/usr/bin/env python2
from __future__ import print_function

import sys
import argparse

from gnuradio import gr
from gnuradio import blocks
from gnuradio import audio
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, PACKET_SIZE, CODEC2_MODE, SAMPLE_SCALE, SAMPLE_RATE


class p25_rx_udp(gr.top_block):

    def create_blocks(self):
        self.socket_pdu = blocks.socket_pdu("UDP_SERVER", '0.0.0.0', self.port, 10000, False)
        self.pdu_to_tagged_stream = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.stream_to_vector = blocks.stream_to_vector(gr.sizeof_char * 1, PACKET_SIZE)
        self.codec2_decode = vocoder.codec2_decode_ps(CODEC2_MODE)
        self.short_to_float = blocks.short_to_float(1, SAMPLE_SCALE)
        self.audio_sink = audio.sink(SAMPLE_RATE, '', True)


    def create_connections(self):
        self.msg_connect((self.socket_pdu, 'pdus'), (self.pdu_to_tagged_stream, 'pdus'))
        self.connect((self.pdu_to_tagged_stream, 0), (self.stream_to_vector, 0))
        self.connect((self.stream_to_vector, 0), (self.codec2_decode, 0))
        self.connect((self.codec2_decode, 0), (self.short_to_float, 0))
        self.connect((self.short_to_float, 0), (self.audio_sink, 0))


    def __init__(self, port):
        gr.top_block.__init__(self)
        self.port = port
        self.create_blocks()
        self.create_connections()


def main():
    #Arguments: ip address and port for UDP client
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest = 'port', default = DEFAULT_PORT, nargs = '?', help = 'port for UDP server')
    args = parser.parse_args()

    print("Listening on UDP port %s" % args.port)

    p25_rx_udp(args.port).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
