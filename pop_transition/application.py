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

import gettext

from gi.repository import Gtk, Gio

from . import flatpak
from .package import Package
from .window import Window

_ = gettext.gettext

class Application(Gtk.Application):
    """ Application class"""

    def __init__(self, app_list):
        self.app_list = app_list
        super().__init__(application_id='org.pop_os.transition',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
    
    def do_startup(self):
        showwin_action = Gio.SimpleAction.new('show-window', None)
        showwin_action.connect('activate', self.show_window)
        self.add_action(showwin_action)
    
    def do_activate(self):
        self.show_notification()
    
    def show_notification(self):
        notification = Gio.Notification.new(_('Transition to Flatpak'))
        notification.set_body(
            _(
                'A number of debian packages are no longer recieving updates. '
                'Please transition these applications to Flatpak to continue '
                'receiving updates.'
            )
        )
        icon = Gio.ThemedIcon.new('system-software-sources')
        notification.set_icon(icon)
        notification.set_default_action('app.show_window')
        self.send_notification('transition-available', notification)
    
    def show_window(self):
        window = Window(app=self)
        self.connect_signals(window)
        for package in self.get_installed_packages():
                window.app_list.add_package(package)
        window.show_all()
    
    def connect_signals(self, window):
        """ Connect signals to their functionality."""
        for button in [window.headerbar.cancel_button,
                       window.headerbar.dismiss_button,
                       window.headerbar.close_button,
                       window.dismiss_button]:
            button.connect('clicked', self.on_quit_clicked)
        
        window.headerbar.install_button.connect(
            'clicked', self.on_install_clicked, window
        )
    
    def on_install_clicked(self, button, window, data=None):
        print('Install clicked')
        window.set_buttons_sensitive(False)
        install_flatpaks = []
        
        for package in window.app_list.packages:
            package.spinner.start()
            package.status = 'Checking'
            if package.checkbox.get_active():
                package.status = 'Installing'
                install_flatpaks.append(package)
            else:
                package.spinner.stop()
                package.status = ''
        flatpak.install_flatpaks(install_flatpaks, window)
        
    
    def get_installed_packages(self):
        """ Yield a list of installed Packages."""
        for app in self.app_list:
            pkg = Package()
            pkg.name = self.app_list[app]['name']
            pkg.version = self.app_list[app]['version']
            pkg.icon = self.app_list[app]['icon']
            pkg.source = 'Flathub'
            pkg.app_id = self.app_list[app]['id']
            pkg.deb_package = self.app_list[app]['deb_pkg']
            if pkg.installed:
                yield pkg

    def on_quit_clicked(self, button, data=None):
        """ Clicked signal handler for the various 'quit' buttons."""
        self.quit()