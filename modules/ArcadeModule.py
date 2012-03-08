import gtk
import webkit
import random

import gtk
import os
import random
from BaseModule import BaseModule
import logging

class BrowserPage(webkit.WebView):
    def __init__(self):
        webkit.WebView.__init__(self)
        settings = self.get_settings()
        settings.set_property("enable-developer-extras", True)
        self.set_full_content_zoom(True)
        settings.set_property("enable-plugins", True)

class ArcadeModule(BaseModule):
    def __init__(self, config):
        super(ArcadeModule, self).__init__(config)
        self.arcade_url = "http://www.twitch.tv/ucsdcsearcade/popout"
        self.webview = BrowserPage()
        self.widget = gtk.ScrolledWindow()
        self.widget.add(self.webview)

        self.webview.load_uri(self.arcade_url)

    def get_widget(self, monitor_number):
        return self.widget

    def update(self):
        return None
