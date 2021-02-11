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

pop-transition - High-permission service
"""

import dbus
import dbus.service
import dbus.mainloop.glib
import sys
import time
import os

from apt.cache import Cache, LockFailedException
import apt_pkg
from gi.repository import GLib, GObject

class TransitionException(dbus.DBusException):
    _dbus_error_name = 'org.pop_os.transition_system.TransitionException'

class PermissionDeniedByPolicy(dbus.DBusException):
    _dbus_error_name = 'org.pop_os.transition_system.PermissionDeniedByPolicy'

class Transition(dbus.service.Object):
    def __init__(self, conn=None, object_path=None, bus_name=None):
        super().__init__(conn, object_path, bus_name)

        self.dbus_info = None
        self.polkit = None
        self.enforce_polkit = True
        self.cache = Cache()
        self.lock = None
    
    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='b',
        sender_keyword='sender', connection_keyword='conn'
    )
    def obtain_lock(self, sender=None, conn=None):
        """ Lock the package system. """
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print('Obtaining Package manager lock')
        try:
            self.lock = apt_pkg.get_lock('/var/lib/dpkg/lock-frontend', True)
            return True
        except apt_pkg.Error:
            return False
    
    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='b',
        sender_keyword='sender', connection_keyword='conn'
    )
    def release_lock(self, sender=None, conn=None):
        """ Unlock the package system. """
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print('Releasing package manager lock')
        try:
            os.close(self.lock)
            return True
        except:
            return False
    
    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='b',
        sender_keyword='sender', connection_keyword='conn'
    )
    def open_cache(self, sender=None, conn=None):
        """ Lock the package system. """
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print('Opening package cache')
        self.cache.update()
        self.cache.open()
        return True
    
    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='b',
        sender_keyword='sender', connection_keyword='conn'
    )
    def commit_changes(self, sender=None, conn=None):
        """ Lock the package system. """
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print('Committing changes to cache')
        self.cache.commit()
        return True
    
    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='b',
        sender_keyword='sender', connection_keyword='conn'
    )
    def close_cache(self, sender=None, conn=None):
        """ Lock the package system. """
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print('Closing package cache')
        self.cache.close()
        return True

    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='s', out_signature='s',
        sender_keyword='sender', connection_keyword='conn'
    )
    def remove_package(self, package, sender=None, conn=None):
        """ Mark a package for removal."""
        self._check_polkit_privilege(
            sender, conn, 'org.pop_os.transition_system.removedebs'
        )
        print(f'Marking {package} for removal')
        try:
            pkg = self.cache[package]
            pkg.mark_delete()
            return pkg.name
        except:
            print(f'Could not mark {package} for removal')
            return ''

    @dbus.service.method(
        'org.pop_os.transition_system.Interface', 
        in_signature='', out_signature='',
        sender_keyword='sender', connection_keyword='conn'
    )
    def exit(self, sender=None, conn=None):
        mainloop.quit()

    def _check_polkit_privilege(self, sender, conn, privilege):
        '''Verify that sender has a given PolicyKit privilege.
        sender is the sender's (private) D-BUS name, such as ":1:42"
        (sender_keyword in @dbus.service.methods). conn is
        the dbus.Connection object (connection_keyword in
        @dbus.service.methods). privilege is the PolicyKit privilege string.
        This method returns if the caller is privileged, and otherwise throws a
        PermissionDeniedByPolicy exception.
        '''

        if sender is None and conn is None:
            # Called locally, not through D-Bus
            return
        
        if not self.enforce_polkit:
            # For testing
            return
        
        if self.dbus_info is None:
            self.dbus_info = dbus.Interface(conn.get_object('org.freedesktop.DBus',
                '/org/freedesktop/DBus/Bus', False), 'org.freedesktop.DBus')
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)
        
        if self.polkit is None:
            self.polkit = dbus.Interface(dbus.SystemBus().get_object(
                'org.freedesktop.PolicyKit1',
                '/org/freedesktop/PolicyKit1/Authority', False),
                'org.freedesktop.PolicyKit1.Authority'
            )
        
        try:
            (is_auth, _, details) = self.polkit.CheckAuthorization(
                ('unix-process', {'pid': dbus.UInt32(pid, variant_level=1),
                'start-time': dbus.UInt64(0, variant_level=1)}), 
                privilege, {'': ''}, dbus.UInt32(1), '', timeout=600
            )

        except dbus.DBusException as e:
            if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
                # polkitd timed out, connect again
                self.polkit = None
                return self._check_polkit_privilege(sender, conn, privilege)
            else:
                raise
        
        if not is_auth:
            raise PermissionDeniedByPolicy(privilege)

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    name = dbus.service.BusName('org.pop_os.transition_system', bus)
    object = Transition(bus, '/PopTransition')
    mainloop = GObject.MainLoop()

    mainloop.run()