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
    with open(os.path.join('pop_transition', '__version__.py')) as fp:
        exec(fp.read(), version)
    return version['__version__']

class Release(Command):
    """ Generate a release and push it to git."""
    description = "Generate a release and push it to git."

    user_options = [
        ('dry-run', None, 'Skip the actual release and do a dry run instead.'),
        ('skip-deb', None, 'Skip doing a debian update for this release.'),
        ('skip-git', None, 'Skip committing to git at the end.'),
        ('prerelease=', None, 'Release a pre-release version (alpha,beta,rc)'),
        ('increment=', None, 'Manually specify the desired increment (MAJOR, MINOR, PATCH)')
    ]

    def initialize_options(self):
        self.dry_run = False
        self.skip_deb = False
        self.skip_git = False
        self.prerelease = None
        self.increment = None
    
    def finalize_options(self):
        pass

    def run(self):
        cz_command = ['cz', 'bump', '--yes']
        ch_command = ['dch']
        git_command = ['git', 'add', '.']

        def capture_version(sp_complete):
            output = sp_complete.stdout.decode('UTF-8').split('\n')
            print('\n'.join(output))
            for line in output:
                    if 'tag to create' in line:
                            version_line = line
            
            try:
                return version_line.split()[-1].replace('v', '')
            except UnboundLocalError:
                stderr = sp_complete.stderr.decode('UTF-8')
                print("WARNING: Couldn't get updated version! Using current.")
                print(stderr)
                return get_version()

        if self.dry_run:
            print('Dry run: Not making actual changes')
            cz_command.append('--dry-run')
        
        if self.prerelease:
            if self.prerelease.lower() not in ['alpha', 'beta', 'rc']:
                raise Exception(
                    f'{self.prerelease} is not a valid prerelease type. Please '
                    'use one of "alpha", "beta", or "rc".'
                )
            cz_command.append('--prerelease')
            cz_command.append(self.prerelease.lower())
        
        if self.increment:
            if self.increment.upper() not in ['MAJOR', 'MINOR', 'PATCH']:
                raise Exception(
                    f'{self.increment} is not a valid increments. Please use '
                    'one of MAJOR, MINOR, or PATCH.'
                )
            cz_command.append('--increment')
            cz_command.append(self.increment.upper())
        
        # We need to get the new version from CZ, as the file hasn't been 
        # updated yet.
        version_command = cz_command.copy()
        version_command.append('--dry-run')
        version_complete = subprocess.run(version_command, capture_output=True)
        
        version = capture_version(version_complete)
        print(f'Old Version: {get_version()}')
        print(f'New version: {version}')

        ch_command.append(f'-v{version}')
        if not self.skip_deb:
            print(ch_command)
            if not self.dry_run:
                subprocess.run(ch_command)
                subprocess.run(['dch', '-r', '""'])
        
        if not self.skip_git:
            print(git_command)
            if not self.dry_run:
                subprocess.run(git_command)

        print(' '.join(cz_command))
        if not self.dry_run:
            subprocess.run(cz_command)

class Test(Command):
    """ Run the local copy of the application for testing."""
    description = 'Run the local copy of the application for testing.'

    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        import pop_transition
        pop_transition.run()

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
    packages=['pop_transition'],
    cmdclass={
        'release': Release,
        'test': Test,
    },
    data_files=[
        ('/usr/share/dbus-1/system-services', ['data/org.pop_os.transition_system.service']),
        ('/usr/share/dbus-1/services', ['data/org.pop_os.transition.service']),
        ('/usr/share/applications', ['data/org.pop_os.transition.desktop']),
        ('/usr/share/polkit-1/actions', ['data/org.pop_os.transition.policy']),
        ('/etc/dbus-1/system.d/', ['data/org.pop_os.transition.conf']),
        ('/usr/lib/pop-transition', ['data/service.py']),
        ('/etc/xdg/autostart', ['data/org.pop_os.transition.Notify.desktop'])
    ],
    scripts=['bin/pop-transition']
)
