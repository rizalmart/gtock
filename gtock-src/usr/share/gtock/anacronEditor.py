# anacronEditor.py - GTK editor for /etc/anacrontab
# SPDX-License-Identifier: GPL-2.0-or-later

import gi
import anacron

from locale import gettext as _

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class AnacronEditor:
    def __init__(self, parent):
        self.parent = parent
        self.backend = anacron.Anacron()

    def _message(self, message, error=True):
        dialog = Gtk.MessageDialog(
            transient_for=self.parent.window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR if error else Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=str(message),
        )
        dialog.run()
        dialog.destroy()

    @staticmethod
    def _set_button_icon(button, icon_name):
        """Place a themed icon above a button label (GTK 3)."""
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.set_image(image)
        button.set_always_show_image(True)
        button.set_image_position(Gtk.PositionType.TOP)

    @staticmethod
    def _icon_tool_button(label, icon_name, tooltip=None):
        """Create a GTK toolbar button with an icon and a text label."""
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        button = Gtk.ToolButton.new(image, label)
        if tooltip:
            button.set_tooltip_text(tooltip)
        return button

    def _job_dialog(self, job=None):
        dialog = Gtk.Dialog(title="Anacron task", transient_for=self.parent.window,
                           flags=Gtk.DialogFlags.MODAL)
        cancel_button = dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        save_button = dialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        self._set_button_icon(cancel_button, "process-stop")
        self._set_button_icon(save_button, "document-save")
        grid = Gtk.Grid(column_spacing=8, row_spacing=8, margin=12)
        dialog.get_content_area().add(grid)
        fields = [
            ("Period (days or @monthly)", "period", "1"),
            ("Delay (minutes)", "delay", "5"),
            ("Job identifier", "identifier", "gtock-job"),
            ("Command", "command", ""),
        ]
        entries = {}
        for row, (label, key, default) in enumerate(fields):
            grid.attach(Gtk.Label(label=label, xalign=0), 0, row, 1, 1)
            entry = Gtk.Entry()
            entry.set_text(str(job[key]) if job else default)
            entry.set_hexpand(True)
            grid.attach(entry, 1, row, 1, 1)
            entries[key] = entry
        dialog.show_all()
        response = dialog.run()
        values = {key: entry.get_text() for key, entry in entries.items()}
        dialog.destroy()
        return values if response == Gtk.ResponseType.OK else None

    def show(self, *args):
        if not self.backend.executable:
            return self._message("Anacron is not installed.")
        if not self.backend.available():
            return self._message("/etc/anacrontab does not exist or is not accessible.")

        dialog = Gtk.Dialog(title="Anacron tasks", transient_for=self.parent.window,
                           flags=Gtk.DialogFlags.MODAL)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(720, 320)
        area = dialog.get_content_area()

        # Keep task actions in a proper toolbar, matching the main gTock window.
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        toolbar.set_icon_size(Gtk.IconSize.LARGE_TOOLBAR)
        toolbar.set_show_arrow(False)
        add_button = self._icon_tool_button(
            _("Add"), "list-add", _("Add an Anacron task"))
        edit_button = self._icon_tool_button(
            _("Edit"), "document-edit", _("Edit the selected Anacron task"))
        delete_button = self._icon_tool_button(
            _("Delete"), "edit-delete", _("Delete the selected Anacron task"))
        for button in (add_button, edit_button, delete_button):
            toolbar.insert(button, -1)
        area.pack_start(toolbar, False, False, 0)

        # The final column stores a themed icon name for each tree row.
        store = Gtk.ListStore(str, str, str, str, int, str)
        tree = Gtk.TreeView(model=store)

        period_column = Gtk.TreeViewColumn(_("Period"))
        icon_renderer = Gtk.CellRendererPixbuf()
        period_column.pack_start(icon_renderer, False)
        period_column.add_attribute(icon_renderer, "icon-name", 5)
        period_renderer = Gtk.CellRendererText()
        period_column.pack_start(period_renderer, True)
        period_column.add_attribute(period_renderer, "text", 0)
        period_column.set_resizable(True)
        tree.append_column(period_column)

        for title, column in ((_("Delay"), 1), (_("Identifier"), 2), (_("Command"), 3)):
            renderer = Gtk.CellRendererText()
            view_column = Gtk.TreeViewColumn(title, renderer, text=column)
            view_column.set_resizable(True)
            tree.append_column(view_column)
        area.pack_start(tree, True, True, 8)

        def refresh():
            store.clear()
            for job in self.backend.read():
                store.append([job["period"], str(job["delay"]), job["identifier"],
                              job["command"], job["linenumber"], "x-office-calendar"])
            update_action_sensitivity()

        def selected():
            model, iterator = tree.get_selection().get_selected()
            if iterator is None:
                return None
            return model, iterator

        def add_job(button):
            values = self._job_dialog()
            if values:
                try:
                    self.backend.add(**values)
                    refresh()
                except Exception as exc:
                    self._message(exc)

        def edit_job(button):
            row = selected()
            if not row:
                return
            model, iterator = row
            line = model.get_value(iterator, 4)
            job = next((item for item in self.backend.read() if item["linenumber"] == line), None)
            values = self._job_dialog(job)
            if values:
                try:
                    self.backend.update(line, **values)
                    refresh()
                except Exception as exc:
                    self._message(exc)

        def delete_job(button):
            row = selected()
            if not row:
                return
            model, iterator = row
            line = model.get_value(iterator, 4)
            try:
                self.backend.delete(line)
                refresh()
            except Exception as exc:
                self._message(exc)

        def update_action_sensitivity(*args):
            has_selection = selected() is not None
            edit_button.set_sensitive(has_selection)
            delete_button.set_sensitive(has_selection)

        add_button.connect("clicked", add_job)
        edit_button.connect("clicked", edit_job)
        delete_button.connect("clicked", delete_job)
        tree.get_selection().connect("changed", update_action_sensitivity)
        # Edit/Delete are unavailable until a concrete job row is selected.
        update_action_sensitivity()
        refresh()
        dialog.show_all()
        dialog.run()
        dialog.destroy()
