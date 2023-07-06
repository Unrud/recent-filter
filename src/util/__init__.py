# Copyright 2019-2020, 2023 Unrud <unrud@outlook.com>
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

from gi.repository import GLib


def gobject_log(obj, info=None):
    DOMAIN = 'gobject-ref'
    LEVEL = GLib.LogLevelFlags.LEVEL_DEBUG
    name = repr(obj)
    if info:
        name += ' (' + str(info) + ')'
    g_log(DOMAIN, LEVEL, 'Create %s', name)
    obj.weak_ref(g_log, DOMAIN, LEVEL, 'Destroy %s', name)
    return obj


def g_log(domain, log_level, format_string, *args):
    fields = GLib.Variant('a{sv}', {
        'MESSAGE': GLib.Variant('s', format_string % args)})
    GLib.log_variant(domain, log_level, fields)
