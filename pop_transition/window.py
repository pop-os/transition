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

from . import dismissal
from .headerbar import Headerbar
from .list import List
from .buuuuuuton import Buuuuuutton

_ = gettext.gettext

class Window(Gtk.ApplicationWindow):
    """ Window for the pop-transition."""

    @staticmethod
    def new(application):
        return Gtk.ApplicationWindow.new(application)
    
    def __init__(self, app):
        super().__init__(application=app)

        self.app = app
        
        self.set_default_size(500, 550)
        self.set_resizable(False)
        
        self.headerbar = Headerbar()
        self.set_titlebar(self.headerbar)

        self.content = Gtk.Stack()
        self.content.set_transition_type(Gtk.StackTransitionType.OVER_LEFT)
        self.content.set_transition_duration(200)
        self.content.props.margin = 24
        self.add(self.content)

        first_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        self.content.add_named(first_page, 'first_page')

        self.description_label = Gtk.Label.new(
            _(
                'Please reinstall the following applications to ensure your '
                'software stays up-to-date. First, install the Flatpak versions '
                'of these applications, as the Debian packages will no longer '
                'receive updates. Then you will be able to remove the Debian '
                'packages.'
            )
        )
        self.description_label.set_line_wrap(True)
        self.description_label.set_halign(Gtk.Align.START)
        self.description_label.set_max_width_chars(54)
        self.description_label.set_xalign(0)
        first_page.add(self.description_label)

        self.backup_label = Gtk.Label.new(
            _(
                'To ensure the smoothest transition, back up or '
                'export your application data and configurations before '
                'installing the Flatpak packages.'
            )
        )
        self.backup_label.set_line_wrap(True)
        self.backup_label.set_halign(Gtk.Align.START)
        self.backup_label.set_max_width_chars(54)
        self.backup_label.set_xalign(0)
        first_page.add(self.backup_label)

        self.app_list = List()
        first_page.add(self.app_list)

        self.dismiss_button = Buuuuuutton()
        first_page.add(self.dismiss_button)
        
        # Summary page
        summary_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        self.content.add_named(summary_page, 'summary')

        summary_label = Gtk.Label.new(
            _(
                'The following actions have been performed:'
            )
        )
        summary_page.add(summary_label)

        summary_scroll = Gtk.ScrolledWindow()
        summary_scroll.set_vexpand(True)
        summary_page.add(summary_scroll)

        self.summary_view = Gtk.TextView()
        summary_scroll.add(self.summary_view)

        # Change thje text is case the notifications are already hidden
        if dismissal.is_dismissed():
            self.dismiss_button.set_show()

        self.content.set_visible_child_name('first_page')
        self.show_all()
    
    def set_buttons_sensitive(self, sensitive):
        """ Sets the buttons in the GUI to be either sensitive or insensitive.

        Arguments:
            sensitive (bool): Whether or not the buttons should be sensitive.
        """
        self.dismiss_button.set_sensitive(sensitive)
        self.headerbar.left_button_stack.set_sensitive(sensitive)
        self.headerbar.right_button_stack.set_sensitive(sensitive)
        self.app_list.select_all_check.set_sensitive(sensitive)
        
        for package in self.app_list.packages:
            package.checkbox.set_sensitive(sensitive)
        
    def quit_app(self):
        self.app.quit()
    
    def set_summary_text(self):
        buffer = self.summary_view.get_buffer()
        summary_text = _('The following Flatpaks were installed:\n')

        for package in self.app_list.packages:
            if package.installed_status == 'Installed':
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.app_id})\n'
            
            if package.installed_status == 'Already Installed':
                # Translators: Do not translate this string
                summary_text += f'    {package.name}'
                summary_text += ' Already Installed\n'
        
        summary_text += _('\nThe following Debian packages were removed:\n')
        for package in self.app_list.packages:
            if package.removed:
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.deb_package})\n'
        
        buffer.set_text(summary_text)
    
    def show_summary(self):
        self.content.set_visible_child_name('summary')
        self.headerbar.left_button_stack.hide()
        self.headerbar.set_right_button('close')
        self.set_summary_text()
        self.set_buttons_sensitive(True)
    
    def show_apt_remove(self):
        """ Change the GUI into Apt removal mode."""
        self.backup_label.hide()
        self.description_label.set_text(
            _(
                'The following Debian packages can be removed. Please note that '
                'removing the packages will uninstall them from all user '
                'accounts. Other users will have to manually reinstall the '
                'applications from Pop Shop.'
            )
        )
        self.headerbar.set_right_button('remove')
        self.headerbar.set_left_button('cancel')
        self.set_buttons_sensitive(True)
        self.app_list.select_all_check.set_sensitive(True)
