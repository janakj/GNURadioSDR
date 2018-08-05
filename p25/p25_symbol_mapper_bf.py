# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Symbol Mapper
# Generated: Sun Aug  5 13:38:28 2018
##################################################

from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes


class p25_symbol_mapper_bf(gr.hier_block2):

    def __init__(self, symbol00=1.0/3.0, symbol01=1.0, symbol10=-1.0/3.0, symbol11=-1.0):
        gr.hier_block2.__init__(
            self, "Symbol Mapper",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.symbol00 = symbol00
        self.symbol01 = symbol01
        self.symbol10 = symbol10
        self.symbol11 = symbol11

        ##################################################
        # Blocks
        ##################################################
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bf(((symbol00, symbol01, symbol10, symbol11)), 1)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self, 0))
        self.connect((self, 0), (self.digital_chunks_to_symbols_xx_0, 0))

    def get_symbol00(self):
        return self.symbol00

    def set_symbol00(self, symbol00):
        self.symbol00 = symbol00
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(((self.symbol00, self.symbol01, self.symbol10, self.symbol11)))

    def get_symbol01(self):
        return self.symbol01

    def set_symbol01(self, symbol01):
        self.symbol01 = symbol01
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(((self.symbol00, self.symbol01, self.symbol10, self.symbol11)))

    def get_symbol10(self):
        return self.symbol10

    def set_symbol10(self, symbol10):
        self.symbol10 = symbol10
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(((self.symbol00, self.symbol01, self.symbol10, self.symbol11)))

    def get_symbol11(self):
        return self.symbol11

    def set_symbol11(self, symbol11):
        self.symbol11 = symbol11
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(((self.symbol00, self.symbol01, self.symbol10, self.symbol11)))
