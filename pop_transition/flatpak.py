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
from gi.repository.Flatpak import RefKind
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
        print('Installing Flatpaks...')
        for package in self.packages:
            print(f'Installing {package.name} flatpak {package.app_id}.')
            try:
                self.user.install(
                    self.flathub.get_name(),
                    RefKind.APP,
                    package.app_id,
                    None,
                    'stable'
                )
                idle_add(package.stop_spinner)
                idle_add(package.set_status_text, 'Flatpak Installed')
                idle_add(package.set_installed_status, 'Installed')
            except:
                idle_add(package.stop_spinner)
                idle_add(package.set_status_text, 'Already Installed')
                idle_add(package.set_installed_status, 'Already Installed')
        
        idle_add(self.window.show_apt_remove)
