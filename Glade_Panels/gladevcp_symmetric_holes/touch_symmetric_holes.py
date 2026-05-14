#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import linuxcnc


class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()

        self.diameter = 10.0
        self.thickness = 4.0
        self.distance = 50.0
        self.axis = 0.0
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0
        self.local_mode = False
        self.dry_run = False

        self.dia_buttons = {6: "dia_6", 8: "dia_8", 10: "dia_10", 12: "dia_12", 15: "dia_15", 20: "dia_20"}
        self.thick_buttons = {2: "thick_2", 3: "thick_3", 4: "thick_4", 6: "thick_6", 8: "thick_8", 10: "thick_10"}
        self.distance_buttons = {25: "dist_25", 50: "dist_50", 75: "dist_75", 100: "dist_100"}
        self.axis_buttons = {0: "axis_x", 1: "axis_y"}

        self._set_entry("entry_dia", self.diameter)
        self._set_entry("entry_thickness", self.thickness)
        self._set_entry("entry_distance", self.distance)
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
        dry_name = "preview only - spindle off, safe Z" if self.dry_run else "real cut"
        self._set_status(
            "Selected: dia %.1f | thickness %.1f | centers %s-/+%.1f | %s | %s | T%d | tool %.2f | F%d" %
            (self.diameter, self.thickness, "X" if int(self.axis) == 0 else "Y", self.distance, mode_name, dry_name, int(self.tool_no), self.tool_dia, int(self.feed))
        )

    def _set_button_label(self, name, active):
        btn = self._obj(name)
        if not btn:
            return
        text = btn.get_label().replace("* ", "")
        btn.set_label(("* " if active else "") + text)

    def _highlight_all(self):
        for value, name in self.dia_buttons.items():
            self._set_button_label(name, abs(self.diameter - value) < 0.001)
        for value, name in self.thick_buttons.items():
            self._set_button_label(name, int(self.thickness) == value)
        for value, name in self.distance_buttons.items():
            self._set_button_label(name, abs(self.distance - value) < 0.001)
        for value, name in self.axis_buttons.items():
            self._set_button_label(name, int(self.axis) == value)

    def _refresh_values(self):
        self.diameter = self._get_float("entry_dia", self.diameter)
        self.thickness = self._get_float("entry_thickness", self.thickness)
        self.distance = self._get_float("entry_distance", self.distance)
        self.axis = self._get_float("entry_axis", self.axis)
        self.tool_no = self._get_float("entry_tool_no", self.tool_no)
        self.tool_dia = self._get_float("entry_tool_dia", self.tool_dia)
        self.feed = self._get_float("entry_feed", self.feed)
        self.local_mode = self._get_bool("check_local_mode", self.local_mode)
        self.dry_run = self._get_bool("check_dry_run", self.dry_run)
        self._update_status()
        self._highlight_all()

    def _set_diameter(self, dia):
        self.diameter = float(dia)
        self._set_entry("entry_dia", self.diameter)
        self._update_status()
        self._highlight_all()

    def _set_thickness(self, thick):
        self.thickness = float(thick)
        self._set_entry("entry_thickness", self.thickness)
        self._update_status()
        self._highlight_all()

    def _set_distance(self, distance):
        self.distance = float(distance)
        self._set_entry("entry_distance", self.distance)
        self._update_status()
        self._highlight_all()

    def _set_axis(self, axis):
        self.axis = float(axis)
        self._set_entry("entry_axis", self.axis)
        self._update_status()
        self._highlight_all()

    def on_dia_6_clicked(self, widget): self._set_diameter(6)
    def on_dia_8_clicked(self, widget): self._set_diameter(8)
    def on_dia_10_clicked(self, widget): self._set_diameter(10)
    def on_dia_12_clicked(self, widget): self._set_diameter(12)
    def on_dia_15_clicked(self, widget): self._set_diameter(15)
    def on_dia_20_clicked(self, widget): self._set_diameter(20)

    def on_thick_2_clicked(self, widget): self._set_thickness(2)
    def on_thick_3_clicked(self, widget): self._set_thickness(3)
    def on_thick_4_clicked(self, widget): self._set_thickness(4)
    def on_thick_6_clicked(self, widget): self._set_thickness(6)
    def on_thick_8_clicked(self, widget): self._set_thickness(8)
    def on_thick_10_clicked(self, widget): self._set_thickness(10)

    def on_dist_25_clicked(self, widget): self._set_distance(25)
    def on_dist_50_clicked(self, widget): self._set_distance(50)
    def on_dist_75_clicked(self, widget): self._set_distance(75)
    def on_dist_100_clicked(self, widget): self._set_distance(100)

    def on_axis_x_clicked(self, widget): self._set_axis(0)
    def on_axis_y_clicked(self, widget): self._set_axis(1)

    def on_refresh_clicked(self, widget):
        self._refresh_values()

    def on_run_clicked(self, widget):
        self._refresh_values()

        if self.diameter <= self.tool_dia:
            self._set_status("ERROR: hole diameter must be larger than tool diameter.")
            return
        if self.thickness <= 0:
            self._set_status("ERROR: material thickness must be greater than zero.")
            return
        if self.distance <= 0:
            self._set_status("ERROR: distance from center must be greater than zero.")
            return
        if self.feed <= 0:
            self._set_status("ERROR: feed must be greater than zero.")
            return
        if int(self.axis) not in (0, 1):
            self._set_status("ERROR: axis must be X or Y.")
            return

        mdi = "o<symmetric_holes> call [%g] [%g] [%g] [%g] [%g] [%g] [%d] [%d] [%d]" % (
            self.diameter, self.thickness, self.tool_no, self.tool_dia, self.feed,
            self.distance, int(self.axis), int(self.local_mode), int(self.dry_run)
        )

        try:
            self.stat.poll()
            prefix = "Sending PREVIEW: " if self.dry_run else "Sending CUT: "
            self._set_status(prefix + mdi)
            self.command.mode(linuxcnc.MODE_MDI)
            self.command.wait_complete(2.0)
            self.command.mdi(mdi)
            self.command.wait_complete(2.0)
            self._set_status("Sent: " + mdi)
        except Exception as e:
            self._set_status("MDI ERROR: " + str(e))


def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]
