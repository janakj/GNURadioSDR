# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: C4FM Transmitter
# Generated: Fri Aug  3 00:33:55 2018
##################################################


import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import pfb
from p25_c4fm_modulator_ff import p25_c4fm_modulator_ff  # grc-generated hier_block
from p25_fm_modulator_fc import p25_fm_modulator_fc  # grc-generated hier_block
from p25_symbol_mapper_bf import p25_symbol_mapper_bf  # grc-generated hier_block
import op25_repeater


class p25_c4fm_transmitter_fc(gr.hier_block2):

    def __init__(self, output_rate=48000):
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
        self.cutoff = cutoff = 2880

        ##################################################
        # Blocks
        ##################################################
        self.symbol_mapper = p25_symbol_mapper_bf(
            symbol00=1.0/3.0,
            symbol01=1.0,
            symbol10=-1.0/3.0,
            symbol11=-1.0,
        )
        self.resampler = pfb.arb_resampler_ccf(
        	  float(output_rate) / 48000,
                  taps=None,
        	  flt_size=32)
        self.resampler.declare_sample_delay(0)

        self.p25_c4fm_modulator_ff_0 = p25_c4fm_modulator_ff(
            input_rate=4800,
            output_rate=48000,
        )
        self.op25_vocoder_0 = op25_repeater.vocoder(True, False, 0, "", 0, False)
        self.interpolator = filter.interp_fir_filter_fff(1, (filter.firdes.low_pass(1.0, 48000, cutoff, cutoff * 0.1, filter.firdes.WIN_HANN)))
        self.interpolator.declare_sample_delay(0)
        self.fm_mod = p25_fm_modulator_fc(
            factor=1.5,
            max_deviation=12.5e3,
            samp_rate=48000,
        )
        self.float_to_short = blocks.float_to_short(1, 32768)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.float_to_short, 0), (self.op25_vocoder_0, 0))
        self.connect((self.fm_mod, 0), (self.resampler, 0))
        self.connect((self.interpolator, 0), (self.fm_mod, 0))
        self.connect((self.op25_vocoder_0, 0), (self.symbol_mapper, 0))
        self.connect((self.p25_c4fm_modulator_ff_0, 0), (self.interpolator, 0))
        self.connect((self, 0), (self.float_to_short, 0))
        self.connect((self.resampler, 0), (self, 0))
        self.connect((self.symbol_mapper, 0), (self.p25_c4fm_modulator_ff_0, 0))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate
        self.resampler.set_rate(float(self.output_rate) / 48000)

    def get_cutoff(self):
        return self.cutoff

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
        self.interpolator.set_taps((filter.firdes.low_pass(1.0, 48000, self.cutoff, self.cutoff * 0.1, filter.firdes.WIN_HANN)))
