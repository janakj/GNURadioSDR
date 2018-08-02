# -*- coding: utf-8 -*-
#
# Copyright 2005,2006,2007 Free Software Foundation, Inc.
#
# OP25 4-Level Modulator Block
# Copyright 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Max H. Parke KA1RBI
#
# GMSK code from gnuradio gr-digital/python/digital/gmsk.py
# gmsk.py is Copyright 2005-2007,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio and part of OP25
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import math
from   math import sin, cos, pi
import numpy as np

from gnuradio import gr, gru, analog
from gnuradio import filter, digital, blocks

import op25           # fsk4_demod
import op25_repeater  # fsk4_slicer, gardner_costas


__all__ = [
    'fm_modulator_fc',
    'fm_demodulator_cf',
    'arb_resampler_cc',
    'c4fm_modulator_bf',
    'c4fm_demodulator_ff',
    'cqpsk_demodulator_cf',
    'c4fm_transmitter_fc',
    'c4fm_receiver_cf']

SYMBOL_RATE = 4800
IF_RATE = 48000


def fm_modulator_fc(rate=IF_RATE, max_deviation=12.5e3, c=1.0):
    '''FM Modulator block for P-25.

    The modulator expects an audio signal (stream of floats) on its
    input and produces a complex baseband signal on the output. The
    output signal can be mixed with a local oscilator, or directly
    passed to SDR hardware sink.

    The modulator should map P-25 symbols to deviations as follows:
    +1 ->   600 Hz
    +3 ->  1800 Hz
    -1 ->  -600 Hz
    -3 -> -1800 Hz
    '''

    k = 2 * math.pi * max_deviation / rate
    sensitivity = c * k # adjust for proper c4fm deviation level
    return analog.frequency_modulator_fc(sensitivity)


def fm_demodulator_cf(rate=IF_RATE, symbol_deviation=600.0):
    gain = rate / (2.0 * pi * symbol_deviation)
    return analog.quadrature_demod_cf(gain)


def symbol_mapper_bf(symbol00=1.0/3.0, symbol01=1.0, symbol10=-1.0/3.0, symbol11=-1.0):
    '''Map di-bits (values from 0 to 3) to float values.
    Map integer symbols to normalized float values:
    00 -> +1 -> 1/3
    01 -> +3 -> 1
    10 -> -1 -> -1/3
    11 -> -3 -> -1
    '''
    return digital.chunks_to_symbols_bf([symbol00, symbol01, symbol10, symbol11])


def symbol_mapper_fb(threshold1=-2.0, threshold2=0.0, threshold3=2.0, threshold4=4.0):
    return op25_repeater.fsk4_slicer_fb([threshold1, threshold2, threshold3, threshold4])


def transfer_function_rx():
    # p25 c4fm de-emphasis filter
    # Specs undefined above 2,880 Hz.  It would be nice to have a sharper
    # rolloff, but this filter is cheap enough....
    xfer = []	# frequency domain transfer function
    for f in xrange(0, SYMBOL_RATE):
        # D(f)
	t = pi * f / SYMBOL_RATE
	if t < 1e-6:
	    df = 1.0
	else:
	    df = sin (t) / t
	xfer.append(df)
    return xfer


def transfer_function_tx():
    xfer = []	# frequency domain transfer function
    for f in xrange(0, 2881):	# specs cover 0 - 2,880 Hz
        # |H(f)| = magnitude response of the Nyquist Raised Cosine Filter
        # |H(f)| = 1                          for |f| < 1920 Hz
        # |H(f)| = 0.5 + 0.5cos(2 π f / 1920) for 1920Hz < |f| < 2880Hz
        # |H(f)| = 0                          for |f| > 2880 Hz

	if f < 1920:
	    hf = 1.0
	else:
	    hf = 0.5 + 0.5 * cos (2 * pi * float(f) / 1920.0)

        # |P(f)| = magnitude response of the Shaping Filter
        # |P(f)| = (π f / 4800) / sin(π f / 4800) for |f| < 2880 Hz
	t = pi * f / float(SYMBOL_RATE)
	if t < 1e-6:
	    pf = 1
	else:
	    pf = t / sin(t)
	# time domain convolution == frequency domain multiplication
	xfer.append(pf * hf)
    return xfer


# span: desired number of impulse response coeffs, in units of symbols
def generate_c4fm_taps(input_rate, output_rate, filter_gain=1.0, span=13, tx=True):
	sps = int(output_rate / input_rate)
	ntaps = (sps * span) | 1

        if tx:
            xfer = transfer_function_tx()
        else:
            xfer = transfer_function_rx()

	impulse_response = np.fft.fftshift(np.fft.irfft(xfer, output_rate))
	start = np.argmax(impulse_response) - (ntaps - 1) / 2
	coeffs = impulse_response[start : start + ntaps]
	gain = filter_gain / sum(coeffs)
	return coeffs * gain


class arb_resampler_cc(gr.hier_block2):
    def __init__(self, input_rate, output_rate):
	gr.hier_block2.__init__(self, "arb_resampler",
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(1, 1, gr.sizeof_gr_complex))
        self.input_rate = input_rate

        rel_freq = 0
        decimation = int(input_rate / output_rate)
        resampled_rate = float(input_rate) / float(decimation) # rate at output of self.lpf
        lpf_coeffs = filter.firdes.low_pass(1.0, input_rate, 7250, 725, filter.firdes.WIN_HANN)

        lpf = filter.fir_filter_ccf(decimation, lpf_coeffs)
        self.osc = analog.sig_source_c(input_rate, analog.GR_SIN_WAVE, rel_freq, 1.0, 0)
        self.set_relative_frequency(rel_freq)
        mixer = blocks.multiply_cc()

        arb_resampler = filter.pfb.arb_resampler_ccf(float(output_rate) / resampled_rate)

        self.connect(self, (mixer, 0))
        self.connect(self.osc, (mixer, 1))
        self.connect(mixer, lpf, arb_resampler)
        self.connect(arb_resampler, self)



    def set_relative_frequency(self, freq):
        if abs(freq) > self.input_rate / 2:
            return False

        if hasattr(self, 'rel_freq') and freq == self.rel_freq:
            return True

        self.rel_freq = freq
        self.osc.set_frequency(self.rel_freq)
        return True


class c4fm_modulator_ff(gr.hier_block2):
    def __init__(self, input_rate=SYMBOL_RATE, output_rate=IF_RATE):
        """P25 pre-modulation (raised cosine filter and pulse shaping) block.

        This hierarchical block implements P25 symbol filtering and
        shaping so that the resulting data stream can be passed to an
        ordinary FM modulator. The input is a stream of float symbols
        scaled to [-1, 1]. The output is a float basedband signal
        suitable for application to an FM modulator.

        The modulator implements the following Nyquist Raised Cosine
        Filter:

        |H(f)| = magnitude response of the Nyquist Raised Cosine Filter
        |H(f)| = 1                          for |f| < 1920 Hz
        |H(f)| = 0.5 + 0.5cos(2 π f / 1920) for 1920Hz < |f| < 2880Hz
        |H(f)| = 0                          for |f| > 2880 Hz

        cascaded with the following shaping filter:

        |P(f)| = magnitude response of the Shaping Filter
        |P(f)| = (π f / 4800) / sin(π f / 4800) for |f| < 2880 Hz

        """

	gr.hier_block2.__init__(self, "c4fm_modulator_bf",
				gr.io_signature(1, 1, gr.sizeof_float), # Input signature
				gr.io_signature(1, 1, gr.sizeof_float)) # Output signature


        if output_rate < input_rate or (output_rate % input_rate) != 0:
            raise Exception("Invalid output rate")

        coeffs = generate_c4fm_taps(input_rate, output_rate, tx=True)
        fir = filter.interp_fir_filter_fff(output_rate / input_rate, coeffs)

        self.connect(self, fir, self)


class c4fm_demodulator_ff(gr.hier_block2):
    def __init__(self, input_rate=IF_RATE, output_rate=SYMBOL_RATE):
	gr.hier_block2.__init__(self, "c4fm_demodulator_ff",
				gr.io_signature(1, 1, gr.sizeof_float),
				gr.io_signature(1, 1, gr.sizeof_float))

        coeffs = generate_c4fm_taps(output_rate, input_rate, span=9, tx=False)
        symbol_filter = filter.fir_filter_fff(1, coeffs)
        fsk4_demod = op25.fsk4_demod_ff(gr.msg_queue(2), input_rate, output_rate)

        self.connect(self, symbol_filter, fsk4_demod, self)


class cqpsk_demodulator_cf(gr.hier_block2):
    def __init__(self, input_rate=IF_RATE, gain_mu=0.025, costas_alpha=0.04, output_rate=SYMBOL_RATE):
	gr.hier_block2.__init__(self, "cqpsk_demodulator_cf",
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(1, 1, gr.sizeof_float))
        self.input_rate = input_rate
        self.output_rate = output_rate

        agc = analog.feedforward_agc_cc(16, 1.0)

        omega = float(self.input_rate) / float(output_rate)
        gain_omega = 0.1 * gain_mu * gain_mu
        alpha = costas_alpha
        beta = 0.125 * alpha * alpha
        fmax = 2400	# Hz
        fmax = 2 * pi * fmax / float(input_rate)
        self.clock = op25_repeater.gardner_costas_cc(omega, gain_mu, gain_omega, alpha,  beta, fmax, -fmax)

        # Perform Differential decoding on the constellation
        diffdec = digital.diff_phasor_cc()

        # take angle of the difference (in radians)
        to_float = blocks.complex_to_arg()

        # convert from radians such that signal is in -3/-1/+1/+3
        rescale = blocks.multiply_const_ff((1 / (pi / 4)))

        slicer = op25_repeater.fsk4_slicer_fb([-2.0, 0.0, 2.0, 4.0])

        self.connect(self, agc, self.clock, diffdec, to_float, rescale, self)


    def get_freq_error(self):	# get error in Hz (approx).
        return int(self.clock.get_freq_error() * self.output_rate)


    def set_omega(self, omega):
        sps = self.input_rate / float(omega)

        if hasattr(self, 'sps') and sps == self.sps:
            return

        self.sps = sps
        self.clock.set_omega(self.sps)


class c4fm_transmitter_fc(gr.hier_block2):
    '''C4FM modulator block

    The C4FM modulator must have the deviation set to provide the
    proper carrier phase shift for each modulated symbol. The
    deviation is set with a test signal consisting of the following
    symbol stream:

    ... 01 01 11 11 01 01 11 11 ...

    This test signal is processed by the modulator to create a C4FM
    signal equivalent to a 1.2 kHz sine wave modulating an FM signal
    with a peak deviation equal to: π/2 x 1800 Hz = 2827 Hz. The
    method of measurement for this test signal and the tolerance on
    the deviation are specified in:

    [1] Digital C4FM / CQPSK Transceiver Methods of Measurement,
        TIA/EIA-102.CAAA, June 1999.

    [2] Digital C4FM/CQPSK Transceiver Performance Recommendations,
        TIA/EIA-102.CAAB, November 2000.
    '''
    def __init__(self, output_rate):
	gr.hier_block2.__init__(self, "c4fm_transmitter_fc",
				gr.io_signature(1, 1, gr.sizeof_float),
				gr.io_signature(1, 1, gr.sizeof_gr_complex))

        # Scale [-1, 1] float values to full-range short samples for
        # the vocoder
        float_to_short = blocks.float_to_short(1, 32768)

        # The encoder expects a stream of shorts with rate 8000
        # samples per seconds on input. It generates a stream of
        # symbols (chars with values 0, 1, 2, 3) at 4800 samples per
        # second.
        encoder = op25_repeater.vocoder(
            True,    # 0=Decode,True=Encode
            False,   # Verbose flag
            0,	     # flex amount
            "",      # udp ip address
            0,	     # udp port
            False)   # dump raw u vectors

        symbol_mapper = symbol_mapper_bf()

        # The C4FM modulator applies a Nyquist Raised Cosine Filter to
        # the input stream, cascaded with a Shaping Filter. The
        # purpose of this step is to cut down the bandwidth. The
        # Raised Cosine Filter cuts off above 2880 Hz.
        c4fm_mod = c4fm_modulator_ff()

        cutoff = 2880
        taps = filter.firdes.low_pass(1.0, IF_RATE, cutoff, cutoff * 0.1, filter.firdes.WIN_HANN)
        interpolator = filter.interp_fir_filter_fff(1, taps)

        fm_mod = fm_modulator_fc(IF_RATE)

        resampler = filter.pfb.arb_resampler_ccf(float(output_rate) / IF_RATE)

        self.connect(
            self,
            float_to_short,
            encoder,
            symbol_mapper,
            c4fm_mod,
            interpolator,
            fm_mod,
            resampler,
            self
        )


class receiver(gr.hier_block2):

    def __init__(self, name, input_rate, *inner):
        gr.hier_block2.__init__(self, name,
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(1, 1, gr.sizeof_float))

        arb_resampler = arb_resampler_cc(input_rate, IF_RATE)

        fa = 6250
        fb = fa + 625
        coeffs = filter.firdes.low_pass(1.0, IF_RATE, (fb + fa) / 2, fb - fa, filter.firdes.WIN_HANN)
        cutoff = filter.fir_filter_ccf(1, coeffs)

        symbol_mapper = symbol_mapper_fb()
        frame_decoder = op25_repeater.p25_frame_assembler(
            "127.0.0.1",     # Wireshark host
            0,               # Wireshark port
            True,            # debug
            True,            # do_imbe
            True,            # do_output
            False,           # do_msgq
            gr.msg_queue(1), # msgq
            True,            # do_audio_output
            False)           # do_phase2_tdma

        # Scale the dynamic range of the stream back to [-1, 1] and
        # feed it to the soundcard.
        short_to_float = blocks.short_to_float(1, 32768)

        self.connect(self, arb_resampler)
        self.connect(arb_resampler, cutoff)
        self.connect(cutoff, *inner)
        self.connect(inner[-1], symbol_mapper, frame_decoder, short_to_float, self)


class c4fm_receiver_cf(receiver):
    def __init__(self, input_rate):
        fm_demod = fm_demodulator_cf()
        c4fm_demod = c4fm_demodulator_ff()
        receiver.__init__(self, "c4fm_receiver_cf", input_rate, fm_demod, c4fm_demod)



class cqpsk_receiver_cf(receiver):
    def __init__(self, input_rate):
        cqpsk_demod = cqpsk_demodulator_cf()
        receiver.__init__(self, "cqpsk_receiver_cf", input_rate, cqpsk_demod)
