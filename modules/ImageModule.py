import gtk
import os
from BaseMediaViewerModule import BaseMediaViewerModule
import utils
import logging

class ImageModule(BaseMediaViewerModule):
    def __init__(self, config):
        super(ImageModule, self).__init__(
            config, config["files"]["images"], [".png", ".jpg", ".gif", ".tif"])

        self.image = gtk.Image()

    def get_widget(self, monitor_number):
        return self.image

    def update_from_media(self, image_file):
        assert os.path.exists(image_file)

        logging.debug("Displaying image '%s'" % (image_file))

        pixbuf = utils.scale_pixbuf(gtk.gdk.pixbuf_new_from_file(image_file),
                                    self.width, self.height)

        self.image.set_from_pixbuf(None)
        self.image.set_from_pixbuf(pixbuf)
