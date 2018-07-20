#!/usr/bin/env python2


from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import vocoder
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.vocoder import codec2
from optparse import OptionParser
import sys
import argparse


#Arguments: ip address and port for UDP client
parser = argparse.ArgumentParser(description='Host ip and port')
parser.add_argument('-p', dest = 'port', default = '10500', nargs = '?', help = 'port for UDP server')
args = parser.parse_args()

class p25_rx_udp(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        ###########
        #VARIABLES#
        ###########
        self.port = port = args.port
        
        ########
        #BLOCKS#
        ########
        self.socket_pdu = blocks.socket_pdu("UDP_SERVER", '0.0.0.0', '10500', 10000, False)
        self.pdu_to_tagged_stream = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.stream_to_vector = blocks.stream_to_vector(gr.sizeof_char*1, 64)
        self.codec2_decode = vocoder.codec2_decode_ps(codec2.MODE_3200)
        self.short_to_float = blocks.short_to_float(1, 32768)
        self.audio_sink = audio.sink(8000, '', True) 
        
        #############
        #CONNECTIONS#
        #############        
        self.msg_connect((self.socket_pdu, 'pdus'), (self.pdu_to_tagged_stream, 'pdus'))
        self.connect((self.pdu_to_tagged_stream, 0), (self.stream_to_vector, 0))
        self.connect((self.stream_to_vector, 0), (self.codec2_decode, 0))
        self.connect((self.codec2_decode, 0), (self.short_to_float, 0))
        self.connect((self.short_to_float, 0), (self.audio_sink, 0))



if __name__ == '__main__':
    try:
        p25_rx_udp().run()
    except [[KeyboardInterrupt]]:
        pass
