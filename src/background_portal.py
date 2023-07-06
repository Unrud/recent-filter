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


import uuid

from collections.abc import Callable
from typing import Iterable, Optional

from gi.repository import Gio, GLib

from recent_filter.util import gobject_log
from recent_filter.util.connection import CloseStack, SignalConnection


class BackgroundPortal:
    def __init__(self):
        self._cs = CloseStack()
        self._background_proxy = gobject_log(Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES |
            Gio.DBusProxyFlags.DO_NOT_CONNECT_SIGNALS |
            Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION, None,
            'org.freedesktop.portal.Desktop',
            '/org/freedesktop/portal/desktop',
            'org.freedesktop.portal.Background'))
        unique_name = self._background_proxy.get_connection().get_unique_name()
        self._sender = unique_name.lstrip(':').replace('.', '_')

    def _connect_response(self, on_response):
        def handle_response(response_proxy, unique_name, method, value):
            if method == 'Response':
                signal_conn.close()
                response, results = value
                on_response(response, results)
        token = str(uuid.uuid4()).replace('-', '_')
        proxy = gobject_log(Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION, Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES |
            Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION, None,
            'org.freedesktop.portal.Desktop',
            '/org/freedesktop/portal/desktop/request/%s/%s' %
            (self._sender, token),
            'org.freedesktop.portal.Request'))
        signal_conn = SignalConnection(proxy, 'g-signal', handle_response)
        self._cs.push(signal_conn)
        return token

    def set_status(self, message: str) -> None:
        parameters = GLib.Variant('(a{sv})', (
            {
                'message': GLib.Variant.new_string(message),
            },
        ))
        self._background_proxy.call_sync(
            'SetStatus', parameters, Gio.DBusCallFlags.NONE, -1)

    def request_background(
            self, window_handle: str, reason: Optional[str],
            autostart: Optional[bool], background: Optional[bool],
            commandline: Optional[Iterable[str]],
            on_response: Optional[Callable[[bool, bool], None]]) -> None:
        if on_response is None:
            on_response = lambda _autostart, _background: None  # noqa: E731
        token = self._connect_response(lambda _, results: on_response(
            results['autostart'], results['background']))
        options = {
            'handle_token': GLib.Variant.new_string(token),
            'dbus-activatable': GLib.Variant.new_boolean(False),
        }
        if reason is not None:
            options['reason'] = GLib.Variant.new_string(reason)
        if autostart is not None:
            options['autostart'] = GLib.Variant.new_boolean(autostart)
        if background is not None:
            options['background'] = GLib.Variant.new_boolean(background)
        if commandline is not None:
            options['commandline'] = GLib.Variant('as', list(commandline))

        parameters = GLib.Variant('(sa{sv})', (window_handle, options,))
        self._background_proxy.call_sync(
            'RequestBackground', parameters, Gio.DBusCallFlags.NONE, -1)
