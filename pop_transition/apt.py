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

pop-transition - APT interface module.
"""

from apt.cache import Cache
from threading import Thread

CACHE = Cache()

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