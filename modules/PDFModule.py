import gtk
import poppler
import urllib
import random
import os
from BaseModule import BaseModule
import utils
import glib

class PDFModule(BaseModule):
    def __init__(self, config):
        super(PDFModule, self).__init__(config)
        self.pdf_image = gtk.Image()
        self.pdf_dir = config["files"]["pdfs"]

    def get_widget(self, monitor_number):
        return self.pdf_image

    def update(self):
        try:
            file_list = map(lambda x: os.path.join(self.pdf_dir, x),
                            filter(lambda y: y[-4:] == ".pdf",
                                   os.listdir(self.pdf_dir)))
        except OSError, e:
            print "Caught OSError while listing directory: %s" % (e)
            return

        try:
            pdf_file = file_list[random.randint(0, len(file_list) - 1)]
            pdf_url = urllib.pathname2url(pdf_file)

            if pdf_url[0:2] == "//":
                pdf_url = pdf_url[2:]

            pdf_url = "file://%s" % (pdf_url)

            poppler_doc = poppler.document_new_from_file(pdf_url, password=None)

            pdf_page = poppler_doc.get_page(0)
            page_width, page_height = map(int, pdf_page.get_size())

            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                                    page_width, page_height)

            pdf_page.render_to_pixbuf(
                src_x = 0, src_y = 0, src_width = page_width,
                src_height = page_height, scale = 1, rotation = 0,
                pixbuf = pixbuf)

            scaled_pixbuf = utils.scale_pixbuf(pixbuf, self.width, self.height)

            print "Opening PDF %s'" % (pdf_url)
            self.pdf_image.set_from_pixbuf(None)
            self.pdf_image.set_from_pixbuf(scaled_pixbuf)
        except:
            print "PDF '%s' is corrupted or inaccessible" % (pdf_url)


