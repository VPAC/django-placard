# Copyright 2012 VPAC
#
# This file is part of django-placard.
#
# django-placard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-placard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-placard  If not, see <http://www.gnu.org/licenses/>.


def is_password_strong(password, old_password=None):
    """Return True if password valid"""
    try:
        from crack import VeryFascistCheck
    except ImportError:
        def VeryFascistCheck(password, old=None):
            if old and password == old:
                return False
            elif len(password) < 6:
                return False
            return True
    try:
        VeryFascistCheck(password, old=old_password)
    except:
        return False

    return True
