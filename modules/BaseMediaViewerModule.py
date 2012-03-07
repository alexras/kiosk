import os
import random
from BaseModule import BaseModule
import logging
import time
import pprint

class BaseMediaViewerModule(BaseModule):
    def __init__(self, config, media_dir, suffixes):
        super(BaseMediaViewerModule, self).__init__(config)

        self.update_count = 0
        self.refresh_interval = config["refresh_interval"]

        self.initial_freshness = config["initial_freshness"]
        self.freshness_decay_rate = config["freshness_decay_rate"]
        self.freshness_decay_time_days = config["freshness_decay_time_days"]
        self.minimum_freshness = config["minimum_freshness"]

        self.total_freshness = 0

        self.media_dir = media_dir
        self.valid_suffixes = list(suffixes)

        def filter_suffixes(filename):
            for suffix in self.valid_suffixes:
                if filename.find(suffix) != -1:
                    return True
            return False

        self.suffix_filter = filter_suffixes

        self.refresh_content_list()

    def compute_freshness(self, content_file):
        content_file = os.path.join(self.media_dir, content_file)

        # To hack around Windows' silliness, if the modification time is older
        # than the creation time, use the modification time as the file's age
        file_creation_time = min(os.path.getctime(content_file),
                                 os.path.getmtime(content_file))

        days_since_file_creation = ((time.time() - file_creation_time) /
                                    (60 * 60 * 24))

        decays_since_file_creation = int(
            days_since_file_creation / self.freshness_decay_time_days)

        freshness = self.initial_freshness

        for i in xrange(decays_since_file_creation):
            freshness *= (1.0 - self.freshness_decay_rate)

        freshness = int(max(freshness, self.minimum_freshness))

        self.total_freshness += freshness

        return (content_file, freshness)

    def refresh_content_list(self):
        self.total_freshness = 0

        try:
            logging.debug("Refreshing content list ...")
            self.content_list = map(
                self.compute_freshness,
                filter(self.suffix_filter, os.listdir(self.media_dir)))
        except OSError, e:
            logging.error("Caught OSError while listing content directory "
                          "'%s': %s" % (self.media_dir, e))

        self.content_list.sort(key=lambda x: x[1], reverse=True)

        for (filename, freshness) in self.content_list:
            logging.debug("File: %s, Freshness: %d" % (
                    filename, freshness))
        logging.debug("Total freshness: %d" % (self.total_freshness))

    def get_random_content(self):
        random_freshness = random.randint(0, self.total_freshness - 1)

        for (content_file, freshness) in self.content_list:
            random_freshness -= freshness

            if random_freshness <= 0:
                return content_file

    def update(self):
        if self.update_count % self.refresh_interval == 0:
            self.refresh_content_list()
        self.update_count += 1

        media_file = self.get_random_content()

        self.update_from_media(media_file)
