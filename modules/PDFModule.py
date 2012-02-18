import gtk
import urllib
import random
import os
from BaseMediaViewerModule import BaseMediaViewerModule
import utils
import glib
import logging
import subprocess

class PDFModule(BaseMediaViewerModule):
    def __init__(self, config):
        super(PDFModule, self).__init__(
            config, config["files"]["pdfs"], [".pdf"])

        self.pdf_image = gtk.Image()

    def get_widget(self, monitor_number):
        return self.pdf_image

    def convert_pdfs(self):
        for filename in self.content_list:
            png_filename = filename[:-4] + ".png"

            if not os.path.exists(png_filename):
                logging.debug("Converting '%s' to png" % (filename))

                cmd = ('%s -sOutputFile="%s" -sDEVICE=%s -r%d '
                       '-dBATCH -dNOPAUSE -dSAFER "%s"' %
                       (self.config["ghostscript"]["binary_path"],
                        png_filename,
                        self.config["ghostscript"]["output_device"],
                        self.config["ghostscript"]["ppi"],
                        filename))
                subproc = subprocess.Popen(cmd, shell=True)
                subproc.communicate()

    def update_from_media(self, pdf_file):
        self.convert_pdfs()

        try:
            png_file = pdf_file[:-4] + ".png"

            # Skip PDFs that failed to convert to PNGs successfully
            if not os.path.exists(png_file):
                return

            pixbuf = utils.scale_pixbuf(gtk.gdk.pixbuf_new_from_file(png_file),
                                        self.width, self.height)

            logging.debug("Opening PNG convert of PDF %s'" % (pdf_file))
            self.pdf_image.set_from_pixbuf(None)
            self.pdf_image.set_from_pixbuf(pixbuf)
        except Exception, e:
            logging.error("Converted PNG for '%s' is corrupted or inaccessible"
                          % (pdf_file))
            logging.exception(e)


