#!/usr/bin/env python2
from __future__ import print_function

import os
import argparse

from gnuradio import gr
from gnuradio import blocks
import osmosdr

from p25_config import IF_RATE, FREQUENCY
import p25

#
# A magic constant for LimeSDR. We need to make sure that the sample rate
# For LimeSDR is an integer multiple of the intermediate rate (IF_RATE),
# which is the output rate of C4FM processing blocks. At the same time,
# the sample rate must be high enough so that LimeSDR can properly tune
# its low pass filters. The resulting sample rate will be slightly over
# 7 MSps.
#
LIMESDR_SAMPLE_RATE = IF_RATE * 160


class p25_tx(gr.top_block):

    def setup_limesdr(self, freq, sample_rate):
        self.lime = osmosdr.sink( args="numchan=1 driver=lime,soapy=0")
        print("Sample rate: min=%d, max=%d S/s" % (self.lime.get_sample_rates().start(), self.lime.get_sample_rates().stop()))
        self.lime.set_sample_rate(sample_rate)

        # Automatically select radio frontend bandpass bandwidth
        self.lime.set_bandwidth(0, 0)

        print("Frequency: min=%d, max=%d Hz" % (self.lime.get_freq_range().start(), self.lime.get_freq_range().stop()))
        print("Tuning to %d Hz" % freq);
        self.lime.set_center_freq(freq)

        self.lime.set_gain(0)
        self.lime.set_if_gain(20)
        self.lime.set_bb_gain(0)

        print("Antennas: %s" % repr(self.lime.get_antennas()))
        self.lime.set_antenna('BAND1')


    def __init__(self, freq, wavfile, gain=1.0):
        gr.top_block.__init__(self)

        wav_source = blocks.wavfile_source(wavfile, True)
        audio_amp = blocks.multiply_const_ff(gain)
        self.setup_limesdr(freq, LIMESDR_SAMPLE_RATE)
        trx = p25.c4fm_transmitter_fc(LIMESDR_SAMPLE_RATE)

        self.connect(wav_source, audio_amp, trx, self.lime)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', dest='freq', default=FREQUENCY, nargs='?', help='Frequency')
    parser.add_argument('-f', dest='wavfile', default='%s/Downloads/sentence2.wav' % os.environ['HOME'], nargs='?', help='WAV file')
    parser.add_argument('-g', dest='gain', default='1.0', nargs='?', help='Audio gain')
    args = parser.parse_args()

    f = int(float(args.freq))
    gain = float(args.gain)
    print("Transmitting file %s on %d Hz" % (args.wavfile, f))
    p25_tx(f, args.wavfile, gain=gain).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
