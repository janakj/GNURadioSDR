#!/usr/bin/env python2

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
parser.add_argument('-ip', dest = 'ip', default = '192.168.1.214', nargs = '?', help = 'host ip address')
parser.add_argument('-p', dest = 'port', default = '10500', nargs = '?', help = 'port for UDP client')
args = parser.parse_args()


class p25_tx_udp(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)
        ###########
        #VARIABLES#
        ###########
        self.port = port = args.port
        self.host_ip = host_ip = args.ip
        
        ########
        #BLOCKS#
        ########
        self.wav_source = blocks.wavfile_source('/home/irt/Downloads/sentence2.wav', True)
        self.throttle = blocks.throttle(gr.sizeof_float*1, 8000,True)
        self.float_to_short = blocks.float_to_short(1, 32768)
        self.codec2_encode = vocoder.codec2_encode_sp(codec2.MODE_3200)
        self.vector_to_stream = blocks.vector_to_stream(gr.sizeof_char*1, 64)
        self.stream_tagger = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 64, "packet_len")
        self.tagged_stream_to_pdu = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.socket_pdu = blocks.socket_pdu("UDP_CLIENT", host_ip, port, 10000, False)
        
        #############
        #CONNECTIONS#
        #############        
        self.connect((self.wav_source, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.float_to_short, 0))
        self.connect((self.float_to_short, 0), (self.codec2_encode, 0))
        self.connect((self.codec2_encode, 0), (self.vector_to_stream, 0))
        self.connect((self.vector_to_stream, 0), (self.stream_tagger, 0))
        self.connect((self.stream_tagger, 0), (self.tagged_stream_to_pdu, 0))
        self.msg_connect((self.tagged_stream_to_pdu, 'pdus'), (self.socket_pdu, 'pdus'))

if __name__ == '__main__':
    try:
        p25_tx_udp().run()
    except [[KeyboardInterrupt]]:
        pass
