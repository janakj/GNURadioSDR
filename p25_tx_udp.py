#!/usr/bin/env python2
from __future__ import print_function

import os
import sys
import argparse
import logging

from gnuradio import gr
from gnuradio import blocks
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, PACKET_SIZE, CODEC2_MODE, SAMPLE_SCALE, SAMPLE_RATE


class p25_tx_udp(gr.top_block):
    def create_blocks(self):
        self.wav_source = blocks.wavfile_source(self.wavfile, True)
        self.throttle = blocks.throttle(gr.sizeof_float * 1, SAMPLE_RATE, True)
        self.float_to_short = blocks.float_to_short(1, SAMPLE_SCALE)
        self.codec2_encode = vocoder.codec2_encode_sp(CODEC2_MODE)
        self.vector_to_stream = blocks.vector_to_stream(gr.sizeof_char * 1, PACKET_SIZE)
        self.stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 64, "packet_len")
        self.tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.socket_pdu = blocks.socket_pdu("UDP_CLIENT", self.ip, self.port, 10000, False)


    def create_connections(self):
        self.connect(self.wav_source,
                     self.throttle,
                     self.float_to_short,
                     self.codec2_encode,
                     self.vector_to_stream,
                     self.stream_tagger,
                     self.tagged_stream_to_pdu)
        self.msg_connect((self.tagged_stream_to_pdu, 'pdus'), (self.socket_pdu, 'pdus'))


    def __init__(self, ip, port, wavfile):
        gr.top_block.__init__(self)
        self.ip = ip
        self.port = port
        self.wavfile = wavfile

        self.create_blocks()
        self.create_connections()



def main():
    #Arguments: ip address and port for UDP client
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest = 'ip', default = '127.0.0.1', nargs = '?', help = 'Receiver IP address')
    parser.add_argument('-p', dest = 'port', default = DEFAULT_PORT, nargs = '?', help = 'Receiver UDP port')
    parser.add_argument('-f', dest='wavfile', default='%s/Downloads/sentence2.wav' % os.environ['HOME'], nargs='?', help='WAV file')
    args = parser.parse_args()

    print("Transmitting file %s" % args.wavfile)
    print("Streaming to udp:%s:%s" % (args.ip, args.port))

    p25_tx_udp(args.ip, args.port, args.wavfile).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
