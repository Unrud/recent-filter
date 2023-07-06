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

from gi.repository import Adw
from gi.repository import Gio, GLib, Gtk

from recent_filter.filter import HOME_PATH, path_to_pattern
from recent_filter.util import gobject_log
from recent_filter.util.connection import (
    Closable, CloseStack, PropertyBinding, SignalConnection, create_action)

N_ = gettext.gettext


@Gtk.Template(resource_path='/io/github/unrud/RecentFilter/window.ui')
class RecentFilterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'RecentFilterWindow'

    ignore_pattern_buffer = Gtk.Template.Child()
    active_wdg = Gtk.Template.Child()
    preferences_wdg = Gtk.Template.Child()
    banner_wdg = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = self.get_application().service
        self._cs = CloseStack()
        self._cs.push(PropertyBinding(
            self._service, 'active',
            self.active_wdg, 'state', bi=True))
        self._cs.push(PropertyBinding(
            self._service, 'active',
            self.active_wdg, 'active'))
        self._cs.push(SignalConnection(
            self.active_wdg, 'state-set', self._handle_state_set))
        self._cs.push(PropertyBinding(
            self._service, 'active',
            self.preferences_wdg, 'sensitive', func_a_to_b=lambda b: not b))
        self._cs.push(PropertyBinding(
            self._service, 'ignore-pattern',
            self.ignore_pattern_buffer, 'text', bi=True))
        self._cs.push(PropertyBinding(
            self._service, 'active', self.banner_wdg, 'revealed'))
        self._cs.push(SignalConnection(
            self.banner_wdg, 'button-clicked',
            setattr, self._service, 'active', False, no_args=True))
        create_action(self, self._cs, 'add-folder', self._show_add_folder,
                      no_args=True)

    def _add_gio_files_to_pattern(self, files):
        if self._service.active or not files:
            return
        ignore_pattern = self._service.ignore_pattern
        for file in files:
            path = file.get_path()
            if not path:
                continue
            path_pattern = path_to_pattern(path, only_dir=True)
            if path_pattern in ignore_pattern.splitlines():
                continue
            if ignore_pattern and not ignore_pattern.endswith('\n'):
                ignore_pattern += '\n'
            ignore_pattern += path_pattern
        self._service.ignore_pattern = ignore_pattern

    def _show_add_folder(self):
        if os.path.exists('/.flatpak-info'):
            self._show_add_folder_builtin()
        else:
            self._show_add_folder_native()

    def _show_add_folder_native(self):
        def handle_callback(dialog, task):
            cancellable_closer.close()
            try:
                files = dialog.select_multiple_folders_finish(task)
            except GLib.GError:
                # Dialog cancelled
                return
            self._add_gio_files_to_pattern(files)
        dialog = gobject_log(Gtk.FileDialog(
            modal=True, title=N_('Add Folders to Ignore Pattern'),
            accept_label=N_('Select Folder')))
        cancellable = Gio.Cancellable()
        cancellable_closer = Closable()
        cancellable_closer.add_close_callback(cancellable.cancel)
        self._cs.push(cancellable_closer)
        dialog.select_multiple_folders(self, cancellable, handle_callback)

    def _show_add_folder_builtin(self):
        def handle_response(dialog, res):
            connection.close()
            if res == Gtk.ResponseType.ACCEPT:
                self._add_gio_files_to_pattern(dialog.get_files())
        dialog = gobject_log(Gtk.FileChooserDialog(
            modal=True, destroy_with_parent=True,
            title=N_('Add Folders to Ignore Pattern'),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            create_folders=False, select_multiple=True))
        dialog.set_current_folder(gobject_log(
            Gio.File.new_for_path(HOME_PATH)))
        dialog.add_button(N_('Cancel'), Gtk.ResponseType.CANCEL)
        dialog.add_button(N_('Select Folder'), Gtk.ResponseType.ACCEPT)
        dialog.set_transient_for(self)
        connection = SignalConnection(dialog, 'response', handle_response)
        connection.add_close_callback(dialog.destroy)
        self._cs.push(connection)
        dialog.present()

    def _handle_state_set(self, obj, state):
        if state:
            self._service.activate(self)
            return True
        return False
