# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: C4FM Demodulator
# Generated: Tue Aug  7 11:25:15 2018
##################################################

from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import op25
import p25


class p25_c4fm_demodulator_ff(gr.hier_block2):

    def __init__(self, input_rate=48000, output_rate=4800):
        gr.hier_block2.__init__(
            self, "C4FM Demodulator",
            gr.io_signature(1, 1, gr.sizeof_float*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.input_rate = input_rate
        self.output_rate = output_rate

        ##################################################
        # Variables
        ##################################################
        self.auto_tune_msgq = auto_tune_msgq = gr.msg_queue(2)

        ##################################################
        # Blocks
        ##################################################
        self.op25_fsk4_demod_ff_0 = op25.fsk4_demod_ff(self.auto_tune_msgq, input_rate, output_rate)
        self.deemphasis = filter.fir_filter_fff(1, (p25.generate_c4fm_taps(input_rate, input_rate, span=9, tx=False)))
        self.deemphasis.declare_sample_delay(0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.deemphasis, 0), (self.op25_fsk4_demod_ff_0, 0))
        self.connect((self.op25_fsk4_demod_ff_0, 0), (self, 0))
        self.connect((self, 0), (self.deemphasis, 0))

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.deemphasis.set_taps((p25.generate_c4fm_taps(self.input_rate, self.input_rate, span=9, tx=False)))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate

    def get_auto_tune_msgq(self):
        return self.auto_tune_msgq

    def set_auto_tune_msgq(self, auto_tune_msgq):
        self.auto_tune_msgq = auto_tune_msgq
