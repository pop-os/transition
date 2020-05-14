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

pop-transition - Headerbar Module
"""

import gettext
from gi.repository import Gtk

_ = gettext.gettext

class Headerbar(Gtk.HeaderBar):
    """Pop transition header bar."""

    def __init__(self, app):
        self.app = app
        super().__init__()

        self.set_title(_('Transition to Flatpak'))
        
        # Left side
        self.dismiss_button = Gtk.Button.new_with_label(_('Dismiss'))

        self.cancel_button = Gtk.Button.new_with_label(_('Cancel'))

        self.left_button_stack = Gtk.Stack()
        self.pack_start(self.left_button_stack)
        self.left_button_stack.add_named(self.dismiss_button, 'dismiss')
        self.left_button_stack.add_named(self.cancel_button, 'cancel')
        
        self.left_button_stack.set_visible_child_name('dismiss')
        
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
        if name in ['dismiss', 'cancel']:
            self.left_button_stack.set_visible_child_name(name)
            button = self.left_button_stack.get_visible_child()
            return button
        else:
            raise Exception(
                f'{name} is not a valid child of window.headerbar.'
                'left_button_stack. Please choose from "dismiss" or "cancel".'
            )
    
    def set_right_button(self, name):
        """ Sets the button on the right-hand side of the headerbar.

        Arguments:
            name (str): The name of the button to set (`install`, `continue`, `close`)
        
        Returns:
            The Gtk.Button that was set
        """
        if name in ['install', 'continue', 'remove', 'cancel']:
            self.right_button_stack.set_visible_child_name(name)
            button = self.right_button_stack.get_visible_child()
            return button
        else:
            raise Exception(
                f'{name} is not a valid child of window.headerbar.'
                'right_button_stack. Please choose from "install", "continue", '
                '"remove", or "close".'
            )
