import gtk
import os
import random
from BaseModule import BaseModule
import utils

SCRIPT_DIR = os.path.dirname(__file__)

class ImageModule(BaseModule):
    def __init__(self, config):
        super(ImageModule, self).__init__(config)
        self.update_count = 0

        self.image = gtk.Image()
        self.images_dir = config["files"]["images"]
        self.update_image_list()

    def update_image_list(self):
        self.image_list = map(lambda x: os.path.join(self.images_dir, x),
                              os.listdir(self.images_dir))
        random.shuffle(self.image_list)

    def get_widget(self, monitor_number):
        return self.image

    def update(self):
        if self.update_count % len(self.images_dir) == 0:
            self.update_image_list()
        self.update_count += 1

        image_file = self.image_list[
            random.randint(0, len(self.image_list) - 1)]

        assert os.path.exists(image_file)

        print "Displaying image '%s'" % (image_file)

        pixbuf = utils.scale_pixbuf(gtk.gdk.pixbuf_new_from_file(image_file),
                                    self.width, self.height)

        self.image.set_from_pixbuf(None)
        self.image.set_from_pixbuf(pixbuf)
