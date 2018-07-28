from gnuradio import vocoder

#
# Any parameters that need to be synchronized between the transmitter
# and the receiver belong here.
#

DEFAULT_PORT = '10500'
PACKET_SIZE = 64
CODEC2_MODE = vocoder.codec2.MODE_3200
SAMPLE_SCALE = 32768
SAMPLE_RATE = 8000
