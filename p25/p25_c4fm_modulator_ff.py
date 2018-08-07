# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: C4FM Modulator
# Generated: Tue Aug  7 14:18:28 2018
##################################################

from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import p25


class p25_c4fm_modulator_ff(gr.hier_block2):

    def __init__(self, input_rate=4800, output_rate=48000, gain=6.0):
        gr.hier_block2.__init__(
            self, "C4FM Modulator",
            gr.io_signature(1, 1, gr.sizeof_float*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.input_rate = input_rate
        self.output_rate = output_rate
        self.gain = gain

        ##################################################
        # Blocks
        ##################################################
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_fff(output_rate / input_rate, (p25.generate_c4fm_taps(input_rate, output_rate, filter_gain=gain, tx=True)))
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.interp_fir_filter_xxx_0, 0), (self, 0))
        self.connect((self, 0), (self.interp_fir_filter_xxx_0, 0))

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.interp_fir_filter_xxx_0.set_taps((p25.generate_c4fm_taps(self.input_rate, self.output_rate, filter_gain=self.gain, tx=True)))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate
        self.interp_fir_filter_xxx_0.set_taps((p25.generate_c4fm_taps(self.input_rate, self.output_rate, filter_gain=self.gain, tx=True)))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.interp_fir_filter_xxx_0.set_taps((p25.generate_c4fm_taps(self.input_rate, self.output_rate, filter_gain=self.gain, tx=True)))
