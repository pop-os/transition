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

pop-transition - Headerbar Module
"""

import gettext
from gi.repository import Gtk

_ = gettext.gettext

class Headerbar(Gtk.HeaderBar):
    """Pop transition header bar."""

    def __init__(self):
        super().__init__()

        self.set_title(_('Transition to Flatpak'))
        
        # Left side
        self.cancel_button = Gtk.Button.new_with_label(_('Cancel'))

        self.left_button_stack = Gtk.Stack()
        self.pack_start(self.left_button_stack)
        self.left_button_stack.add_named(self.cancel_button, 'cancel')
        
        self.left_button_stack.set_visible_child_name('cancel')
        
        # Right side
        self.install_button = Gtk.Button.new_with_label(_('Install'))
        Gtk.StyleContext.add_class(self.install_button.get_style_context(),
                                   'suggested-action')

        self.continue_button = Gtk.Button.new_with_label(_('Continue'))
        Gtk.StyleContext.add_class(self.continue_button.get_style_context(),
                                   'suggested-action')
        
        self.remove_button = Gtk.Button.new_with_label(_('Remove'))
        Gtk.StyleContext.add_class(self.remove_button.get_style_context(),
                                   'destructive-action')
        
        self.close_button = Gtk.Button.new_with_label(_('Close'))

        self.right_button_stack = Gtk.Stack()
        self.pack_end(self.right_button_stack)
        self.right_button_stack.add_named(self.install_button, 'install')
        self.right_button_stack.add_named(self.continue_button, 'continue')
        self.right_button_stack.add_named(self.remove_button, 'remove')
        self.right_button_stack.add_named(self.close_button, 'close')

        self.right_button_stack.set_visible_child_name('install')
    
    def set_left_button(self, name):
        """ Sets the button on the left-hand side of the headerbar.

        Arguments:
            name (str): The name of the button to set (`dismiss`, `cancel`)
        
        Returns:
            The Gtk.Button that was set
        """
        if name in ['cancel']:
            self.left_button_stack.set_visible_child_name(name)
            button = self.left_button_stack.get_visible_child()
            return button
        else:
            raise Exception(
                f'{name} is not a valid child of window.headerbar.'
                'left_button_stack. Please choose "cancel".'
            )
    
    def set_right_button(self, name):
        """ Sets the button on the right-hand side of the headerbar.

        Arguments:
            name (str): The name of the button to set (`install`, `continue`, `close`)
        
        Returns:
            The Gtk.Button that was set
        """
        if name in ['install', 'continue', 'remove', 'close']:
            self.right_button_stack.set_visible_child_name(name)
            button = self.right_button_stack.get_visible_child()
            return button
        else:
            raise Exception(
                f'{name} is not a valid child of window.headerbar.'
                'right_button_stack. Please choose from "install", "continue", '
                '"remove", or "close".'
            )
