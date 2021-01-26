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

pop-transition - flatpak interface module.
"""

from threading import Thread
from gi.repository import Flatpak, GLib
from gi.repository.GObject import idle_add
from repoman import flatpak_helper

def get_flathub_remote():
    """ Finds the Flathub remote and returns it.

    This is required because a user may have changed the name of the flathub 
    remote, ergo we need to find it and match it to the URL.

    Returns:
        A Flatpak.Remote matching the flathub URL.
    """
    user = get_user_installation()
    for remote in user.list_remotes():
        if remote.get_url() == 'https://dl.flathub.org/repo/':
            return remote

def get_user_installation():
    """ Gets the default user Flatpak Installation.

    Returns:
        The Flatpak.Installation 
    """
    return flatpak_helper.get_installation_for_type('user')

def install_flatpaks(packages, window):
    """ Install a package from Flathub in user mode.

    Arguments:
        packages ([Package]): the package widgets to install.
    """
    install_thread = InstallThread(packages, window)
    install_thread.start()

class InstallThread(Thread):

    def __init__(self, packages, window):
        super().__init__()
        self.packages = packages
        self.window = window
        self.user = get_user_installation()
        self.flathub = get_flathub_remote()
    
    def run(self):
        print('Updating Appstream Data')
        # If the appstream data is out of date, it can cause problems installing
        # some applications. So we update it first.
        self.user.update_appstream_full_sync(self.flathub.get_name())

        print('Installing Flatpaks...')
        
        # We use a transaction to get error details and to install dependencies 
        transaction = Flatpak.Transaction.new_for_installation(self.user)
        transaction.connect('new_operation', self.on_new_operation)
        transaction.connect('operation-done', self.on_operation_done)
        transaction.connect('operation-error', self.on_operation_error)

        for package in self.packages:
            print(f'Installing {package.name} flatpak {package.app_id}.')
            remote_ref = self.user.fetch_remote_ref_sync(
                self.flathub.get_name(),
                Flatpak.RefKind.APP,
                package.app_id,
                None,
                'stable'
            )
            try:
                transaction.add_install(
                    self.flathub.get_name(), remote_ref.format_ref()
                )
                idle_add(package.set_status_text, 'Waiting')
            except GLib.Error as err:
                idle_add(package.stop_spinner)
                
                # Package is already installed, inform the user
                if 'is already installed' in err.message:
                    idle_add(package.set_status_text, 'Already Installed')
                    idle_add(package.set_installed_status, 'already installed')
                
                # Or there was some other error, let the user know
                else:
                    idle_add(package.set_status_text, 'Error installing')
                    idle_add(package.set_installed_status, err.message)
                
        transaction.run()
        idle_add(self.window.show_apt_page)
    
    def get_package_from_operation(self, operation):
        ref = operation.get_ref()
        ref_name = ref.split('/')[1]
        print(f'Looking for ID from ref {ref}')

        for package in self.packages:
            if ref_name == package.app_id:
                print(f'Found ID {ref_name} in package {package.name}')
                return package
    
    def on_new_operation(self, transaction, operation, progress):
        package = self.get_package_from_operation(operation)
        
        # Don't try and update UI if there is no pacakge (probably a runtime)
        if package:
            idle_add(package.start_spinner)
            idle_add(package.set_status_text, 'Installing')

    def on_operation_done(self, transaction, operation, commit, result):
        package = self.get_package_from_operation(operation)
        
        # Don't try and update UI if there is no pacakge (probably a runtime)
        if package:
            idle_add(package.stop_spinner)
            idle_add(package.set_status_text, "Flatpak installed")
            idle_add(package.set_installed_status, 'installed')
    
    def on_operation_error(self, transaction, operation, error, details):
        package = self.get_package_from_operation(operation)
        error_text = f"Error: {error.message}"
        
        # Don't try and update UI if there is no pacakge (probably a runtime)
        if package:
            idle_add(package.stop_spinner)
            idle_add(package.set_status_text, "Error installing")
            idle_add(package.set_installed_status, error_text)
