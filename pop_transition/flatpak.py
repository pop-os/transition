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
            except:
                idle_add(package.stop_spinner)
                idle_add(package.set_status_text, 'Already Installed')
        
        idle_add(self.window.show_apt_remove)
