# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: C4FM Receiver
# Generated: Sun Aug  5 13:38:12 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from p25_c4fm_demodulator_ff import p25_c4fm_demodulator_ff  # grc-generated hier_block
from p25_fm_demodulator_cf import p25_fm_demodulator_cf  # grc-generated hier_block
from p25_symbol_mapper_fb import p25_symbol_mapper_fb  # grc-generated hier_block
import op25_repeater


class p25_c4fm_receiver_cf(gr.hier_block2):

    def __init__(self, input_rate=48000 * 20):
        gr.hier_block2.__init__(
            self, "C4FM Receiver",
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
            threshold1=-2,
            threshold2=0,
            threshold3=2.0,
            threshold4=4.0,
        )
        self.p25_fm_demodulator_cf_0 = p25_fm_demodulator_cf(
            max_deviation=2500,
            samp_rate=input_rate,
        )
        self.p25_c4fm_demodulator_ff_0 = p25_c4fm_demodulator_ff(
            input_rate=48000,
            output_rate=4800,
        )
        self.op25_frame_assembler_0 = op25_repeater.p25_frame_assembler("127.0.01", 0, True, True, True, False, gr.msg_queue(1), True, False)
        self.cutoff = filter.fir_filter_fff(input_rate // 48000, (filter.firdes.low_pass(1.0, input_rate, 3000, 300, filter.firdes.WIN_HAMMING)))
        self.cutoff.declare_sample_delay(0)
        self.baseband_amp = blocks.multiply_const_vff((6.0, ))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.baseband_amp, 0), (self.p25_c4fm_demodulator_ff_0, 0))
        self.connect((self.cutoff, 0), (self.baseband_amp, 0))
        self.connect((self.op25_frame_assembler_0, 0), (self.short_to_float, 0))
        self.connect((self.p25_c4fm_demodulator_ff_0, 0), (self.p25_symbol_mapper_fb_0, 0))
        self.connect((self.p25_fm_demodulator_cf_0, 0), (self.cutoff, 0))
        self.connect((self.p25_symbol_mapper_fb_0, 0), (self.op25_frame_assembler_0, 0))
        self.connect((self, 0), (self.p25_fm_demodulator_cf_0, 0))
        self.connect((self.short_to_float, 0), (self, 0))

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.p25_fm_demodulator_cf_0.set_samp_rate(self.input_rate)
        self.cutoff.set_taps((filter.firdes.low_pass(1.0, self.input_rate, 3000, 300, filter.firdes.WIN_HAMMING)))

    def get_fa(self):
        return self.fa

    def set_fa(self, fa):
        self.fa = fa
        self.set_fb(self.fa + 0.1 * self.fa)

    def get_fb(self):
        return self.fb

    def set_fb(self, fb):
        self.fb = fb
