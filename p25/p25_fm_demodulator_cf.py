# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM Demodulator
# Generated: Fri Aug  3 00:46:16 2018
##################################################


from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
import math


class p25_fm_demodulator_cf(gr.hier_block2):

    def __init__(self, samp_rate=48000, symbol_deviation=600.0):
        gr.hier_block2.__init__(
            self, "FM Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.samp_rate = samp_rate
        self.symbol_deviation = symbol_deviation

        ##################################################
        # Blocks
        ##################################################
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(samp_rate / (2 * math.pi * symbol_deviation))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self, 0))
        self.connect((self, 0), (self.analog_quadrature_demod_cf_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate / (2 * math.pi * self.symbol_deviation))

    def get_symbol_deviation(self):
        return self.symbol_deviation

    def set_symbol_deviation(self, symbol_deviation):
        self.symbol_deviation = symbol_deviation
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate / (2 * math.pi * self.symbol_deviation))
