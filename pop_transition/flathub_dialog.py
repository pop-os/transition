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

pop-transition - dialog to add Flathub if it is missing.
"""

import gettext
from gi.repository import Gtk

_ = gettext.gettext

class FlathubDialog(Gtk.Dialog):
    """ Dialog to add Flathub if it is missing."""

    def __init__(self, main_window, *args, **kwargs):
        super().__init__(
            '',
            main_window,
            0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK),
            *args,
            modal=1,
            use_header_bar=True,
            **kwargs
        )
        
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(main_window)

        self.content_area = self.get_content_area()
        
        self.content_grid = Gtk.Grid()
        self.content_grid.set_row_spacing(6)
        self.content_grid.set_column_spacing(12)
        self.content_grid.props.margin = 12
        self.content_area.add(self.content_grid)

        self.flathub_image = Gtk.Image.new_from_file(
            '/usr/lib/pop-transition/flathub-badge.svg'
        )
        self.content_grid.attach(self.flathub_image, 0, 0, 1, 2)

        self.message_title = Gtk.Label()
        self.message_title.set_line_wrap(True)
        self.message_title.set_width_chars(40)
        self.content_grid.attach(self.message_title, 1, 0, 1, 1)

        self.message = Gtk.Label()
        self.message.set_line_wrap(True)
        self.message.set_width_chars(40)
        self.content_grid.attach(self.message, 1, 1, 1, 1)

        self.ok_button = self.get_widget_for_response(Gtk.ResponseType.OK)
        Gtk.StyleContext.add_class(
            self.ok_button.get_style_context(),
            'suggested-action'
        )

        # Future code here.

        self.show_all()

        # Testing code here.
        self.setup_for_disabled()

    def setup_for_missing(self):
        """ Set up the dialog for adding a missing Flathub remote."""
        
        # Message title
        message_title_text = _('Flahub not detected')
        self.message_title.set_markup(f'<b>{message_title_text}</b>')
        
        # Message text
        message_text = _(
            'Flathub was not detected as a flatpak remote on your system. You '
            'will need to add it to install updated applications.'
        )
        self.message.set_text(message_text)
        self.ok_button.set_label(_('Add Flathub'))

    def setup_for_disabled(self):
        """ Set up the dialog for adding a disabled Flathub remote."""
        
        # Message title
        message_title_text = _('Flahub is disabled')
        self.message_title.set_markup(f'<b>{message_title_text}</b>')
        
        # Message text
        message_text = _(
            'Flathub is currently disabled on your system. You will need to '
            'enable it to install updated applications.\n\n'
            'After installation you can re-disable Flathub from the Pop_Shop '
            'settings.'
        )
        self.message.set_text(message_text)
        self.ok_button.set_label(_('Enable Flathub'))
