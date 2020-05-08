#!/usr/bin/env python3

"""
Copyright (c) 2020 Ian Santopietro
Copyright (c) 2020 System76, Inc.
All rights reserved.

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice 
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH 
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND 
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, 
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS 
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER 
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF 
THIS SOFTWARE.

pop-transition - Main Application
"""

from gi.repository import Gtk, Gio

from .window import Window
from .package import Package

class Application(Gtk.Application):
    """ Application class"""

    def __init__(self, app_list):
        self.app_list = app_list
        super().__init__(application_id='org.pop-os.transition',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
    
    def do_activate(self):
        window = Window(app=self)
        self.connect_signals(window)
        self.add_testing_data(window)
        window.show()
    
    def connect_signals(self, window):
        """ Connect signals to their functionality."""
        for button in [window.headerbar.cancel_button,
                       window.headerbar.dismiss_button,
                       window.headerbar.close_button,
                       window.dismiss_button]:
            button.connect('clicked', self.on_quit_clicked)
    
    def add_testing_data(self, window):
        """ Populate the GUI with test data to test the UI layout."""
        for app in self.app_list:
            pkg = Package()
            pkg.name = self.app_list[app]['name']
            pkg.version = self.app_list[app]['version']
            pkg.icon = self.app_list[app]['icon']
            pkg.source = 'Flathub'
            pkg.app_id = self.app_list[app]['id']
            pkg.deb_package = self.app_list[app]['deb_pkg']
            window.app_list.add_package(pkg)

        window.show_all()

    def on_quit_clicked(self, button, data=None):
        """ Clicked signal handler for the various 'quit' buttons."""
        self.quit()