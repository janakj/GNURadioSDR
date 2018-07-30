from gnuradio import vocoder

#
# Any parameters that need to be synchronized between the transmitter
# and the receiver belong here.
#

DEFAULT_PORT = '10500'
CODEC2_MODE = vocoder.codec2.MODE_3200
CODEC2_BITS_PER_FRAME = 64
SAMPLE_RATE = 8000
MTU = 1400
FREQUENCY=139.05e6
