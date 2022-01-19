# -*- coding: utf-8 -*-

"""Top-level package for didatictests."""

__author__ = "Lincoln Makoto Kawakami"
__email__ = "lmkawakami@hotmail.com"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.9"


def get_module_version():
    return __version__


from .example import Example  # noqa: F401

from .didatictests import Didatic_test  # noqa: F401
