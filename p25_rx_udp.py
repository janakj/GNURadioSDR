#!/usr/bin/env python2
from __future__ import print_function

import sys
import argparse
import numpy

from gnuradio import gr
from gnuradio import blocks
from gnuradio import audio
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, CODEC2_MODE, CODEC2_BITS_PER_FRAME, SAMPLE_RATE, MTU
import op25_repeater
import p25


class codec2_decoder(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(self, "codec2", gr.io_signature(1, 1, gr.sizeof_char),
                                gr.io_signature(1, 1, gr.sizeof_float))

        # Unpack the 8 bytes (one codec2 frame) into a stream of bits
        unpacker = blocks.packed_to_unpacked_bb(1, gr.GR_LSB_FIRST)

        # Convert the stream of bits into a vector of bits, which is
        # what the CODEC2 encoder expects, and decode the frame.
        stream_to_vector = blocks.stream_to_vector(gr.sizeof_char, CODEC2_BITS_PER_FRAME)
        codec2_decode = vocoder.codec2_decode_ps(CODEC2_MODE)

        # Scale the dynamic range of the stream back to [-1, 1] and
        # feed it to the soundcard.
        short_to_float = blocks.short_to_float(1, 32768)

        self.connect(self,
                     unpacker,
                     stream_to_vector,
                     codec2_decode,
                     short_to_float,
                     self)


class p25_rx(gr.top_block):
    def __init__(self, port):
        gr.top_block.__init__(self)

        socket_pdu = blocks.socket_pdu("UDP_SERVER", '0.0.0.0', port, MTU, True)
        input = blocks.pdu_to_tagged_stream(blocks.complex_t, 'packet_len')
        self.msg_connect((socket_pdu, 'pdus'), (input, 'pdus'))

        receiver = p25.c4fm_receiver_cf()

        audio_sink = audio.sink(SAMPLE_RATE, '', True)

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
