# Copyright 2023 Unrud <unrud@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from recent_filter import gitignore

HOME_PATH = os.path.expanduser('~')


def expand_path(path):
    if path == '~' or path.startswith('~/'):
        path = HOME_PATH + path[1:]
    return path


def path_to_pattern(path, only_dir=False):
    if only_dir and not path.endswith('/'):
        path += '/'
    if path == HOME_PATH or path.startswith(HOME_PATH + '/'):
        path = '~' + path[len(HOME_PATH):]
    return gitignore.escape(path)


class Filter:
    def __init__(self, ignore_pattern):
        self._pattern = list(filter(None, (
            gitignore.convert_to_re(expand_path(line))
            for line in ignore_pattern.splitlines())))

    def __call__(self, path):
        is_match = False
        for p in self._pattern:
            if is_match == p.negate and p(path):
                is_match = not is_match
        return is_match
