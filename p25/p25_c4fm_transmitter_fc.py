# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: C4FM Transmitter
# Generated: Tue Aug  7 14:18:53 2018
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from p25_c4fm_modulator_ff import p25_c4fm_modulator_ff  # grc-generated hier_block
from p25_fm_modulator_fc import p25_fm_modulator_fc  # grc-generated hier_block
from p25_symbol_mapper_bf import p25_symbol_mapper_bf  # grc-generated hier_block
import op25_repeater


class p25_c4fm_transmitter_fc(gr.hier_block2):

    def __init__(self, output_rate=48000 * 150):
        gr.hier_block2.__init__(
            self, "C4FM Transmitter",
            gr.io_signature(1, 1, gr.sizeof_float*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.output_rate = output_rate

        ##################################################
        # Variables
        ##################################################
        self.if_rate = if_rate = 48000

        self.taps = taps = firdes.low_pass(output_rate // if_rate, output_rate, 6250, 100, firdes.WIN_HANN, 6.76)


        ##################################################
        # Blocks
        ##################################################
        self.symbol_mapper = p25_symbol_mapper_bf(
            symbol00=1.0/3.0,
            symbol01=1.0,
            symbol10=-1.0/3.0,
            symbol11=-1.0,
        )
        self.p25_c4fm_modulator_ff_0 = p25_c4fm_modulator_ff(
            input_rate=4800,
            output_rate=if_rate,
            gain=6.0,
        )
        self.op25_vocoder_0 = op25_repeater.vocoder(True, False, 0, "", 0, False)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf(output_rate // if_rate, (taps))
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.fm_mod = p25_fm_modulator_fc(
            factor=1.0,
            max_deviation=2.5e3,
            samp_rate=if_rate,
        )
        self.float_to_short = blocks.float_to_short(1, 32768)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.float_to_short, 0), (self.op25_vocoder_0, 0))
        self.connect((self.fm_mod, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self, 0))
        self.connect((self.op25_vocoder_0, 0), (self.symbol_mapper, 0))
        self.connect((self.p25_c4fm_modulator_ff_0, 0), (self.fm_mod, 0))
        self.connect((self, 0), (self.float_to_short, 0))
        self.connect((self.symbol_mapper, 0), (self.p25_c4fm_modulator_ff_0, 0))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate
        self.p25_c4fm_modulator_ff_0.set_output_rate(self.if_rate)
        self.fm_mod.set_samp_rate(self.if_rate)

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.interp_fir_filter_xxx_0.set_taps((self.taps))
