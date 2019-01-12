"""
gui_set_path module provides a file dialog for selecting paths or a line edit to paste and display the chosen path

Copyright (C) 2017 Stefan Tapper, All rights reserved.

    This file is part of RenderKnecht Strink Kerker.

    RenderKnecht Strink Kerker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RenderKnecht Strink Kerker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with RenderKnecht Strink Kerker.  If not, see <http://www.gnu.org/licenses/>.

"""
import os.path
from pathlib import Path
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QObject, Signal

from modules.log import init_logging
from modules.detect_language import get_translation

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class SetDirectoryPath(QObject):
    path_changed = Signal(Path)
    invalid_path_entered = Signal()

    def __init__(self, app, ui, mode='dir',
                 line_edit=None,
                 tool_button=None,
                 dialog_args=(),
                 reject_invalid_path_edits=False,
                 parent=None):
        super(SetDirectoryPath, self).__init__()
        self.app, self.ui, self.line_edit, self.tool_button = app, ui, line_edit, tool_button
        self.mode = mode

        self.path = None

        self.parent = self.ui
        if parent is not None:
            self.parent = parent

        if self.tool_button:
            self.dialog_args = dialog_args
            self.tool_button.pressed.connect(self.btn_open_dialog)

        if self.line_edit:
            self.reject_invalid_path_edits = reject_invalid_path_edits
            self.line_edit.editingFinished.connect(self.path_text_changed)

    def btn_open_dialog(self):
        current_path = Path('.') or self.ui.current_path

        if self.line_edit:
            line_edit_path = Path(self.line_edit.text())

            if line_edit_path.exists():
                current_path = line_edit_path
            else:
                current_path = Path('.')

        self.get_directory_file_dialog(current_path, *self.dialog_args)

    def get_directory_file_dialog(self, current_path, title=_("Verzeichnis auswählen"), file_filter='(*.*)'):
        if not Path(current_path).exists() or current_path == '':
            current_path = Path(self.ui.current_path)
        else:
            current_path = Path(current_path)

        if self.mode == 'dir':
            current_path = QFileDialog.getExistingDirectory(
                self.parent, caption=title, directory=current_path.as_posix()
            )
            if not current_path:
                return
        else:
            current_path, file_type = QFileDialog.getOpenFileName(
                self.parent, caption=title, directory=current_path.as_posix(), filter=file_filter
            )
            if not file_type:
                return

        if self.mode == 'file2dir':
            if Path(current_path).is_file():
                current_path = Path(current_path).parent

        current_path = Path(current_path)

        self.set_path(current_path)

        return current_path

    def set_path(self, current_path):
        current_path = Path(current_path)
        if not current_path.exists():
            return

        # Update line edit
        self.set_path_text(current_path)

        # Emit change
        self.path_changed.emit(current_path)

        # Set own path var
        self.path = current_path

    def set_path_text(self, current_path):
        if not self.line_edit:
            return

        self.line_edit.setText(current_path.as_posix())

    def path_text_changed(self):
        """ line edit text changed """
        text_path = self.line_edit.text()

        if os.path.exists(text_path):
            text_path = Path(text_path)

            if self.path:
                if text_path != self.path:
                    self.set_path(text_path)
            else:
                self.set_path(text_path)
        else:
            # Pasted or typed Path does not exist
            if self.reject_invalid_path_edits:
                self.line_edit.clear()
                self.line_edit.setPlaceholderText(_("< Gültigen Pfad eingeben >"))

            self.invalid_path_entered.emit()
