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
import sys

from gi.repository import Adw, Gio, GLib, Gtk
from recent_filter.service import Service
from recent_filter.util import gobject_log
from recent_filter.util.connection import (CloseStack, SignalConnection,
                                           create_action)
from recent_filter.window import RecentFilterWindow

N_ = gettext.gettext


class RecentFilterApplication(Adw.Application):

    def __init__(self):
        super().__init__(application_id='io.github.unrud.RecentFilter',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self._cs = CloseStack()
        self.add_main_option('service', 0, GLib.OptionFlags.HIDDEN,
                             GLib.OptionArg.NONE, '', None)
        self.service = gobject_log(Service(self))
        GLib.set_application_name(N_('Recent Filter'))

        self._cs.push(SignalConnection(
            self, 'shutdown', self._cs.close, no_args=True))
        create_action(self, self._cs, 'quit', self.quit, no_args=True)
        self.set_accels_for_action('app.quit', ['<primary>q'])
        create_action(self, self._cs, 'about', self._show_about, no_args=True)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = RecentFilterWindow(application=self)
        win.present()

    def do_handle_local_options(self, options):
        service_opt = options.lookup_value('service', GLib.VariantType('b'))
        if service_opt:
            self.register()
            return 0
        return -1

    def _show_about(self):
        builder = Gtk.Builder.new_from_resource(
            '/io/github/unrud/RecentFilter/about_dialog.ui')
        about_window = builder.get_object('about_window')
        about_window.set_transient_for(self.props.active_window)
        about_window.present()


def main(version):
    app = RecentFilterApplication()
    return app.run(sys.argv)
