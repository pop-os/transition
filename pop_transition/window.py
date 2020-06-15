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
        self.pages = ['flatpak', 'apt', 'summary']
        
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
        self.description_label.set_max_width_chars(66)
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
        self.backup_label.set_max_width_chars(66)
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

        for button in [self.headerbar.continue_button, self.headerbar.back_button]:
            button.connect('clicked', self.move_pages)
        
        for package in self.app_list.packages:
            package.checkbox.connect('toggled', self.set_visible_buttons)

        self.content.set_visible_child_name('first_page')
        self.show_all()
        self.current_page = 'flatpak'
    
    @property
    def current_page(self):
        """str: the currently active page."""
        return self._current_page
    
    @current_page.setter
    def current_page(self, page):
        """ We need to set the GUI up correctly."""
        pages = {
            'apt': self.show_apt_page,
            'flatpak': self.show_flatpak_page,
            'summary': self.show_summary_page
        }
        pages[page]()
    
    def move_pages(self, button):
        """ Move to the next or previous page."""
        current_index = self.pages.index(self.current_page)
        
        if button is self.headerbar.continue_button:
            self.current_page = self.pages[current_index + 1]
        
        elif button is self.headerbar.back_button:
            self.current_page = self.pages[current_index - 1]

    def set_visible_buttons(self, *args, **kwargs):
        """ Sets the correct combination of headerbar buttons.

        We need to take into account the current page we're on.
        """
        number_checked = 0
        for package in self.app_list.packages:
            if package.checkbox.get_active():
                number_checked += 1
        
        if self.current_page == 'flatpak':
            self.headerbar.left_button_stack.show()
            self.headerbar.right_button_stack.show()
            self.headerbar.set_left_button('cancel')
            
            if number_checked != 0:
                self.headerbar.set_right_button('install')
            
            else:
                self.headerbar.set_right_button('continue')
        
        elif self.current_page == 'apt':
            self.headerbar.left_button_stack.show()
            self.headerbar.right_button_stack.show()
            self.headerbar.set_left_button('back')

            if number_checked != 0:
                self.headerbar.set_right_button('remove')
            
            else:
                self.headerbar.set_right_button('continue')
        
        else:
            self.headerbar.left_button_stack.hide()
            self.headerbar.right_button_stack.show()
            self.headerbar.set_right_button('close')
    
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
            if package.installed_status == 'installed':
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.app_id})\n'
            
            if package.installed_status == 'already installed':
                # Translators: Do not translate this string
                summary_text += f'    {package.name}'
                summary_text += _(' Already Installed\n')
        
        summary_text += _('\nThe following Debian packages were removed:\n')
        for package in self.app_list.packages:
            if package.removed:
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.deb_package})\n'
        
        summary_text += '\n\n'
        for package in self.app_list.packages:
            if package.installed_status.startswith('Error'):
                summary_text += f'{package.name} {package.installed_status}\n'

        buffer.set_text(summary_text)

    def show_apt_page(self):
        """ Show the Apt page for removing Debs."""
        self.backup_label.hide()
        self.description_label.set_text(
            _(
                'The following Debian packages can be removed. Please note that '
                'removing the packages will uninstall them from all user '
                'accounts. Other users will have to manually reinstall the '
                'applications from Pop Shop.'
            )
        )
        self.set_buttons_sensitive(True)
        self.app_list.select_all_check.set_sensitive(True)

        for package in self.app_list.packages:
            package.source = "Pop!_OS Repo"
            if "Error" in package.installed_status:
                package.checkbox.set_active(False)
        
        self._current_page = 'apt'
        self.set_visible_buttons()
    
    def show_flatpak_page(self):
        """ Change the GUI into Apt removal mode."""
        self.backup_label.show()
        self.description_label.set_text(
            _(
                'Please reinstall the following applications to ensure your '
                'software stays up-to-date. First, install the Flatpak versions '
                'of these applications, as the Debian packages will no longer '
                'receive updates. Then you will be able to remove the Debian '
                'packages.'
            )
        )
        self.set_buttons_sensitive(True)
        self.app_list.select_all_check.set_sensitive(True)

        for package in self.app_list.packages:
            package.source = "Pop!_OS Repo"
            if "Error" in package.installed_status:
                package.checkbox.set_active(False)
        
        self._current_page = 'flatpak'
        self.set_visible_buttons()

    def show_summary_page(self):
        self.content.set_visible_child_name('summary')
        self.set_summary_text()
        self.set_buttons_sensitive(True)
        self._current_page = 'summary'
        self.set_visible_buttons()
