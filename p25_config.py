from gnuradio import vocoder

#
# Any parameters that need to be synchronized between the transmitter
# and the receiver belong here.
#

CODEC2_MODE = vocoder.codec2.MODE_3200
CODEC2_BITS_PER_FRAME = 64
IF_RATE = 48000
FREQUENCY='139.05e6'
