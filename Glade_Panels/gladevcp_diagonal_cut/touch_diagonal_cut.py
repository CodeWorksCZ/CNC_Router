#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import linuxcnc


class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()

        self.length_x = 20.0
        self.width_y = 5.0
        self.cut_depth = 6.0
        self.axis = 1.0
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0
        self.local_mode = False
        self.preview = False

        self.length_buttons = {10: "len_10", 20: "len_20", 30: "len_30", 50: "len_50"}
        self.width_buttons = {3: "width_3", 5: "width_5", 8: "width_8", 10: "width_10"}
        self.depth_buttons = {3: "depth_3", 5: "depth_5", 6: "depth_6", 10: "depth_10"}
        self.axis_buttons = {0: "axis_x", 1: "axis_y"}

        self._set_entry("entry_length", self.length_x)
        self._set_entry("entry_width", self.width_y)
        self._set_entry("entry_depth", self.cut_depth)
        self._set_entry("entry_axis", self.axis)
        self._set_entry("entry_tool_no", self.tool_no)
        self._set_entry("entry_tool_dia", self.tool_dia)
        self._set_entry("entry_feed", self.feed)
        self._update_status()
        self._highlight_all()

    def _obj(self, name):
        return self.builder.get_object(name)

    def _set_entry(self, name, value):
        obj = self._obj(name)
        if obj:
            obj.set_text(str(int(value)) if float(value).is_integer() else str(value))

    def _get_float(self, name, default):
        obj = self._obj(name)
        if not obj:
            return default
        try:
            return float(obj.get_text().replace(",", "."))
        except Exception:
            return default

    def _get_bool(self, name, default):
        obj = self._obj(name)
        if not obj:
            return default
        try:
            return bool(obj.get_active())
        except Exception:
            return default

    def _set_status(self, text):
        label = self._obj("label_status")
        if label:
            label.set_text(text)
        print(text)

    def _update_status(self):
        mode_name = "local" if self.local_mode else "toolchange"
        preview_name = "preview only - spindle off, safe Z" if self.preview else "real cut"
        self._set_status(
            "Selected: diagonal %s length %.1f, width %.1f | depth %.1f | %s | %s | T%d | Dia %.2f | F%d" %
            ("Y" if int(self.axis) == 1 else "X", self.length_x, self.width_y, self.cut_depth, mode_name, preview_name, int(self.tool_no), self.tool_dia, int(self.feed))
        )

    def _set_button_label(self, name, active):
        btn = self._obj(name)
        if not btn:
            return
        text = btn.get_label().replace("* ", "")
        btn.set_label(("* " if active else "") + text)

    def _highlight_all(self):
        for buttons, current in ((self.length_buttons, self.length_x), (self.width_buttons, self.width_y), (self.depth_buttons, self.cut_depth)):
            for value, name in buttons.items():
                self._set_button_label(name, abs(current - value) < 0.001)
        for value, name in self.axis_buttons.items():
            self._set_button_label(name, int(self.axis) == value)

    def _refresh_values(self):
        self.length_x = self._get_float("entry_length", self.length_x)
        self.width_y = self._get_float("entry_width", self.width_y)
        self.cut_depth = self._get_float("entry_depth", self.cut_depth)
        self.axis = self._get_float("entry_axis", self.axis)
        self.tool_no = self._get_float("entry_tool_no", self.tool_no)
        self.tool_dia = self._get_float("entry_tool_dia", self.tool_dia)
        self.feed = self._get_float("entry_feed", self.feed)
        self.local_mode = self._get_bool("check_local_mode", self.local_mode)
        self.preview = self._get_bool("check_preview", self.preview)
        self._update_status()
        self._highlight_all()

    def _set_value(self, attr, entry, value):
        setattr(self, attr, float(value))
        self._set_entry(entry, getattr(self, attr))
        self._update_status()
        self._highlight_all()

    def on_len_10_clicked(self, widget): self._set_value("length_x", "entry_length", 10)
    def on_len_20_clicked(self, widget): self._set_value("length_x", "entry_length", 20)
    def on_len_30_clicked(self, widget): self._set_value("length_x", "entry_length", 30)
    def on_len_50_clicked(self, widget): self._set_value("length_x", "entry_length", 50)
    def on_width_3_clicked(self, widget): self._set_value("width_y", "entry_width", 3)
    def on_width_5_clicked(self, widget): self._set_value("width_y", "entry_width", 5)
    def on_width_8_clicked(self, widget): self._set_value("width_y", "entry_width", 8)
    def on_width_10_clicked(self, widget): self._set_value("width_y", "entry_width", 10)
    def on_depth_3_clicked(self, widget): self._set_value("cut_depth", "entry_depth", 3)
    def on_depth_5_clicked(self, widget): self._set_value("cut_depth", "entry_depth", 5)
    def on_depth_6_clicked(self, widget): self._set_value("cut_depth", "entry_depth", 6)
    def on_depth_10_clicked(self, widget): self._set_value("cut_depth", "entry_depth", 10)
    def on_axis_x_clicked(self, widget): self._set_value("axis", "entry_axis", 0)
    def on_axis_y_clicked(self, widget): self._set_value("axis", "entry_axis", 1)

    def on_refresh_clicked(self, widget):
        self._refresh_values()

    def on_run_clicked(self, widget):
        self._refresh_values()
        if self.length_x <= 0 or self.width_y <= 0:
            self._set_status("ERROR: diagonal length and width must be greater than zero.")
            return
        if self.cut_depth <= 0:
            self._set_status("ERROR: cut depth must be greater than zero.")
            return
        if self.feed <= 0:
            self._set_status("ERROR: feed must be greater than zero.")
            return
        if int(self.axis) not in (0, 1):
            self._set_status("ERROR: axis must be X or Y.")
            return

        mdi = "o<diagonal_cut> call [%g] [%g] [%g] [%g] [%g] [%g] [%d] [%d] [%d]" % (
            self.length_x, self.width_y, self.cut_depth, self.tool_no, self.tool_dia, self.feed,
            int(self.axis), int(self.local_mode), int(self.preview)
        )
        try:
            self.stat.poll()
            self._set_status(("Sending PREVIEW: " if self.preview else "Sending CUT: ") + mdi)
            self.command.mode(linuxcnc.MODE_MDI)
            self.command.wait_complete(2.0)
            self.command.mdi(mdi)
            self.command.wait_complete(2.0)
            self._set_status("Sent: " + mdi)
        except Exception as e:
            self._set_status("MDI ERROR: " + str(e))


def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]
