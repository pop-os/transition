#!/usr/bin/env python3

"""
Copyright (c) 2020 Ian Santopietro
Copyright (c) 2020 System76, Inc.
All rights reserved.

This file is part of Pop-Transition.

    Pop-Transition is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Pop-Transition is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Pop-Transition.  If not, see <https://www.gnu.org/licenses/>.

pop-transition is a simple app that notifies users if they have debian versions
of packages which were transitioned to Flatpak in Pop_OS 20.04. 
"""

import gettext
import gi
import sys

gi.require_versions (
    {
        'Flatpak': '1.0',
        'Gdk': '3.0',
        'GdkPixbuf': '2.0',
        'Gio': '2.0',
        'Gtk': '3.0',
    }
)

from .application import Notification, Application

gettext.bindtextdomain('pop-transition', '/usr/share/pop-transition/po')
gettext.textdomain('pop-transition')

APPS = {
    'android_studio': {
        'name': 'Android Studio',
        'version': '3.6.3.0',
        'icon': 'androidstudio',
        'id': 'com.google.AndroidStudio',
        'old_id': None,
        'deb_pkg': 'android-studio'
    },
    'chromium': {
        'name': 'Chromium',
        'version': '87.0.4280.88-1',
        'icon': 'chromium',
        'id': 'org.chromium.Chromium',
        'old_id': None,
        'deb_pkg': 'chromium'
    },
    'dbeaver': {
        'name': 'DBeaver',
        'version': '7.0.4',
        'icon': '/usr/share/dbeaver/dbeaver.png',
        'id': 'io.dbeaver.DBeaverCommunity',
        'old_id': None,
        'deb_pkg': 'dbeaver-ce'
    },
    'gitkraken': {
        'name': 'GitKracken',
        'version': '6.6.0',
        'icon': 'gitkraken',
        'id': 'com.axosoft.GitKraken',
        'old_id': None,
        'deb_pkg': 'gitkraken'
    },
    'keepassxc': {
        'name': 'KeePassXC',
        'version': '2.5.4',
        'icon': 'keepassxc',
        'id': 'org.keepassxc.KeePassXC',
        'old_id': None,
        'deb_pkg': 'keepassxc'
    },
    'mattermost': {
        'name': 'Mattermost',
        'version': '4.4.1',
        'icon': 'mattermost-desktop',
        'id': 'com.mattermost.Desktop',
        'old_id': None,
        'deb_pkg': 'mattermost-desktop'
    },
    'signal': {
        'name': 'Signal',
        'version': '1.33.4',
        'icon': 'signal-desktop',
        'id': 'org.signal.Signal',
        'old_id': None,
        'deb_pkg': 'signal-desktop'
    },
    'spotify': {
        'name': 'Spotify',
        'version': '1.1.26.501',
        'icon': 'spotify-client',
        'id': 'com.spotify.Client',
        'old_id': None,
        'deb_pkg': 'spotify-client'
    },
    'wire': {
        'name': 'Wire',
        'version': '3.17.2924',
        'icon': 'wire-desktop',
        'id': 'com.wire.WireDesktop',
        'old_id': None,
        'deb_pkg': 'wire-desktop'
    },
}

def run():
    app = Notification(APPS)
    app.run()

def run_window():
    app = Application(APPS)
    app.run()

def run_check():
    app = Application(APPS)
    installed_pkgs = []
    
    for package in app.get_installed_packages():
        installed_pkgs.append(package)
    
    output_text = 'No installed Debian packages are depcrecated by Pop!_OS.'
    output = False
    if installed_pkgs:
        output = True
        output_text = (
            'The following Debian packages have been deprecated by Pop!_OS. '
            'Please install the corresponding Flatpaks and remove the deprecated '
            'Debian packages:\n'
        )
        for package in installed_pkgs:
            output_text += f'    {package.name}: {package.deb_package} is now {package.app_id}\n'
    
    return (output, output_text)
