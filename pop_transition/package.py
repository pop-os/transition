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

pop-transition - Packages displayed within the list.
"""

import gettext

from gi.repository import Gtk, GdkPixbuf

_ = gettext.gettext

class Package(Gtk.Grid):
    """ A special class to represent packages within the list.

    This lets us perform actions more easily.
    """

    def __init__(self):
        
        super().__init__()

        self.props.margin = 6
        self.set_column_spacing(12)
        self.set_row_spacing(6)
        self.set_hexpand(True)

        self.checkbox = Gtk.CheckButton()
        self.attach(self.checkbox, 0, 0, 1, 2)

        self.icon_image = Gtk.Image()
        self.attach(self.icon_image, 1, 0, 1, 2)

        self.name_label = Gtk.Label()
        self.name_label.set_valign(Gtk.Align.END)
        self.name_label.set_yalign(1)
        self.name_label.set_xalign(0)
        self.attach(self.name_label, 2, 0, 3, 1)

        self.source_label = Gtk.Label()
        Gtk.StyleContext.add_class(self.source_label.get_style_context(), 'dim-label')
        self.source_label.set_halign(Gtk.Align.START)
        self.source_label.set_valign(Gtk.Align.START)
        self.source_label.set_yalign(0)
        self.attach(self.source_label, 2, 1, 1, 1)

        # FIXME: This won't work because AppStream segfaults when getting 
        # Components. Consider re-adding later.
        # dash = Gtk.Label.new('-')
        # Gtk.StyleContext.add_class(dash.get_style_context(), 'dim-label')
        # dash.set_valign(Gtk.Align.START)
        # dash.set_yalign(0)
        # self.attach(dash, 3, 1, 1, 1)
        #
        # self.version_label = Gtk.Label()
        # Gtk.StyleContext.add_class(self.version_label.get_style_context(), 'dim-label')
        # self.version_label.set_valign(Gtk.Align.START)
        # self.version_label.set_yalign(0)
        # self.attach(self.version_label, 2, 1, 1, 1)

        self.spinner = Gtk.Spinner()
        self.spinner.set_halign(Gtk.Align.END)
        self.spinner.set_hexpand(True)
        self.attach(self.spinner, 5, 0, 1, 2)

        self.source = 'Flathub'

    @property
    def name(self):
        """ str: The name of the application. """
        return self.name_label.get_text()
    
    @name.setter
    def name(self, name):
        self.name_label.set_text(name)
    
    # @property
    # def version(self):
    #     """ str: The version of the app."""
    #     return self.version_label.get_text()
    
    # @version.setter
    # def version(self, version):
        # self.version_label.set_text(version)
    
    @property
    def icon(self):
        return self.icon_image.get_icon_name()
    
    @icon.setter
    def icon(self, icon):
        if not icon.startswith('/'):
            self.icon_image.set_from_icon_name(icon, Gtk.IconSize.DND)
        else:
            pxbf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, 32, 32)
            self.icon_image.set_from_pixbuf(pxbf)
    
    @property
    def source(self):
        return self.source_label.get_text()
    
    @source.setter
    def source(self, source):
        self.source_label.set_text(source)
    
    @property
    def app_id(self):
        """ str: The RDNN App ID that we're installing as a replacement."""
        return self._app_id
    
    @app_id.setter
    def app_id(self, id):
        self._app_id = id
    
    @property
    def old_app_id(self):
        """ str: The App ID used by the old package

        If this is the same as the new one, then return the new one instead.
        """
        try:
            return self._old_app_id
        
        except AttributeError:
            return self.app_id
    
    @old_app_id.setter
    def old_app_id(self, id):
        self._old_app_id = id
    
    @property
    def deb_package(self):
        """ str: The name of the Debian package."""
        return self._deb_name
    
    @deb_package.setter
    def deb_package(self, deb):
        self._deb_name = deb
    