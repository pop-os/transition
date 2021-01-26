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
from threading import Thread

import gettext
from gi.repository import Flatpak, Gio, GLib, Gtk, Pango
from . import flatpak

_ = gettext.gettext
FLATPAKREPO_URL = 'https://flathub.org/repo/flathub.flatpakrepo'

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

        self.flathub_remote = None
        
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(main_window)

        self.content_area = self.get_content_area()
        self.content_area.set_orientation(Gtk.Orientation.VERTICAL)
        
        self.content_grid = Gtk.Grid()
        self.content_grid.set_row_spacing(12)
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
        
        self.show_all()

        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.status_box.set_visible(False)
        self.status_box.set_margin_top(24)
        self.status_box.set_margin_bottom(12)
        self.content_area.add(self.status_box)

        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.END)
        self.spinner.start()
        self.spinner.show()
        self.status_box.pack_start(self.spinner, True, True, 6)
        
        self.status = Gtk.Label.new('')
        self.status.set_line_wrap(True)
        self.status.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.status.set_halign(Gtk.Align.START)
        self.status.set_max_width_chars(40)
        self.status.show()
        self.status_box.pack_start(self.status, True, True, 6)

        self.ok_button = self.get_widget_for_response(Gtk.ResponseType.OK)
        Gtk.StyleContext.add_class(
            self.ok_button.get_style_context(),
            'suggested-action'
        )

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
        self.ok_button.connect('clicked', self.fix_missing)
        status = _('Adding flathub from {}').format(FLATPAKREPO_URL)
        self.status.set_text(status)

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
            'settings, although it is recommended to leave it enabled to allow '
            'for future updates.'
        )
        self.message.set_text(message_text)
        self.status.set_text(_('Enabling Flathub'))
        self.ok_button.set_label(_('Enable Flathub'))
        self.ok_button.connect('clicked', self.fix_disabled)
    
    def fix_missing(self, button):
        """ Add a missing Flathub remote to the user installation. """
        self.show_all()

        # We do this in a thread because we don't know how long it will take 
        # to download the flatpakrepo file or how long it will take to save to
        # the disk. This prevents the GUI from locking up. 
        add_thread = AddThread(self, FLATPAKREPO_URL)
        self.spinner.start()
        self.set_sensitive(False)
        add_thread.start()
    
    def fix_disabled(self, button):
        """ Enabling a disabled Flathub remote on the user installation."""
        self.show_all()
        self.spinner.start()
        flathub_remote = flatpak.get_flathub_remote()
        user_installation = flatpak.get_user_installation()
        flathub_remote.set_disabled(False)
        user_installation.modify_remote(flathub_remote)


class AddThread(Thread):

    def __init__(self, dialog, url):
        super().__init__()
        self.dialog = dialog
        self.url = url

    def run(self):
        installation = flatpak.get_user_installation()
        repofile = Gio.File.new_for_uri(self.url)
        try:
            a, contents, b = repofile.load_contents()
            repodata = GLib.Bytes.new(contents)
            
            new_remote = Flatpak.Remote.new_from_file('flathub', repodata)
            installation.add_remote(new_remote, True, None)
        
        except GLib.Error as e:
            contents = None
        
        GLib.idle_add(self.dialog.spinner.stop)
        GLib.idle_add(self.dialog.set_sensitive, True)
