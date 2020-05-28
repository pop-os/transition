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

pop-transition - Widget to display a list of applications to transition.
"""

import gettext

from gi.repository import Gtk

_ = gettext.gettext

class List(Gtk.Box):
    """ Displays a list of applications that need to be transitioned."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.select_all_check = Gtk.CheckButton.new_with_label(_('Select all'))
        self.select_all_check.connect('toggled', self.on_select_all_toggled)
        self.add(self.select_all_check)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.add(scrolled)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.listbox)

        self.packages = []
    
    def on_select_all_toggled(self, button, data=None):
        state = self.select_all_check.get_active()
        for i in self.packages:
            i.checkbox.set_active(state)
    
    def add_package(self, package):
        """ Adds an application object to the list.

        Arguments: 
            package (package): The package to add.
        """
        self.listbox.add(package)
        self.packages.append(package)
    