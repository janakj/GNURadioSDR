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


from p25_config import DEFAULT_PORT, CODEC2_MODE, CODEC2_BITS_PER_FRAME, DYNAMIC_RANGE, SAMPLE_RATE, MTU
import op25_c4fm_mod
import op25_repeater



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

        self.connect(self,
                     self.float_to_short,
                     self.codec2_encoder,
                     self.vector_to_stream,
                     self.packer,
                     self)


class p25_tx_udp(gr.top_block):
    def create_blocks(self):

        # Produces float samples with values within [-1, 1]
        self.wav_source = blocks.wavfile_source(self.wavfile, True)
        self.throttle = blocks.throttle(gr.sizeof_float * 1, SAMPLE_RATE, True)
        # Scales [-1, 1] float samples to full-range short samples for CODEC2 encoder
        self.float_to_short = blocks.float_to_short(1, DYNAMIC_RANGE)

        # The encoder expects a stream of shorts with rate 8000
        # samples per seconds on input. It generates a stream of
        # symbols (chars) at 4800 samples per second.
        self.encoder = op25_repeater.vocoder(
            True,    # 0=Decode,True=Encode
            False,   # Verbose flag
            0,	     # flex amount
            "",      # udp ip address
            0,	     # udp port
            False)   # dump raw u vectors

        audio_rate = 48000
        if_rate = 48000

        self.c4fm_mod = op25_c4fm_mod.p25_mod_bf(output_sample_rate=audio_rate)

        interp_factor = if_rate / audio_rate
        low_pass = 2.88e3
        interp_taps = filter.firdes.low_pass(1.0, if_rate, low_pass, low_pass * 0.1, filter.firdes.WIN_HANN)
        interpolator = filter.interp_fir_filter_fff (int(interp_factor), interp_taps)

        max_dev = 12.5e3
        k = 2 * math.pi * max_dev / if_rate
        adjustment = 1.5   # adjust for proper c4fm deviation level
        self.fm_mod = analog.frequency_modulator_fc(k * adjustment)

        # Convert a fixed number of symbols into a PDU and transmit
        # the PDU to the receiver via UDP.
        self.stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, MTU / gr.sizeof_gr_complex, "packet_len")
        self.tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len')
        self.socket_pdu = blocks.socket_pdu("UDP_CLIENT", self.ip, self.port, MTU, True)


    def create_connections(self):
        self.connect(self.wav_source,
                     #self.throttle,
                     self.float_to_short,
                     self.encoder,
                     self.c4fm_mod,
                     self.fm_mod,
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
