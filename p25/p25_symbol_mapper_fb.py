# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Symbol Demapper
# Generated: Fri Aug  3 00:35:26 2018
##################################################


from gnuradio import gr
from gnuradio.filter import firdes
import op25_repeater


class p25_symbol_mapper_fb(gr.hier_block2):

    def __init__(self, threshold1=-2, threshold2=0, threshold3=2.0, threshold4=4.0):
        gr.hier_block2.__init__(
            self, "Symbol Demapper",
            gr.io_signature(1, 1, gr.sizeof_float*1),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.threshold3 = threshold3
        self.threshold4 = threshold4

        ##################################################
        # Blocks
        ##################################################
        self.op25_fsk4_slicer_fb_0 = op25_repeater.fsk4_slicer_fb([-2.0, 0.0, 2.0, 4.0])

        ##################################################
        # Connections
        ##################################################
        self.connect((self.op25_fsk4_slicer_fb_0, 0), (self, 0))
        self.connect((self, 0), (self.op25_fsk4_slicer_fb_0, 0))

    def get_threshold1(self):
        return self.threshold1

    def set_threshold1(self, threshold1):
        self.threshold1 = threshold1

    def get_threshold2(self):
        return self.threshold2

    def set_threshold2(self, threshold2):
        self.threshold2 = threshold2

    def get_threshold3(self):
        return self.threshold3

    def set_threshold3(self, threshold3):
        self.threshold3 = threshold3

    def get_threshold4(self):
        return self.threshold4

    def set_threshold4(self, threshold4):
        self.threshold4 = threshold4
