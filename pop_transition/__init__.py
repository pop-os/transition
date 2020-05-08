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

pop-transition is a simple app that notifies users if they have debian versions
of packages which were transitioned to Flatpak in Pop_OS 20.04. 
"""

import gettext
import gi
import sys

gi.require_versions (
    {
        'Gdk': '3.0',
        'GdkPixbuf': '2.0',
        'Gio': '2.0',
        'Gtk': '3.0',
    }
)

from .application import Application

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
    'dbeaver': {
        'name': 'DBeaver',
        'version': '7.0.4',
        'icon': '/usr/share/dbeaver/dbeaver.png',
        'id': 'io.dbeaver.DBeaverCommunity',
        'old_id': None,
        'deb_pkg': 'dbeaver-ce'
    },
    'discord': {
        'name': 'Discord',
        'version': '0.0.10',
        'icon': 'discord',
        'id': 'com.discordapp.Discord',
        'old_id': None,
        'deb_pkg': 'discord'
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
    'lollypop': {
        'name': 'Lollypop',
        'version': '1.2.35',
        'icon': 'org.gnome.Lollypop',
        'id': 'org.gnome.Lollypop',
        'old_id': None,
        'deb_pkg': 'lollypop'
    },
    'mattermost': {
        'name': 'Mattermost',
        'version': '4.4.1',
        'icon': 'mattermost-desktop',
        'id': 'com.mattermost.Desktop',
        'old_id': None,
        'deb_pkg': 'mattermost-desktop'
    },
    'peek': {
        'name': 'Peek',
        'version': '1.5.1',
        'icon': 'com.uploadedlobster.peek',
        'id': 'com.uploadedlobster.peek',
        'old_id': None,
        'deb_pkg': 'peek'
    },
    'signal': {
        'name': 'Signal',
        'version': '1.33.4',
        'icon': 'signal-desktop',
        'id': 'org.signal.signal',
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
    app = Application(APPS)
    app.run()
