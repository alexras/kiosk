import gtk
import webkit
import random

import gtk
import os
import random
from BaseModule import BaseModule
import feedparser

SCRIPT_DIR = os.path.dirname(__file__)

class BrowserPage(webkit.WebView):
    def __init__(self):
        webkit.WebView.__init__(self)
        settings = self.get_settings()
        settings.set_property("enable-developer-extras", True)
        self.set_full_content_zoom(True)

        # Disable plugins and scripts to be on the safe side
        settings.set_property("enable-plugins", False)

class HTMLModule(BaseModule):
    def __init__(self, config):
        super(HTMLModule, self).__init__(config)
        self.webview = BrowserPage()
        self.widget = gtk.ScrolledWindow()
        self.widget.add(self.webview)

        self.feeds = config["rss_feeds"]

        self.update_urls()

        self.update_count = 0

    def update_urls(self):
        self.urls = set()

        for feed in self.feeds:
            parsed_feed = feedparser.parse(feed)

            if parsed_feed.bozo == 1:
                continue

            for entry in parsed_feed.entries:
                self.urls.add(entry.link)

        self.urls = list(self.urls)
        random.shuffle(self.urls)

    def get_widget(self, monitor_number):
        return self.widget

    def update(self):
        if len(self.urls) > 0 and self.update_count % len(self.urls) == 0:
            self.update_urls()
        self.update_count += 1

        if len(self.urls) > 0:
            current_url = self.urls[self.update_count % len(self.urls)]
        else:
            current_url = urllib.pathname2url(
                os.path.join(SCRIPT_DIR, "html_module_error.html"))

        print "Opening URL '%s'" % (current_url)
        self.webview.load_uri(current_url)
