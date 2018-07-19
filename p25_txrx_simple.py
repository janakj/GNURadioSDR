#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: P25 Txrx Simple
# Generated: Thu Jul 19 16:47:38 2018
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
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
from gnuradio import qtgui


class p25_txrx_simple(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "P25 Txrx Simple")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("P25 Txrx Simple")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "p25_txrx_simple")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Blocks
        ##################################################
        self.vocoder_codec2_encode_sp_0 = vocoder.codec2_encode_sp(codec2.MODE_3200)
        self.vocoder_codec2_decode_ps_0 = vocoder.codec2_decode_ps(codec2.MODE_3200)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/irt/Downloads/sentence2.wav', False)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_char*1, 64)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, 8000,True)
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 64)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 64, "packet_len")
        self.blocks_socket_pdu_1 = blocks.socket_pdu("UDP_SERVER", '0.0.0.0', '10500', 10000, False)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("UDP_CLIENT", '192.168.1.214', '10500', 10000, False)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 32768)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 32768)
        self.audio_sink_0 = audio.sink(8000, '', True)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_1, 'pdus'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.blocks_socket_pdu_0, 'pdus'))
        self.connect((self.blocks_float_to_short_0, 0), (self.vocoder_codec2_encode_sp_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.vocoder_codec2_decode_ps_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.vocoder_codec2_decode_ps_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.vocoder_codec2_encode_sp_0, 0), (self.blocks_vector_to_stream_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "p25_txrx_simple")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


def main(top_block_cls=p25_txrx_simple, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
