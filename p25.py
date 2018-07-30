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


def fm_modulator_fc(rate, max_deviation=12.5e3):
    # The analog FM modulator expects an audio signal (stream of
    # floats) on its input and produces a complex baseband signal on
    # the output. The output signal can be mixed with a local
    # oscilator, or directly passed to SDR hardware sink.
    k = 2 * math.pi * max_deviation / rate
    sensitivity = 1.5 * k # adjust for proper c4fm deviation level
    return analog.frequency_modulator_fc(sensitivity)


def fm_demodulator_cf(rate, symbol_deviation=600.0):
    gain = rate / (2.0 * pi * symbol_deviation)
    return analog.quadrature_demod_cf(gain)


def transfer_function_rx():
    # p25 c4fm de-emphasis filter
    # Specs undefined above 2,880 Hz.  It would be nice to have a sharper
    # rolloff, but this filter is cheap enough....
    xfer = []	# frequency domain transfer function
    for f in xrange(0, 4800):
        # D(f)
	t = pi * f / 4800
	if t < 1e-6:
	    df = 1.0
	else:
	    df = sin (t) / t
	xfer.append(df)
    return xfer


def transfer_function_tx():
    xfer = []	# frequency domain transfer function
    for f in xrange(0, 2881):	# specs cover 0 - 2,880 Hz
        # H(f)
	if f < 1920:
	    hf = 1.0
	else:
	    hf = 0.5 + 0.5 * cos (2 * pi * float(f) / 1920.0)

	# P(f)
	t = pi * f / 4800.0
	if t < 1e-6:
	    pf = 1
	else:
	    pf = t / sin (t)
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
    def __init__(self, input_rate=4800, output_rate=48000):
        """Hierarchical block for RRC-filtered P25 FM modulation.

	The input is a dibit (P25 symbol) stream (char, not packed)
	and the output is the float "C4FM" signal at baseband,
	suitable for application to an FM modulator stage
        """

	gr.hier_block2.__init__(self, "c4fm_modulator_bf",
				gr.io_signature(1, 1, gr.sizeof_float), # Input signature
				gr.io_signature(1, 1, gr.sizeof_float)) # Output signature

        lcm = gru.lcm(input_rate, output_rate)
        self._interp_factor = int(lcm // input_rate)
        self._decimation = int(lcm // output_rate)


        coeffs = generate_c4fm_taps(input_rate, output_rate, tx=True)
        self.filter = filter.interp_fir_filter_fff(self._interp_factor, coeffs)

        self.connect(self, self.filter)

        if (self._decimation > 1):
            self.decimator = filter.rational_resampler_fff(1, self._decimation)
            self.connect(self.filter, self.decimator, self)
        else:
            self.connect(self.filter, self)


class c4fm_demodulator_ff(gr.hier_block2):
    def __init__(self, input_rate, symbol_rate=4800):
	gr.hier_block2.__init__(self, "c4fm_demodulator_ff",
				gr.io_signature(1, 1, gr.sizeof_float),
				gr.io_signature(1, 1, gr.sizeof_float))

        coeffs = generate_c4fm_taps(symbol_rate, input_rate, span=9, tx=False)
        symbol_filter = filter.fir_filter_fff(1, coeffs)
        fsk4_demod = op25.fsk4_demod_ff(gr.msg_queue(2), input_rate, symbol_rate)

        self.connect(self, symbol_filter, fsk4_demod, self)


class cqpsk_demodulator_cf(gr.hier_block2):
    def __init__(self, input_rate, gain_mu=0.025, costas_alpha=0.04, symbol_rate=4800):
	gr.hier_block2.__init__(self, "cqpsk_demodulator_cf",
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(1, 1, gr.sizeof_float))
        self.input_rate = input_rate

        agc = analog.feedforward_agc_cc(16, 1.0)

        omega = float(self.input_rate) / float(symbol_rate)
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


    def set_omega(self, omega):
        sps = self.input_rate / float(omega)

        if hasattr(self, 'sps') and sps == self.sps:
            return
        
        self.sps = sps
        self.clock.set_omega(self.sps)


class c4fm_transmitter_fc(gr.hier_block2):
    def __init__(self, output_rate=48000):
	gr.hier_block2.__init__(self, "c4fm_transmitter_fc",
				gr.io_signature(1, 1, gr.sizeof_float),
				gr.io_signature(1, 1, gr.sizeof_gr_complex))
        
        # Scales [-1, 1] float samples to full-range short samples for CODEC2 encoder
        float_to_short = blocks.float_to_short(1, 32768)

        # The encoder expects a stream of shorts with rate 8000
        # samples per seconds on input. It generates a stream of
        # symbols (chars) at 4800 samples per second.
        encoder = op25_repeater.vocoder(
            True,    # 0=Decode,True=Encode
            False,   # Verbose flag
            0,	     # flex amount
            "",      # udp ip address
            0,	     # udp port
            False)   # dump raw u vectors

        audio_rate = 24000

        symbol_mapper = digital.chunks_to_symbols_bf([1.0/3.0, 1.0, -(1.0/3.0), -1.0])

        # The C4FM modulator does 4FSK. It expects a stream of symbols
        # (chars) on its input with a rate of 4800 symbols per second.
        # It outputs an "audio" signal (stream of floats) that is
        # suitable as input to an analog frequency modulator.
        c4fm_mod = c4fm_modulator_ff(4800, audio_rate)

        interp_factor = output_rate / audio_rate
        low_pass = 2.88e3
        interp_taps = filter.firdes.low_pass(1.0, output_rate, low_pass, low_pass * 0.1, filter.firdes.WIN_HANN)
        interpolator = filter.interp_fir_filter_fff(int(interp_factor), interp_taps)

        fm_mod = fm_modulator_fc(output_rate)

        self.connect(
            self,
            float_to_short,
            encoder,
            symbol_mapper,
            c4fm_mod,
            interpolator,
            fm_mod,
            self
        )


class receiver(gr.hier_block2):
    IF_RATE = 24000
    
    def __init__(self, name, input_rate=48000, *inner):
        gr.hier_block2.__init__(self, name,
				gr.io_signature(1, 1, gr.sizeof_gr_complex),
				gr.io_signature(1, 1, gr.sizeof_float)) 

        arb_resampler = arb_resampler_cc(input_rate, self.IF_RATE)
        symbol_mapper = op25_repeater.fsk4_slicer_fb([-2.0, 0.0, 2.0, 4.0])
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
        self.connect(arb_resampler, *inner)
        self.connect(inner[-1], symbol_mapper, frame_decoder, short_to_float, self)
        

class c4fm_receiver_cf(receiver):
    def __init__(self, rate=48000):
        fm_demod = fm_demodulator_cf(self.IF_RATE)
        c4fm_demod = c4fm_demodulator_ff(self.IF_RATE)
        receiver.__init__(self, "c4fm_receiver_cf", rate, fm_demod, c4fm_demod) 



class cqpsk_receiver_cf(receiver):
    def __init__(self, rate=48000):
        cqpsk_demod = cqpsk_demodulator_cf(self.IF_RATE)
        receiver.__init__(self, "cqpsk_receiver_cf", rate, cqpsk_demod)
