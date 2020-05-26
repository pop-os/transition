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

from . import apt
from . import dismissal
from . import flatpak
from .package import Package
from .window import Window

_ = gettext.gettext

class Application(Gtk.Application):
    """ Application class"""

    def __init__(self, app_list):
        self.app_list = app_list
        super().__init__(application_id='org.pop_os.transition',
                         flags=Gio.ApplicationFlags.REPLACE)
    
    def do_activate(self):
        self.show_window()
    
    def show_window(self, action=None, data=None):
        print('showing window')
        self.withdraw_notification('transition-ready')
        self.window = Window(self)
        self.connect_signals(self.window)
        for package in self.get_installed_packages():
                self.window.app_list.add_package(package)
        self.window.show_all()
    
    def connect_signals(self, window):
        """ Connect signals to their functionality."""
        for button in [window.headerbar.cancel_button,
                       window.headerbar.close_button]:
            button.connect('clicked', self.on_quit_clicked)
        
        window.headerbar.install_button.connect(
            'clicked', self.on_install_clicked, window
        )
        window.headerbar.remove_button.connect(
            'clicked', self.on_remove_clicked, window
        )

        window.dismiss_button.connect(
            'clicked', self.on_dmismiss_clicked, window
        )
    
    def on_dmismiss_clicked(self, button, window, data=None):
        if not dismissal.is_dismissed():
            dismissal.dismiss_notifications()
            self.quit()
        
        else:
            dismissal.show_notifications()
            window.dismiss_button.set_dismiss()

    
    def on_remove_clicked(self, button, window, data=None):
        print('Remove Clicked')
        window.set_buttons_sensitive(False)
        remove_debs = []

        for package in window.app_list.packages:
            package.spinner.start()
            package.status = f'Checking'

            if package.checkbox.get_active():
                package.status = f'Removing deb {package.deb_package}'
                remove_debs.append(package.deb_package)
            else:
                package.spinner.stop()
                package.status = 'Removed'
        
        apt.remove_debs(remove_debs, window)
    
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
                package.status = 'Installed'
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

class Notification(Application):
    """ Application class, with notification"""

    def __init__(self, app_list):
        self.app_list = app_list
        Gtk.Application.__init__(self, application_id='org.pop_os.transition',
                         flags=Gio.ApplicationFlags.IS_SERVICE)
    
    def do_startup(self):
        showwin_action = Gio.SimpleAction.new('show-window', None)
        showwin_action.connect('activate', self.show_window)
        self.add_action(showwin_action)
        
        # Don't show a notification if the user has dismissed them.
        if not dismissal.is_dismissed():
            self.show_notification()

        Gtk.Application.do_startup(self)
    
    def do_activate(self):
        pass
    
    def show_notification(self):
        pkgs = []
        for pkg in self.get_installed_packages():
            pkgs.append(pkg)
        
        if len(pkgs) > 0:
            print('Showing notification')
            notification = Gio.Notification.new(_('Transition to Flatpak'))
            notification.set_body(
                _(
                    'A number of debian packages are no longer recieving updates. '
                    'Please transition these applications to Flatpak to continue '
                    'receiving updates.'
                )
            )
            icon = Gio.ThemedIcon.new('system-software-update')
            notification.set_icon(icon)
            notification.set_default_action('app.show-window')
            print(notification)
            self.send_notification('transition-ready', notification)
        else:
            self.quit()
