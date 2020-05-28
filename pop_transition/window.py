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

pop-transition - Window Module
"""

import gettext

from gi.repository import Gtk

from .headerbar import Headerbar
from .list import List
from .buuuuuuton import Buuuuuutton

_ = gettext.gettext

class Window(Gtk.ApplicationWindow):
    """ Window for the pop-transition."""

    def __init__(self, app=None):
        super().__init__(application=app)
        
        self.set_default_size(400, 500)
        self.set_resizable(False)
        
        self.headerbar = Headerbar(app)
        self.set_titlebar(self.headerbar)

        content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        content.props.margin = 24
        self.add(content)

        description_label = Gtk.Label.new(
            _(
                'Please reinstall the following applications to ensure your '
                'software stays up-to-date. First, install the Flatpak versions '
                'of these applications, as the Debian packages will no longer '
                'receive updates. Then you will be able to remove the Debian '
                'packages.'
            )
        )
        description_label.set_line_wrap(True)
        description_label.set_halign(Gtk.Align.START)
        description_label.set_max_width_chars(54)
        description_label.set_xalign(0)
        content.add(description_label)

        backup_label = Gtk.Label.new(
            _(
                'To ensure the smoothest transition, back up or '
                'export your application data and configurations before '
                'installing the Flatpak packages.'
            )
        )
        backup_label.set_line_wrap(True)
        backup_label.set_halign(Gtk.Align.START)
        backup_label.set_max_width_chars(54)
        backup_label.set_xalign(0)
        content.add(backup_label)

        self.app_list = List()
        content.add(self.app_list)

        self.dismiss_button = Buuuuuutton()
        content.add(self.dismiss_button)

        self.show_all()
