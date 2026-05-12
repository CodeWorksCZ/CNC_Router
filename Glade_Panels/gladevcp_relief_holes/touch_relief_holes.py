#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GMoccapy relief holes handler - no gtk.MessageDialog
# Fixes gi.repository / static gtk dialog conflict.

import linuxcnc
import hal
import time

class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()

        self.diameter = 20.0
        self.thickness = 4.0
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0
        self.hole_count = 1.0
        self.spacing = 10.0
        self.direction = 0.0
        self.local_mode = False

        self.dia_buttons = {
            10: "dia_10", 15: "dia_15", 20: "dia_20", 25: "dia_25", 30: "dia_30",
            35: "dia_35", 40: "dia_40", 45: "dia_45", 50: "dia_50", 55: "dia_55", 60: "dia_60"
        }
        self.thick_buttons = {
            2: "thick_2", 3: "thick_3", 4: "thick_4", 6: "thick_6",
            8: "thick_8", 10: "thick_10", 12: "thick_12"
        }
        self.count_buttons = {1: "count_1", 2: "count_2", 5: "count_5", 10: "count_10"}
        self.direction_buttons = {0: "direction_x_pos", 1: "direction_x_neg", 2: "direction_y_pos", 3: "direction_y_neg"}

        self._set_entry("entry_custom_dia", self.diameter)
        self._set_entry("entry_tool_no", self.tool_no)
        self._set_entry("entry_tool_dia", self.tool_dia)
        self._set_entry("entry_feed", self.feed)
        self._set_entry("entry_thickness", self.thickness)
        self._set_entry("entry_count", self.hole_count)
        self._set_entry("entry_spacing", self.spacing)
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
        direction_names = {0: "+X", 1: "-X", 2: "+Y", 3: "-Y"}
        direction_name = direction_names.get(int(self.direction), "+X")
        mode_name = "local" if self.local_mode else "toolchange"
        self._set_status(
            "Selected: hole %.1f mm | material %.1f mm | %d holes, %.1f mm spacing, %s | %s | T%d | tool %.2f mm | F%d" %
            (self.diameter, self.thickness, int(self.hole_count), self.spacing, direction_name, mode_name, int(self.tool_no), self.tool_dia, int(self.feed))
        )

    def _set_button_label(self, name, active):
        btn = self._obj(name)
        if not btn:
            return
        text = btn.get_label().replace("* ", "")
        btn.set_label(("* " if active else "") + text)

    def _highlight_all(self):
        for value, name in self.thick_buttons.items():
            self._set_button_label(name, int(self.thickness) == value)
        for value, name in self.dia_buttons.items():
            self._set_button_label(name, abs(self.diameter - value) < 0.001)
        for value, name in self.count_buttons.items():
            self._set_button_label(name, int(self.hole_count) == value)
        for value, name in self.direction_buttons.items():
            self._set_button_label(name, int(self.direction) == value)

    def _refresh_values(self):
        self.tool_no = self._get_float("entry_tool_no", self.tool_no)
        self.tool_dia = self._get_float("entry_tool_dia", self.tool_dia)
        self.feed = self._get_float("entry_feed", self.feed)
        self.diameter = self._get_float("entry_custom_dia", self.diameter)
        self.thickness = self._get_float("entry_thickness", self.thickness)
        self.hole_count = self._get_float("entry_count", self.hole_count)
        self.spacing = self._get_float("entry_spacing", self.spacing)
        self.local_mode = self._get_bool("check_local_mode", self.local_mode)
        self._update_status()
        self._highlight_all()

    def _set_diameter(self, dia):
        self.diameter = float(dia)
        self._set_entry("entry_custom_dia", self.diameter)
        self._update_status()
        self._highlight_all()

    def on_dia_10_clicked(self, widget): self._set_diameter(10)
    def on_dia_15_clicked(self, widget): self._set_diameter(15)
    def on_dia_20_clicked(self, widget): self._set_diameter(20)
    def on_dia_25_clicked(self, widget): self._set_diameter(25)
    def on_dia_30_clicked(self, widget): self._set_diameter(30)
    def on_dia_35_clicked(self, widget): self._set_diameter(35)
    def on_dia_40_clicked(self, widget): self._set_diameter(40)
    def on_dia_45_clicked(self, widget): self._set_diameter(45)
    def on_dia_50_clicked(self, widget): self._set_diameter(50)
    def on_dia_55_clicked(self, widget): self._set_diameter(55)
    def on_dia_60_clicked(self, widget): self._set_diameter(60)

    def on_custom_set_clicked(self, widget):
        self._set_diameter(self._get_float("entry_custom_dia", self.diameter))

    def _set_thickness(self, thick):
        self.thickness = float(thick)
        self._set_entry("entry_thickness", self.thickness)
        self._update_status()
        self._highlight_all()

    def _set_count(self, count):
        self.hole_count = float(count)
        self._set_entry("entry_count", self.hole_count)
        self._update_status()
        self._highlight_all()

    def _set_direction(self, direction):
        self.direction = float(direction)
        self._update_status()
        self._highlight_all()

    def on_thick_2_clicked(self, widget): self._set_thickness(2)
    def on_thick_3_clicked(self, widget): self._set_thickness(3)
    def on_thick_4_clicked(self, widget): self._set_thickness(4)
    def on_thick_6_clicked(self, widget): self._set_thickness(6)
    def on_thick_8_clicked(self, widget): self._set_thickness(8)
    def on_thick_10_clicked(self, widget): self._set_thickness(10)
    def on_thick_12_clicked(self, widget): self._set_thickness(12)

    def on_count_1_clicked(self, widget): self._set_count(1)
    def on_count_2_clicked(self, widget): self._set_count(2)
    def on_count_5_clicked(self, widget): self._set_count(5)
    def on_count_10_clicked(self, widget): self._set_count(10)

    def on_direction_x_pos_clicked(self, widget): self._set_direction(0)
    def on_direction_x_neg_clicked(self, widget): self._set_direction(1)
    def on_direction_y_pos_clicked(self, widget): self._set_direction(2)
    def on_direction_y_neg_clicked(self, widget): self._set_direction(3)

    def on_refresh_clicked(self, widget):
        self._refresh_values()

    def on_run_clicked(self, widget):
        self._refresh_values()

        if self.diameter <= self.tool_dia:
            self._set_status("ERROR: hole diameter must be larger than tool diameter.")
            return
        if self.hole_count < 1:
            self._set_status("ERROR: hole count must be at least 1.")
            return
        if self.spacing < 0:
            self._set_status("ERROR: spacing cannot be negative.")
            return
        if self.hole_count > 1 and self.spacing <= 0:
            self._set_status("ERROR: spacing must be greater than 0 for multiple holes.")
            return
        if int(self.direction) not in (0, 1, 2, 3):
            self._set_status("ERROR: direction must be +X, -X, +Y, or -Y.")
            return

        mdi = "o<relief_hole> call [%g] [%g] [%g] [%g] [%g] [%d] [%g] [%d] [%d]" % (
            self.diameter, self.thickness, self.tool_no, self.tool_dia, self.feed,
            int(self.hole_count), self.spacing, int(self.direction), int(self.local_mode)
        )

        try:
            self.stat.poll()
            self._set_status("Sending MDI: " + mdi)
            self.command.mode(linuxcnc.MODE_MDI)
            self.command.wait_complete(2.0)
            self.command.mdi(mdi)
            self.command.wait_complete(2.0)
            self._set_status("Sent: " + mdi)
        except Exception as e:
            self._set_status("MDI ERROR: " + str(e))

def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]
