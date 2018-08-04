# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: CQPSK Demodulator
# Generated: Sat Aug  4 16:52:29 2018
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
import math
import op25_repeater


class p25_cqpsk_demodulator_cf(gr.hier_block2):

    def __init__(self, costas_alpha=0.04, gain_mu=0.025, input_rate=48000, output_rate=4800):
        gr.hier_block2.__init__(
            self, "CQPSK Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.costas_alpha = costas_alpha
        self.gain_mu = gain_mu
        self.input_rate = input_rate
        self.output_rate = output_rate

        ##################################################
        # Variables
        ##################################################
        self.alpha = alpha = costas_alpha
        self.omega = omega = float(input_rate) / float(output_rate)
        self.gain_omega = gain_omega = 0.1 * gain_mu * gain_mu
        self.fmax = fmax = 2 * math.pi * 2400 / float(input_rate)
        self.beta = beta = 0.125 * alpha * alpha

        ##################################################
        # Blocks
        ##################################################
        self.to_float = blocks.complex_to_arg(1)
        self.rescale = blocks.multiply_const_vff((1 / (math.pi / 4), ))
        self.diffdec = digital.diff_phasor_cc()
        self.clock = op25_repeater.gardner_costas_cc(omega, gain_mu, gain_omega, alpha, beta, fmax, -fmax)
        self.agc = analog.feedforward_agc_cc(16, 1.0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.agc, 0), (self.clock, 0))
        self.connect((self.clock, 0), (self.diffdec, 0))
        self.connect((self.diffdec, 0), (self.to_float, 0))
        self.connect((self, 0), (self.agc, 0))
        self.connect((self.rescale, 0), (self, 0))
        self.connect((self.to_float, 0), (self.rescale, 0))

    def get_costas_alpha(self):
        return self.costas_alpha

    def set_costas_alpha(self, costas_alpha):
        self.costas_alpha = costas_alpha
        self.set_alpha(self.costas_alpha)

    def get_gain_mu(self):
        return self.gain_mu

    def set_gain_mu(self, gain_mu):
        self.gain_mu = gain_mu
        self.set_gain_omega(0.1 * self.gain_mu * self.gain_mu)

    def get_input_rate(self):
        return self.input_rate

    def set_input_rate(self, input_rate):
        self.input_rate = input_rate
        self.set_omega(float(self.input_rate) / float(self.output_rate))
        self.set_fmax(2 * math.pi * 2400 / float(self.input_rate))

    def get_output_rate(self):
        return self.output_rate

    def set_output_rate(self, output_rate):
        self.output_rate = output_rate
        self.set_omega(float(self.input_rate) / float(self.output_rate))

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.set_beta(0.125 * self.alpha * self.alpha)

    def get_omega(self):
        return self.omega

    def set_omega(self, omega):
        self.omega = omega

    def get_gain_omega(self):
        return self.gain_omega

    def set_gain_omega(self, gain_omega):
        self.gain_omega = gain_omega

    def get_fmax(self):
        return self.fmax

    def set_fmax(self, fmax):
        self.fmax = fmax

    def get_beta(self):
        return self.beta

    def set_beta(self, beta):
        self.beta = beta
