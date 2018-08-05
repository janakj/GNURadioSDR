# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: CQPSK Receiver
# Generated: Sun Aug  5 13:38:20 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from p25_arb_resampler_cc import p25_arb_resampler_cc  # grc-generated hier_block
from p25_cqpsk_demodulator_cf import p25_cqpsk_demodulator_cf  # grc-generated hier_block
from p25_symbol_mapper_fb import p25_symbol_mapper_fb  # grc-generated hier_block
import op25_repeater


class p25_cqpsk_receiver_cf(gr.hier_block2):

    def __init__(self, input_rate=48000):
        gr.hier_block2.__init__(
            self, "CQPSK Receiver",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.input_rate = input_rate

        ##################################################
        # Variables
        ##################################################
        self.fa = fa = 6250
        self.fb = fb = fa + 0.1 * fa

        ##################################################
        # Blocks
        ##################################################
        self.short_to_float = blocks.short_to_float(1, 32768)
        self.p25_symbol_mapper_fb_0 = p25_symbol_mapper_fb(
            threshold1=-2.0,
            threshold2=0.0,
            threshold3=2.0,
            threshold4=4.0,
        )
        self.p25_cqpsk_demodulator_cf_0 = p25_cqpsk_demodulator_cf(
            costas_alpha=0.04,
            gain_mu=0.025,
            input_rate=48000,
            output_rate=4800,
        )
        self.op25_frame_assembler_0 = op25_repeater.p25_frame_assembler("127.0.01", 0, True, True, True, False, gr.msg_queue(1), True, False)
        self.cutoff = filter.fir_filter_ccc(1, (filter.firdes.low_pass(1.0, 48000, (fa + fb) / 2, fb - fa, filter.firdes.WIN_HANN)))
        self.cutoff.declare_sample_delay(0)
        self.arb_resampler = p25_arb_resampler_cc(
            input_rate=input_rate,
            output_rate=48000,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.arb_resampler, 0), (self.cutoff, 0))
        self.connect((self.cutoff, 0), (self.p25_cqpsk_demodulator_cf_0, 0))
        self.connect((self.op25_frame_assembler_0, 0), (self.short_to_float, 0))
        self.connect((self.p25_cqpsk_demodulator_cf_0, 0), (self.p25_symbol_mapper_fb_0, 0))
        self.connect((self.p25_symbol_mapper_fb_0, 0), (self.op25_frame_assembler_0, 0))
        self.connect((self, 0), (self.arb_resampler, 0))
        self.connect((self.short_to_float, 0), (self, 0))

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.arb_resampler.set_input_rate(self.input_rate)

    def get_fa(self):
        return self.fa

    def set_fa(self, fa):
        self.fa = fa
        self.set_fb(self.fa + 0.1 * self.fa)
        self.cutoff.set_taps((filter.firdes.low_pass(1.0, 48000, (self.fa + self.fb) / 2, self.fb - self.fa, filter.firdes.WIN_HANN)))

    def get_fb(self):
        return self.fb

    def set_fb(self, fb):
        self.fb = fb
        self.cutoff.set_taps((filter.firdes.low_pass(1.0, 48000, (self.fa + self.fb) / 2, self.fb - self.fa, filter.firdes.WIN_HANN)))
