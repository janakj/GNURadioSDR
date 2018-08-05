# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM Demodulator
# Generated: Sun Aug  5 13:38:23 2018
##################################################

from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
import math


class p25_fm_demodulator_cf(gr.hier_block2):

    def __init__(self, max_deviation=2500, samp_rate=48000 * 20):
        gr.hier_block2.__init__(
            self, "FM Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.max_deviation = max_deviation
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(samp_rate / (2 * math.pi * max_deviation))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self, 0))
        self.connect((self, 0), (self.analog_quadrature_demod_cf_0, 0))

    def get_max_deviation(self):
        return self.max_deviation

    def set_max_deviation(self, max_deviation):
        self.max_deviation = max_deviation
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate / (2 * math.pi * self.max_deviation))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate / (2 * math.pi * self.max_deviation))
