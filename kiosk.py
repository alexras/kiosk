#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import json
import os
import sys
import time

from modules.ImageModule import ImageModule
from modules.HTMLModule import HTMLModule
from modules.PDFModule import PDFModule

SCRIPT_DIR = os.path.dirname(__file__)

class Kiosk(object):
    def update_module_handler(self, module, monitor_number):
        def handler(widget, event):
            if event.width > 200:
                module.width = event.width
                module.height = event.height
                widget.disconnect(self.initial_update_handler_ids[widget])

                try:
                    print "Refreshing monitor %d" % (monitor_number)
                    module.update()
                except Exception, e:
                    print >>sys.stderr, "Caught exception:"
                    print >>sys.stderr, e
        return handler

    def realize_callback(self, widget):
        widget.window.set_cursor(self.get_invisible_cursor())

    def get_invisible_cursor(self):
        pix_data = """/* XPM */
 static char * invisible_xpm[] = {
 "1 1 1 1",
 "       c None",
 " "};"""
        color = gtk.gdk.Color()
        pix = gtk.gdk.pixmap_create_from_data(
            None, pix_data, 1, 1, 1, color, color)
        invisible = gtk.gdk.Cursor(pix, pix, color, color, 0, 0)
        return invisible

    def update_modules(self):
        for monitor_number, monitor in enumerate(self.monitors):
            module = self.display_modules[monitor_number]

            try:
                print "Refreshing monitor %d" % (monitor_number)
                module.update()
            except Exception, e:
                print >>sys.stderr, "Caught exception:"
                print >>sys.stderr, e

        self.update_timer = gobject.timeout_add_seconds(
            self.config["kiosk"]["transition_time"], self.update_modules)

    def __init__(self, config_file):
        with open(config_file, 'r') as fp:
            self.config = json.load(fp)

        self.screen = gtk.gdk.screen_get_default()

        if self.screen is None:
            print >>sys.stderr, "Can't initialize screen"
            sys.exit(1)

        self.monitors = []
        self.display_modules = [HTMLModule(self.config),
                                ImageModule(self.config),
                                ImageModule(self.config),
                                HTMLModule(self.config)]
        self.initial_update_handler_ids = {}

        for monitor_number in xrange(self.screen.get_n_monitors()):
            monitor = gtk.Window(gtk.WINDOW_TOPLEVEL)
            color = gtk.gdk.color_parse(
                self.config["kiosk"]["background_color"])
            monitor.modify_bg(gtk.STATE_NORMAL, color)

            monitor_rect = self.screen.get_monitor_geometry(monitor_number)
            monitor.move(monitor_rect.x, monitor_rect.y)
            monitor.connect("realize", self.realize_callback)
            monitor.connect("destroy", gtk.main_quit)

            monitor.fullscreen()
            monitor.set_decorated(False)
            self.monitors.append(monitor)

        for monitor_number, monitor in enumerate(self.monitors):
            module = self.display_modules[monitor_number]
            handler_id = monitor.connect("configure_event",
                                         self.update_module_handler(
                    module, monitor_number))
            self.initial_update_handler_ids[monitor] = handler_id

            monitor.add(module.get_widget(monitor_number))
            monitor.show_all()

        self.update_timer = gobject.timeout_add_seconds(
            self.config["kiosk"]["transition_time"], self.update_modules)

    def main(self):
        gobject.threads_init()
        gtk.main()

if __name__ == '__main__':
    log_fp = open(os.path.join(SCRIPT_DIR, "kiosk.log"), 'w+')
    sys.stdout = log_fp
    sys.stderr = log_fp

    kiosk = Kiosk("config.json")
    kiosk.main()
