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

pop-transition - Handle user dismissal of notifications.
"""

from pathlib import Path

def get_user_home():
    """ Gets the current user home dir.

    Returns:
        The Path() for the home dir.
    """
    return Path.home()

def get_user_local():
    """ Gets the current ~/.local/share path.

    Returns:
        the Path() ~/.local/share
    """
    user_home = get_user_home()
    user_local = user_home / '.local' / 'share'
    if user_local.exists():
        return user_local
    return user_home

def get_transition_path():
    """ Gets a directory in the user local dir for storing our dismissal file.

    If the config dir is the user home folder (because ~/.local/share doesn't 
    exist), then prefix the path with a . so that it shows up hidden.
    
    Returns:
        The Path() for the transition dir
    """
    user_home = get_user_home()
    user_local = get_user_local()
    transition_dirname = 'pop-transition'
    
    # hide the folder if it's in the user home folder
    if user_local == user_home:
        transition_dirname = '.pop-transition'
    
    transition_path = user_local / transition_dirname

    # make it if it doesn't exist
    transition_path.mkdir(exist_ok=True)

    return transition_path

def dismiss_notifications():
    """ Prevent from showing future notifications

    Places a file a standardized location which will tell the application not to
    display notifications in the future.
    """
    dismiss_file = get_transition_path() / 'dismiss-notifications'
    dismiss_file.touch()

def show_notifications():
    """ Continue showing notifications.

    This undoes the actions of dismiss_notifications().
    """
    dismiss_file = get_transition_path() / 'dismiss-notifications'
    dismiss_file.unlink(missing_ok=True)

def is_dismissed():
    """ Figures out if notifications have been dismissed before.

    Returns:
        True if notifications are dismissed, else False
    """
    dismiss_file = get_transition_path() / 'dismiss-notifications'
    
    if dismiss_file.exists():
        return True
    else:
        return False
