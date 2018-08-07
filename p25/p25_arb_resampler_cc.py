# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Arbitrary Resampler
# Generated: Sat Aug  4 01:48:22 2018
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import pfb


class p25_arb_resampler_cc(gr.hier_block2):

    def __init__(self, input_rate=48000, output_rate=48000):
        gr.hier_block2.__init__(
            self, "Arbitrary Resampler",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.input_rate = input_rate
        self.output_rate = output_rate

        ##################################################
        # Variables
        ##################################################
        self.decimation = decimation = int(input_rate / output_rate)
        self.resampled_rate = resampled_rate = float(input_rate) / float(decimation)
        self.rel_freq = rel_freq = 0

        ##################################################
        # Blocks
        ##################################################
        self.osc = analog.sig_source_c(input_rate, analog.GR_SIN_WAVE, rel_freq, 1, 0)
        self.mixer = blocks.multiply_vcc(1)
        self.lpf = filter.fir_filter_ccf(decimation, (filter.firdes.low_pass(1.0, input_rate, 7250, 725, filter.firdes.WIN_HANN)))
        self.lpf.declare_sample_delay(0)
        self.arb_resampler = pfb.arb_resampler_ccf(
        	  float(output_rate) / resampled_rate,
                  taps=None,
        	  flt_size=32)
        self.arb_resampler.declare_sample_delay(0)




        ##################################################
        # Connections
        ##################################################
        self.connect((self.arb_resampler, 0), (self, 0))
        self.connect((self.lpf, 0), (self.arb_resampler, 0))
        self.connect((self.mixer, 0), (self.lpf, 0))
        self.connect((self.osc, 0), (self.mixer, 1))
        self.connect((self, 0), (self.mixer, 0))

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.set_resampled_rate(float(self.input_rate) / float(self.decimation))
        self.set_decimation(int(self.input_rate / self.output_rate))
        self.osc.set_sampling_freq(self.input_rate)
        self.lpf.set_taps((filter.firdes.low_pass(1.0, self.input_rate, 7250, 725, filter.firdes.WIN_HANN)))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate
        self.set_decimation(int(self.input_rate / self.output_rate))
        self.arb_resampler.set_rate(float(self.output_rate) / self.resampled_rate)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_resampled_rate(float(self.input_rate) / float(self.decimation))

    def get_resampled_rate(self):
        return self.resampled_rate

    def set_resampled_rate(self, resampled_rate):
        self.resampled_rate = resampled_rate
        self.arb_resampler.set_rate(float(self.output_rate) / self.resampled_rate)

    def get_rel_freq(self):
        return self.rel_freq

    def set_rel_freq(self, rel_freq):
        self.rel_freq = rel_freq
        self.osc.set_frequency(self.rel_freq)
