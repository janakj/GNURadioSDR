#!/usr/bin/env python2
from __future__ import print_function

import sys
import argparse
import numpy

from gnuradio import gr
from gnuradio import blocks
from gnuradio import audio
from gnuradio import vocoder

from p25_config import DEFAULT_PORT, CODEC2_MODE, CODEC2_BITS_PER_FRAME, DYNAMIC_RANGE, SAMPLE_RATE, MTU
import op25_repeater
import op25
import p25_demodulator


class codec2_decoder(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(self, "codec2", gr.io_signature(1, 1, gr.sizeof_char),
                                gr.io_signature(1, 1, gr.sizeof_float))

        # Unpack the 8 bytes (one codec2 frame) into a stream of bits
        self.unpacker = blocks.packed_to_unpacked_bb(1, gr.GR_LSB_FIRST)

        # Convert the stream of bits into a vector of bits, which is
        # what the CODEC2 encoder expects, and decode the frame.
        self.stream_to_vector = blocks.stream_to_vector(gr.sizeof_char, CODEC2_BITS_PER_FRAME)
        self.codec2_decode = vocoder.codec2_decode_ps(CODEC2_MODE)

        # Scale the dynamic range of the stream back to [-1, 1] and
        # feed it to the soundcard.
        self.short_to_float = blocks.short_to_float(1, DYNAMIC_RANGE)

        self.connect(self,
                     self.unpacker,
                     self.stream_to_vector,
                     self.codec2_decode,
                     self.short_to_float,
                     self)


class p25_rx_udp(gr.top_block):

    def create_blocks(self):
        self.socket_pdu = blocks.socket_pdu("UDP_SERVER", '0.0.0.0', self.port, MTU, True)
        self.pdu_to_tagged_stream = blocks.pdu_to_tagged_stream(blocks.complex_t, 'packet_len')

        self.c4fm_demod = p25_demodulator.p25_demod_cb(48000, demod_type='fsk4')

        self.decoder = op25_repeater.p25_frame_assembler(
            "127.0.0.1",  # Wireshark host
            0,            # Wireshark port
            True,         # debug
            True,         # do_imbe
            True,         # do_output
            False,        # do_msgq
            self.msgq,    # msgq
            True,         # do_audio_output
            False)        # do_phase2_tdma

        # Scale the dynamic range of the stream back to [-1, 1] and
        # feed it to the soundcard.
        self.short_to_float = blocks.short_to_float(1, DYNAMIC_RANGE)
        self.audio_sink = audio.sink(SAMPLE_RATE, '', True)


    def create_connections(self):
        self.msg_connect((self.socket_pdu, 'pdus'), (self.pdu_to_tagged_stream, 'pdus'))
        self.connect(self.pdu_to_tagged_stream,
                     self.c4fm_demod,
                     self.decoder,
                     self.short_to_float,
                     self.audio_sink)


    def __init__(self, port):
        gr.top_block.__init__(self)
        self.msgq = gr.msg_queue(1)
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
