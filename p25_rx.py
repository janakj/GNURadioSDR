#!/usr/bin/env python2
from __future__ import print_function

import os
import argparse

from gnuradio import gr
from gnuradio import audio
import osmosdr

from p25_config import IF_RATE, FREQUENCY
import p25

#
# A magic constant for RTL-SDR. We need to make sure that the sample rate
# is an integer multiple of the intermediate rate (IF_RATE),
# which is the processing rate of C4FM blocks. At the same time,
# the sample rate must be high enough for RTL-SDR. The resulting sample
# rate will be around 960 kSps.
#
RTL_SAMPLE_RATE = IF_RATE * 20


class p25_rx(gr.top_block):
    def __init__(self, freq):
        gr.top_block.__init__(self)

        rtl = osmosdr.source(args="numchan=1")
        rtl.set_sample_rate(RTL_SAMPLE_RATE)
        rtl.set_center_freq(freq)
        rtl.set_freq_corr(0)
        rtl.set_dc_offset_mode(0)
        rtl.set_iq_balance_mode(0)
        rtl.set_gain_mode(True)
        rtl.set_gain(10)
        rtl.set_if_gain(20)
        rtl.set_bb_gain(20)
        rtl.set_antenna('RX')
        rtl.set_bandwidth(0)

        receiver = p25.c4fm_receiver_cf(RTL_SAMPLE_RATE)
        audio_sink = audio.sink(8000, '', True)

        self.connect(rtl, receiver, audio_sink)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', dest='freq', default=FREQUENCY, nargs='?', help='Frequency')
    args = parser.parse_args()

    f = int(float(args.freq))
    print("Listening on %d Hz" % (f))
    p25_rx(f).run()


if __name__ == '__main__':
    try:
        main()
    except [[KeyboardInterrupt]]:
        pass
