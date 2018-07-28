#!/usr/bin/env python2
from __future__ import print_function

import os
import sys
import argparse
import logging

from gnuradio import gr
from gnuradio import blocks
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, CODEC2_MODE, CODEC2_BITS_PER_FRAME, DYNAMIC_RANGE, SAMPLE_RATE


class codec2_encoder(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(self, "codec2", gr.io_signature(1, 1, gr.sizeof_float),
                                gr.io_signature(1, 1, gr.sizeof_char))

        # Scales [-1, 1] float samples to full-range short samples for CODEC2 encoder
        self.float_to_short = blocks.float_to_short(1, DYNAMIC_RANGE)

        # CODEC2 encoder produces arrays of char where each char
        # represents one bit of output. That is, an 8 byte CODEC2
        # frame will be represented with an vector of 64 chars where
        # each char will be either 0 or 1.
        self.codec2_encoder = vocoder.codec2_encode_sp(CODEC2_MODE)

        # Convert the vector of 0s and 1s coming from the CODEC2
        # encoder into a stream of bits
        self.vector_to_stream = blocks.vector_to_stream(gr.sizeof_char, CODEC2_BITS_PER_FRAME)

        # Pack the stream of bits into byte values, where each byte
        # value will contain 8-bits of input
        self.packer = blocks.unpacked_to_packed_bb(1, gr.GR_LSB_FIRST)

        # Arrange the stream of bytes into packets of 8 bytes
        self.stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 8, "packet_len")

        self.connect(self,
                     self.float_to_short,
                     self.codec2_encoder,
                     self.vector_to_stream,
                     self.packer,
                     self.stream_tagger,
                     self)


class p25_tx_udp(gr.top_block):
    def create_blocks(self):
        # Produces float samples with values within [-1, 1]
        self.wav_source = blocks.wavfile_source(self.wavfile, True)
        self.throttle = blocks.throttle(gr.sizeof_float * 1, SAMPLE_RATE, True)

        self.codec2_encoder = codec2_encoder()

        self.tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')

        self.socket_pdu = blocks.socket_pdu("UDP_CLIENT", self.ip, self.port, 10000, False)


    def create_connections(self):
        self.connect(self.wav_source,
                     self.throttle,
                     self.codec2_encoder,
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
