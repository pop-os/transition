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

from logging import getLogger
import time

import dbus

from apt.cache import Cache
import apt_pkg
from gi.repository.GLib import idle_add
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
        self.log = getLogger('pop-transition.apt')
        self.window = window
        self.packages = packages
        self.success:list = []
        self.cache_open:bool = False
    
    def run(self):
        pkg_list = []

        for package in self.packages:
            pkg_list.append(package.deb_package)
            idle_add(package.set_status_text, 'Waiting')

        self.log.info(f'Removing debs: {pkg_list}')

        # Keep trying to obtain a lock and remove the packages
        count:int = 0
        while True:
            self.log.info('Waiting for package manager lock')
            idle_add(
                self.packages[0].set_status_text,
                'Waiting for the package system lock'
            )
            lock, error = self.lock_cache()
            self.log.debug('Lock: %s; Error: %s', lock, error)
            if lock:
                break
            if count >= 2: # Insist on password entry 3 times, then error out
                self.log.error('Could not open package cache: Permission Denied')
                idle_add(
                    self.window.show_error,
                    'Packages could not be removed',
                    error
                )
                self.cache_open = False
                idle_add(self.window.show_summary_page)
                return
            if error:
                count += 1
                time.sleep(.5)
                continue
            self.log.warning('Could not obtain lock, trying again in 5 seconds')
            time.sleep(5)
        
        # Most of the following code is contained within try-except blocks 
        # because we need to be 100% sure that we release the package manager
        # lock at the end of the process, so we cannot allow a failure from the
        # package system to propagate outwards and prevent release of the lock.
        # debugging information can be obtained by running the dbus service from 
        # a root terminal and observing the output. 
        self.open_cache()

        if self.cache_open:
            self.mark()
        
        if self.cache_open and self.success:
            self.commit()
        
        if self.cache_open:
            self.close()

        # Don't exit until the lock is released.
        self.release()
                
        # idle_add(self.window.quit_app)
        for package in self.packages:
            if package.deb_package in self.success:
                idle_add(package.set_removed, True)
        
        idle_add(self.window.show_summary_page)
    
    def lock_cache(self) -> tuple:
        err = None
        lock = False
        try:
            lock:bool = privileged_object.obtain_lock()
        except dbus.exceptions.DBusException as e:
            if 'org.pop_os.transition_system.PermissionDeniedByPolicy' in str(e):
                err = e
        except Exception as e:
            pass

        return (lock, err)


    def open_cache(self):
        try:
            self.log.info('Opening cache')
            privileged_object.open_cache()
            self.cache_open = True
        except Exception as exc:
            self.log.error('Could not open package cache: %s', exc)
            idle_add(
                self.window.show_error,
                'Packages could not be removed',
                exc
            )
            self.cache_open = False
    
    def mark(self):
        try:
            for package in self.packages:
                self.log.info(f'Removing {package.deb_package}')
                idle_add(package.set_status_text, f'Removing {package.deb_package}')
                removed = privileged_object.remove_package(package.deb_package)
                if removed:
                    self.log.info(f'Marked {removed} removed.')
                    self.success.append(removed)
        except Exception as e:
            self.log.error('Could not mark packages for removal: %s', e)
            idle_add(
                self.window.show_error,
                'Packages could not be removed',
                str(e)
            )
            self.success = []
    
    def commit(self):
        self.log.info('Committing changes to the package system')
        try:
            privileged_object.commit_changes()
        except Exception as e:
            self.log.error('Could not commit changes!')
            idle_add(
                self.window.show_error,
                'Packages could not be removed',
                str(e)
            )
            self.success = []

    def close(self):
        try:
            privileged_object.close_cache()
            self.cache_open = False
        except Exception as e:
            self.log.error('Could not close the package cache')
            idle_add(
                self.window.show_error,
                'Package system error',
                str(e)
            )

    def release(self):
        while True:
            try:
                self.log.info('Releasing package manager lock')
                idle_add(
                    self.packages[0].set_status_text,
                    'Releasing Package Manager Lock'
                )
                unlock = privileged_object.release_lock()
                if unlock:
                    break
            except Exception as e:
                self.log.warning(e)
                continue

