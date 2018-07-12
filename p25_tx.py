#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: P25 Tx
# Generated: Mon Jul  9 11:56:17 2018
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
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import vocoder
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from gnuradio.vocoder import codec2
from optparse import OptionParser
import osmosdr
import pmt
import sys
import time
from gnuradio import qtgui


class p25_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "P25 Tx")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("P25 Tx")
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

        self.settings = Qt.QSettings("GNU Radio", "p25_tx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 8000
        self.freq = freq = 450e6

        ##################################################
        # Blocks
        ##################################################
        self._freq_range = Range(450e6, 490e6, 12.5e3, 450e6, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "freq", "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_win)
        self.vocoder_codec2_encode_sp_0 = vocoder.codec2_encode_sp(codec2.MODE_3200)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=1,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'driver=lime,soapy=0' )
        self.osmosdr_sink_0.set_sample_rate(8000)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(10, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('BAND1', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)

        self.digital_hdlc_framer_pb_0 = digital.hdlc_framer_pb('frame_tag')
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
        	samples_per_symbol=2,
        	sensitivity=1.0,
        	bt=0.35,
        	verbose=False,
        	log=False,
        )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_char*1, 64)
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.blocks_tagged_stream_to_pdu_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, 64, "packet_len")
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, '/home/irt/codec2-dev/raw/hts1a.raw', True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.analog_sig_source_x_0 = analog.sig_source_c(8000, analog.GR_COS_WAVE, 0, 142.857e-3, 0)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0, 'pdus'), (self.digital_hdlc_framer_pb_0, 'in'))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_file_source_0, 0), (self.vocoder_codec2_encode_sp_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_gfsk_mod_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.digital_hdlc_framer_pb_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.vocoder_codec2_encode_sp_0, 0), (self.blocks_vector_to_stream_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "p25_tx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)


def main(top_block_cls=p25_tx, options=None):

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
