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

pop-transition is a simple app that notifies users if they have debian versions
of packages which were transitioned to Flatpak in Pop_OS 20.04. 
"""

from distutils.core import setup
from distutils.cmd import Command
import os
import subprocess
import sys

def get_version():
    version = {}
    with open(os.path.join('pop-transition', '__version__.py')) as fp:
        exec(fp.read(), version)
    return version['__version__']

class Release(Command):
    """ Generate a release and push it to git."""
    description = "Generate a release and push it to git."

    user_options = [
        ('dry-run', None, 'Skip the actual release and do a dry run instead.'),
        ('prerelease', None, 'Release this version as a pre-release.'),
        ('skip-deb', None, 'Skip doing a debian update for this release.'),
        ('skip-git', None, 'Skip committing to git at the end.')
        ('force-version=', None, 'Force the version to update to the given value.')
    ]

    def initialize_options(self):
        self.dry_run = False
        self.prerelease = False
        self.skip_deb = False
        self.skip_git = False
        self.force_version = None
    
    def finalize_options(self):
        if self.force_version:
            if not isinstance(self.force_version, str):
                raise Exception('Please specify the test version to release')

    def run(self):
        cz_command = ['cz', 'bump']
        ch_command = ['dch']
        git_command = ['git', 'commit', '-a']

        print(f'Old Version: {get_version()}')
        
        if not self.dry_run:
            print(cz_command)
            subprocess.run(cz_command)
        else:
            print('NOTICE: Not bumping version, --dry-run specified.')
        
        version = get_version()
        print(f'New Version: {version}')

        ch_command.append(f'-v {version}')
        if not self.skip_deb:
            print(ch_command)
            if not self.dry_run:
                subprocess.run(ch_command)
                subprocess.run(['dch', '-r', '""'])
        
        git_command.append(f'-m chore(deb): Deb release {version}')
        if not self.skip_git:
            print(git_command)
            if not self.dry_run:
                subprocess.run(git_command)

setup(
    name='pop-transition',
    version=get_version(),
    description=(
        'Notify users if their Deb packages are no longer maintained so that '
        'they can transition to Flatpak versions instead.'
    ),
    url='https://github.com/pop-os/pop-transition',
    author='Ian Santopietro',
    author_email='ian@system76.com',
    license='ISC',
    packages=['pop-transition'],
    cmdclass={
        'release': Release
    }
)
