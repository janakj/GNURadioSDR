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
#import osmosdr

from p25_config import DEFAULT_PORT, CODEC2_MODE, CODEC2_BITS_PER_FRAME, SAMPLE_RATE, MTU, FREQUENCY
import p25
import op25_repeater



class codec2_encoder(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(self, "codec2", gr.io_signature(1, 1, gr.sizeof_float),
                                gr.io_signature(1, 1, gr.sizeof_char))

        # Scales [-1, 1] float samples to full-range short samples for CODEC2 encoder
        float_to_short = blocks.float_to_short(1, 32768)

        # CODEC2 encoder produces arrays of char where each char
        # represents one bit of output. That is, an 8 byte CODEC2
        # frame will be represented with an vector of 64 chars where
        # each char will be either 0 or 1.
        codec2_encoder = vocoder.codec2_encode_sp(CODEC2_MODE)

        # Convert the vector of 0s and 1s coming from the CODEC2
        # encoder into a stream of bits
        vector_to_stream = blocks.vector_to_stream(gr.sizeof_char, CODEC2_BITS_PER_FRAME)

        # Pack the stream of bits into byte values, where each byte
        # value will contain 8-bits of input
        packer = blocks.unpacked_to_packed_bb(1, gr.GR_LSB_FIRST)

        self.connect(
            self,
            float_to_short,
            codec2_encoder,
            vector_to_stream,
            packer,
            self
        )


class p25_tx(gr.top_block):

    def setup_sdr(self, sample_rate):
        self.lime = osmosdr.sink( args="numchan=1 driver=lime,soapy=0")
        print("Sample rate: min=%d, max=%d S/s" % (self.lime.get_sample_rates().start(), self.lime.get_sample_rates().stop()))
        self.lime.set_sample_rate(sample_rate)

        # Automatically select radio frontend bandpass bandwidth
        self.lime.set_bandwidth(0, 0)

        print("Frequency: min=%d, max=%d Hz" % (self.lime.get_freq_range().start(), self.lime.get_freq_range().stop()))
        print("Transmitting on %d Hz" % FREQUENCY);
        self.lime.set_center_freq(FREQUENCY)

        self.lime.set_gain(10)
        self.lime.set_if_gain(20)
        self.lime.set_bb_gain(20)

        print("Antennas: %s" % repr(self.lime.get_antennas()))
        self.lime.set_antenna('BAND1')


    def __init__(self, ip, port, wavfile):
        gr.top_block.__init__(self)
        self.ip = ip
        self.port = port

        # Produces float samples with values within [-1, 1]
        wav_source = blocks.wavfile_source(wavfile, True)
        throttle = blocks.throttle(gr.sizeof_float * 1, SAMPLE_RATE * 2, True)

        trx = p25.c4fm_transmitter_fc(48000)

        # Convert a fixed number of symbols into a PDU and transmit
        # the PDU to the receiver via UDP.
        stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, MTU / gr.sizeof_gr_complex, "packet_len")
        tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len')
        socket_pdu = blocks.socket_pdu("UDP_CLIENT", ip, port, MTU, True)
        self.msg_connect((tagged_stream_to_pdu, 'pdus'), (socket_pdu, 'pdus'))

        self.connect(
            wav_source,
            throttle,
            trx
        )

        #self.setup_sdr(self.if_rate)
        #self.connect(self.fm_mod, self.lime)

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
