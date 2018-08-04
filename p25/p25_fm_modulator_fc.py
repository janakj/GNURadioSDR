# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM Modulator
# Generated: Sat Aug  4 18:30:01 2018
##################################################

from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
import math


class p25_fm_modulator_fc(gr.hier_block2):

    def __init__(self, factor=1.5, max_deviation=12.5e3, samp_rate=48000):
        gr.hier_block2.__init__(
            self, "FM Modulator",
            gr.io_signature(1, 1, gr.sizeof_float*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.factor = factor
        self.max_deviation = max_deviation
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(factor * 2 * math.pi * max_deviation / samp_rate)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self, 0))
        self.connect((self, 0), (self.analog_frequency_modulator_fc_0, 0))

    def get_factor(self):
        return self.factor

    def set_factor(self, factor):
        self.factor = factor
        self.analog_frequency_modulator_fc_0.set_sensitivity(self.factor * 2 * math.pi * self.max_deviation / self.samp_rate)

    def get_max_deviation(self):
        return self.max_deviation

    def set_max_deviation(self, max_deviation):
        self.max_deviation = max_deviation
        self.analog_frequency_modulator_fc_0.set_sensitivity(self.factor * 2 * math.pi * self.max_deviation / self.samp_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_frequency_modulator_fc_0.set_sensitivity(self.factor * 2 * math.pi * self.max_deviation / self.samp_rate)
