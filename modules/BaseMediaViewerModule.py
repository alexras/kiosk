import os
import random
from BaseModule import BaseModule

class BaseMediaViewerModule(BaseModule):
    def __init__(self, config, media_dir, suffixes):
        super(BaseMediaViewerModule, self).__init__(config)

        self.update_count = 0
        self.media_dir = media_dir
        self.valid_suffixes = list(suffixes)

        def filter_suffixes(filename):
            for suffix in self.valid_suffixes:
                if filename.find(suffix) != -1:
                    return True
            return False

        self.suffix_filter = filter_suffixes

        self.refresh_content_list()

    def refresh_content_list(self):
        try:
            self.content_list = map(
                lambda x: os.path.join(self.media_dir, x),
                filter(self.suffix_filter, os.listdir(self.media_dir)))

            random.shuffle(self.content_list)
        except OSError, e:
            logging.error("Caught OSError while listing content directory "
                          "'%s': %s" % (self.media_dir, e))


    def update(self):
        if self.update_count % len(self.media_dir) == 0:
            self.refresh_content_list()
        self.update_count += 1

        media_file = self.content_list[
            self.update_count % len(self.content_list)]

        self.update_from_media(media_file)
