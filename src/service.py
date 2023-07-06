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

import gettext
import os
import sys

from gi.repository import Gio, GLib, GObject, Gtk

from recent_filter.background_portal import BackgroundPortal
from recent_filter.filter import Filter
from recent_filter.util import g_log, gobject_log
from recent_filter.util.connection import (CloseStack, PropertyBinding,
                                           SignalConnection)

COMMANDLINE = sys.argv[:1]
RECENTLY_USED_PATH = os.path.expanduser('~/.local/share/recently-used.xbel')
N_ = gettext.gettext


class Service(GObject.GObject):
    active = GObject.Property(type=bool, default=False)
    ignore_pattern = GObject.Property(type=str, default='')

    def __init__(self, application):
        super().__init__()
        self._cs = CloseStack()
        self._application = application
        self._settings = gobject_log(
            Gio.Settings.new(self._application.props.application_id))
        self._settings.bind('active', self, 'active',
                            Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind('ignore-pattern', self, 'ignore-pattern',
                            Gio.SettingsBindFlags.DEFAULT)
        self._recent_manager = gobject_log(Gtk.RecentManager(
            filename=RECENTLY_USED_PATH))
        self._bg_portal = BackgroundPortal()
        self._previous_active = None
        self._cs.push(PropertyBinding(
            self, 'active', func_a_to_b=self._on_active_changed))
        self._cs.push(SignalConnection(
            self._recent_manager, 'changed', self._recent_filter,
            no_args=True))
        self._cs.push(SignalConnection(
            self, 'notify::active', self._recent_filter, no_args=True))
        self._filter = None
        self._cs.push(SignalConnection(
            self, 'notify::ignore-pattern',
            setattr, self, '_filter', None, no_args=True))
        self._recent_filter()

    def _on_active_changed(self, active):
        if not self._previous_active and active:
            self._application.hold()
        if self._previous_active and not active:
            self._application.release()
        if not active:
            self._bg_portal.request_background(
                '', N_('Deactivate background service'),
                False, False, None, None)
            self._bg_portal.set_status(N_('Service deactivated'))
        else:
            self._bg_portal.set_status(N_('Monitoring recently used files'))
        self._previous_active = active

    def _recent_filter(self):
        if not self.active:
            return
        if self._filter is None:
            self._filter = Filter(self.ignore_pattern)
        for recent_info in self._recent_manager.get_items():
            uri = recent_info.get_uri()
            path = Gio.File.new_for_uri(uri).get_path()
            if not path:
                continue
            if self._filter(path) and self._recent_manager.remove_item(uri):
                g_log('service', GLib.LogLevelFlags.LEVEL_INFO,
                      'Removed recent file %r', path)

    def activate(self, window):
        def handle_response(autostart, background):
            self.active = autostart and background
        # TODO: No public API to get window handle
        window_handle = ''
        self._bg_portal.request_background(
            window_handle, N_('Activate background service'), True, True,
            [*COMMANDLINE, '--service'], handle_response)
