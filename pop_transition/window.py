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
import traceback

from gi.repository import Gtk, Gio

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

        # Change the text is case the notifications are already hidden
        if dismissal.is_dismissed():
            self.dismiss_button.set_show()

        for button in [self.headerbar.continue_button, self.headerbar.back_button]:
            button.connect('clicked', self.move_pages)

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
    
    def show_error(self, title:str, exception:Exception) -> None:
        """Show an error dialog"""
        self.error = ErrorDialog(self, title, exception)
        message_text = traceback.format_exception_only(exception)[0].strip()
        print(message_text)
        self.error.dialog_message.set_markup(
            self.parse_errors(message_text, self.error)
        )
        self.error.run()
        self.error.destroy()
    
    def parse_errors(self, message:str, dialog:Gtk.Dialog):
        """Looks through an error message and tries to translate it into a
        more user-friendly form.
        
        Should help provide users with enough info to actually fix a problem.
        """

        message_translated = message

        message_list = message.split('\n')
        for line in message_list:
            if 'does not have a Release file' in line: # discontinued repo
                line_list = line.split("'")
                repo: str = line_list[1]
                message_translated = 'The repository '
                message_translated += repo
                message_translated += (
                    ' appears to no longer be valid, and removal cannot continue. Please '
                    'remove the repository from the System Software Sources, then '
                    'try again.'
                )
                dialog.add_repos_button()
                break
            
            if 'org.pop_os.transition_system.PermissionDeniedByPolicy' in line:
                message_translated = (
                    'Administrator privileges are required to remove old Debian '
                    'packages from the system.'
                )
                dialog.expander.hide()
                break
        
        return message_translated
                    
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
        app_counter = 0

        summary_text = _('The following Flatpaks were installed:\n')
        for package in self.app_list.packages:
            if package.installed_status == 'installed':
                app_counter += 1
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.app_id})\n'
            
            if package.installed_status == 'already installed':
                app_counter += 1
                # Translators: Do not translate this string
                summary_text += f'    {package.name}'
                summary_text += _(' Already Installed\n')
        
        if app_counter == 0:
            summary_text += 'None\n'
        
        app_counter = 0
        
        summary_text += _('\nThe following Debian packages were removed:\n')
        for package in self.app_list.packages:
            if package.removed:
                app_counter += 1
                # Translators: Do not translate this string
                summary_text += f'    {package.name} ({package.deb_package})\n'

        if app_counter == 0:
            summary_text += 'None\n'
        
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

class ErrorDialog(Gtk.Dialog):
    def __init__(self, 
                 window: Gtk.Window, 
                 message_title: str,
                 exception: Exception) -> None:

        super().__init__(use_header_bar=True, modal=1)
        self.set_deletable(False)
        self.set_transient_for(window)

        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.OK)

        content_area = self.get_content_area()

        self.set_size_request(650, 100)

        self.content_grid = Gtk.Grid()
        self.content_grid.set_margin_top(24)
        self.content_grid.set_margin_left(24)
        self.content_grid.set_margin_right(24)
        self.content_grid.set_margin_bottom(24)
        self.content_grid.set_column_spacing(36)
        self.content_grid.set_row_spacing(12)
        content_area.add(self.content_grid)

        error_image = Gtk.Image.new_from_icon_name(
            'dialog-warning-symbolic',
            Gtk.IconSize.DIALOG
        )
        self.content_grid.attach(error_image, 0, 0, 1, 2)

        dialog_label = Gtk.Label()
        dialog_label.set_markup(f'<b>{message_title}</b>')
        self.content_grid.attach(dialog_label, 1, 0, 1, 1)

        self.dialog_message = Gtk.Label.new('message_text')
        self.dialog_message.set_line_wrap(True)
        self.dialog_message.set_width_chars(1)
        self.content_grid.attach(self.dialog_message, 1, 1, 1, 1)

        self.expander = Gtk.Expander.new('Error details:')
        self.content_grid.attach(self.expander, 0, 3, 2, 1)

        traceback_scroll = Gtk.ScrolledWindow()
        traceback_scroll.set_vexpand(True)
        traceback_scroll.set_hexpand(True)
        traceback_scroll.set_size_request(-1, 200)
        self.expander.add(traceback_scroll)

        traceback_label = Gtk.TextView.new()
        traceback_text = traceback_label.get_buffer()
        traceback_text.set_text('\n'.join(traceback.format_exception(exception)))
        traceback_scroll.add(traceback_label)

        self.show_all()
    
    def add_repos_button(self) -> None:
        repoman_app = None
        all_apps = Gio.AppInfo.get_all()
        for app in all_apps:
            if app.get_name() == 'Repoman':
                repoman_app = app
                break
        print(repoman_app.get_name())
        if repoman_app:
            repoman_button = Gtk.Button.new_with_label(
                _('Open Software Sources')
            )
            repoman_button.connect('clicked', self.launch_repoman, repoman_app)
            print(repoman_button)
            self.content_grid.attach(repoman_button, 1, 2, 1, 1)
            repoman_button.show()
    
    def launch_repoman(self, button, repoman_app):
        repoman_app.launch()
