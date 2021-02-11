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

pop-transition - APT interface module.
"""
import time

import dbus

from apt.cache import Cache
import apt_pkg
from gi.repository.GObject import idle_add
from threading import Thread

CACHE = Cache()
bus = dbus.SystemBus()
privileged_object = bus.get_object('org.pop_os.transition_system', '/PopTransition')

def get_privileged_object():
    global privileged_object
    return privileged_object

def get_cache():
    """ Returns the currently-open apt.cache.Cache object."""
    global CACHE
    return CACHE

def update_cache():
    """ Replaces the current CACHE with a new one.

    This is required because using cache.open() or cache.update() requires
    root permissions, which we don't have. Not using this is fine for the
    unprivileged side of the code because we aren't making any changes, only
    reading state. But there may be changes happening behind the scenes, so we
    want a way to get a current cache.
    
    Returns:
        The new apt.cache.Cache object.
    """
    global CACHE
    CACHE = Cache()
    return CACHE

def remove_debs(remove_debs, window):
    remove_thread = RemoveThread(remove_debs, window)
    remove_thread.start()

class RemoveThread(Thread):
    def __init__(self, packages, window):
        super().__init__()
        self.window = window
        self.packages = packages
    
    def run(self):
        pkg_list = []
        success = []

        for package in self.packages:
            pkg_list.append(package.deb_package)
            idle_add(package.set_status_text, 'Waiting')

        print(f'Removing debs: {pkg_list}')

        # Keep trying to obtain a lock and remove the packages
        while True:
            idle_add(
                self.packages[0].set_status_text,
                'Waiting for the package system lock'
            )
            lock = privileged_object.obtain_lock()
            if lock:
                break
            print('Could not obtain lock, trying again in 5 seconds')
            time.sleep(5)
        
        privileged_object.open_cache()
        
        for package in self.packages:
            idle_add(package.set_status_text, f'Removing {package.deb_package}')
            removed = privileged_object.remove_package(package.deb_package)
            if removed:
                success.append(removed)
        
        try:
            privileged_object.commit_changes()
        except:
            success = []
        privileged_object.close_cache()

        # Don't exit until the lock is released.
        while True:
            try:
                idle_add(
                    self.packages[0].set_status_text,
                    'Releasing Package Manager Lock'
                )
                unlock = privileged_object.release_lock()
                if unlock:
                    break
            except:
                continue
                
        # idle_add(self.window.quit_app)
        for package in self.packages:
            if package.deb_package in success:
                idle_add(package.set_removed, True)
        
        idle_add(self.window.show_summary_page)

