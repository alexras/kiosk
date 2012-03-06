#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import json
import os
import sys
import time
import logging
import logging.handlers
import time

import modules

# From http://stackoverflow.com/a/452981
def get_class(classname):
    classname_parts = classname.split('.')
    module = '.'.join(classname_parts[:-1])
    class_obj = __import__(module)

    for component in classname_parts[1:]:
        class_obj = getattr(class_obj, component)

    return class_obj

SCRIPT_DIR = os.path.dirname(__file__)
KIOSK_LOG_FILE = os.path.join(SCRIPT_DIR, "kiosk.log")

# Configure logging to roll over after 10 MB of logs, keeping the most recent 5
# copies
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_file_handler = logging.handlers.RotatingFileHandler(
    KIOSK_LOG_FILE, maxBytes=10000000, backupCount=5)
log_file_handler.setFormatter(logging.Formatter(
        fmt='%(process)s\t%(asctime)-15s\t%(message)s'))
logger.addHandler(log_file_handler)

class Kiosk(object):
    def update_module_handler(self, module, monitor_number):
        def handler(widget, event):
            if event.width > 200:
                module.width = event.width
                module.height = event.height
                widget.disconnect(self.initial_update_handler_ids[widget])

                try:
                    logging.debug("Refreshing monitor %d" % (monitor_number))
                    module.update()
                except Exception, e:
                    logging.exception(e)
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
                logging.debug("Refreshing monitor %d" % (monitor_number))
                module.update()
            except Exception, e:
                logging.exception(e)

        self.update_timer = gobject.timeout_add_seconds(
            self.config["kiosk"]["transition_time"], self.update_modules)

    def get_monitor_bounds(self):
        monitor_bounds = {}

        for monitor_number, monitor in self.monitors.items():
            monitor_geometry = self.screen.get_monitor_geometry(monitor_number)

            monitor_bounds[monitor_number] = {
                "width" : monitor.width,
                "height" : monitor.height,
                "x" : monitor_geometry.x,
                "y" : monitor_geometry.y
                }

        return monitor_bounds

    def load_config(self):
        """
        Loads the current configuration from the file named by self.config_path
        into self.config as a dictionary. If you fail to parse the config file,
        roll back, wait 5 seconds, and re-try until you read a config file
        successfully
        """
        parsed_config = False
        old_config = self.config

        while not parsed_config:
            try:
                with open(self.config_path, 'r') as fp:
                    self.config = json.load(fp)
                    parsed_config = True
            except ValueError, e:
                self.config = old_config
                logging.exception(e)
                time.sleep(5)

    def init_display_module(self, module, module_config):
        return get_class("modules.%(module_name)s.%(module_name)s" %
                         {"module_name" : module})(module_config)

    def __init__(self, config_file):
        self.config_path = config_file
        self.config = {}

        self.load_config()

        self.screen = gtk.gdk.screen_get_default()

        if self.screen is None:
            sys.exit("Can't initialize screen")

        self.monitors = []
        self.display_modules = []

        for module, module_config in self.config["modules"].items():
            self.display_modules.append(self.init_display_module(
                    module, module_config))

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
    kiosk = Kiosk("config.json")
    kiosk.main()
