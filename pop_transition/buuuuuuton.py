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

pop-transition - Dismiss notifications button.
"""

import gettext

from gi.repository import Gtk

_ = gettext.gettext

class Buuuuuutton(Gtk.Button):

    dismiss_label = _('Dismiss all notifications')
    show_label = _('Show notifications')

    def __init__(self):
        super().__init__()

        self.set_dismiss()

    def set_show(self):
        self.set_label(self.show_label)
    
    def set_dismiss(self):
        self.set_label(self.dismiss_label)
