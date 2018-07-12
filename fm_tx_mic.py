#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Fm Tx Mic
# Generated: Mon Jul  9 14:58:55 2018
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
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr
import sys
import time
from gnuradio import qtgui
import argparse

#Parse frequency argument
parser = argparse.ArgumentParser(description='Set frequency')
parser.add_argument('frequency', type=float, default = 87.7e6, nargs = '?')
args = parser.parse_args()

class fm_tx_mic(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Fm Tx Mic")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Fm Tx Mic")
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

        self.settings = Qt.QSettings("GNU Radio", "fm_tx_mic")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 44100
        self.samp_out = samp_out = 500000
        self.freq_tx = freq_tx = args.frequency #91.3e6

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=samp_out,
                decimation=samp_rate*4,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_sink_1 = osmosdr.sink( args="numchan=" + str(1) + " " + 'driver=lime,soapy=0' )
        self.osmosdr_sink_1.set_sample_rate(samp_out)
        self.osmosdr_sink_1.set_center_freq(freq_tx, 0)
        self.osmosdr_sink_1.set_freq_corr(0, 0)
        self.osmosdr_sink_1.set_gain(10, 0)
        self.osmosdr_sink_1.set_if_gain(20, 0)
        self.osmosdr_sink_1.set_bb_gain(20, 0)
        self.osmosdr_sink_1.set_antenna('BAND1', 0)
        self.osmosdr_sink_1.set_bandwidth(0, 0)

        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.audio_source_0 = audio.source(samp_rate, '', True)
        self.analog_wfm_tx_0 = analog.wfm_tx(
        	audio_rate=samp_rate,
        	quad_rate=samp_rate*4,
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1.0,
        )
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_out, analog.GR_COS_WAVE, 0, 142.857e-3, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_wfm_tx_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.audio_source_0, 0), (self.analog_wfm_tx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.osmosdr_sink_1, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_multiply_xx_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "fm_tx_mic")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_samp_out(self):
        return self.samp_out

    def set_samp_out(self, samp_out):
        self.samp_out = samp_out
        self.osmosdr_sink_1.set_sample_rate(self.samp_out)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_out)

    def get_freq_tx(self):
        return self.freq_tx

    def set_freq_tx(self, freq_tx):
        self.freq_tx = freq_tx
        self.osmosdr_sink_1.set_center_freq(self.freq_tx, 0)


def main(top_block_cls=fm_tx_mic, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    #tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
