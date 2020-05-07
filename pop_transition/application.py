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

    def __init__(self):
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
                       window.headerbar.close_button]:
            button.connect('clicked', self.on_quit_clicked)
    
    def add_testing_data(self, window):
        """ Populate the GUI with test data to test the UI layout."""
        android_studio = Package(
            name='Android Studio',
            version='3.6.3.0',
            app_id='com.android.studio',
            deb='android-studio'
        )
        window.app_list.add_package(android_studio)
        peek = Package(
            name='Peek',
            version='1.5.1',
            app_id='com.peak',
            deb='peek'
        )
        window.app_list.add_package(peek)
        mattermost = Package(
            name='Mattermost',
            version='4.4.1',
            app_id='com.mattermost.desktop',
            deb='mattermost-desktop'
        )
        window.app_list.add_package(mattermost)
        spotify = Package(
            name='Spotify',
            version='1.1.26.501',
            app_id='com.spotify.desktop',
            deb='spotify'
        )
        window.app_list.add_package(spotify)
        signal = Package(
            name='Signal',
            version='1.33.4',
            app_id='com.signal.desktop',
            deb='signal-desktop'
        )
        window.app_list.add_package(signal)

        window.show_all()

    def on_quit_clicked(self, button, data=None):
        """ Clicked signal handler for the various 'quit' buttons."""
        self.quit()