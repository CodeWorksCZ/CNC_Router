#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import linuxcnc


class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()

        self.width = 60.0
        self.height = 30.0
        self.corner_r = 3.0
        self.thickness = 4.0
        self.distance = 50.0
        self.axis = 0.0
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0
        self.local_mode = False
        self.dry_run = False

        self.width_buttons = {20: "width_20", 40: "width_40", 60: "width_60", 80: "width_80"}
        self.height_buttons = {10: "height_10", 20: "height_20", 30: "height_30", 40: "height_40"}
        self.radius_buttons = {0: "radius_0", 2: "radius_2", 3: "radius_3", 5: "radius_5"}
        self.thick_buttons = {2: "thick_2", 3: "thick_3", 4: "thick_4", 6: "thick_6"}
        self.distance_buttons = {25: "dist_25", 50: "dist_50", 75: "dist_75", 100: "dist_100"}
        self.axis_buttons = {0: "axis_x", 1: "axis_y"}

        for name, value in (
            ("entry_width", self.width), ("entry_height", self.height), ("entry_radius", self.corner_r),
            ("entry_thickness", self.thickness), ("entry_distance", self.distance), ("entry_axis", self.axis),
            ("entry_tool_no", self.tool_no), ("entry_tool_dia", self.tool_dia), ("entry_feed", self.feed)
        ):
            self._set_entry(name, value)
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
        axis_name = "X" if int(self.axis) == 0 else "Y"
        self._set_status(
            "Selected: rect %.1f x %.1f R%.1f | centers %s-/+%.1f | %.1f mm | %s | %s | T%d | Dia %.2f | F%d" %
            (self.width, self.height, self.corner_r, axis_name, self.distance, self.thickness, mode_name, dry_name, int(self.tool_no), self.tool_dia, int(self.feed))
        )

    def _set_button_label(self, name, active):
        btn = self._obj(name)
        if not btn:
            return
        text = btn.get_label().replace("* ", "")
        btn.set_label(("* " if active else "") + text)

    def _highlight_all(self):
        groups = [
            (self.width_buttons, self.width), (self.height_buttons, self.height), (self.radius_buttons, self.corner_r),
            (self.thick_buttons, self.thickness), (self.distance_buttons, self.distance), (self.axis_buttons, self.axis)
        ]
        for buttons, current in groups:
            for value, name in buttons.items():
                self._set_button_label(name, abs(float(current) - float(value)) < 0.001)

    def _refresh_values(self):
        self.width = self._get_float("entry_width", self.width)
        self.height = self._get_float("entry_height", self.height)
        self.corner_r = self._get_float("entry_radius", self.corner_r)
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

    def _set_value(self, attr, entry, value):
        setattr(self, attr, float(value))
        self._set_entry(entry, getattr(self, attr))
        self._update_status()
        self._highlight_all()

    def on_width_20_clicked(self, widget): self._set_value("width", "entry_width", 20)
    def on_width_40_clicked(self, widget): self._set_value("width", "entry_width", 40)
    def on_width_60_clicked(self, widget): self._set_value("width", "entry_width", 60)
    def on_width_80_clicked(self, widget): self._set_value("width", "entry_width", 80)
    def on_height_10_clicked(self, widget): self._set_value("height", "entry_height", 10)
    def on_height_20_clicked(self, widget): self._set_value("height", "entry_height", 20)
    def on_height_30_clicked(self, widget): self._set_value("height", "entry_height", 30)
    def on_height_40_clicked(self, widget): self._set_value("height", "entry_height", 40)
    def on_radius_0_clicked(self, widget): self._set_value("corner_r", "entry_radius", 0)
    def on_radius_2_clicked(self, widget): self._set_value("corner_r", "entry_radius", 2)
    def on_radius_3_clicked(self, widget): self._set_value("corner_r", "entry_radius", 3)
    def on_radius_5_clicked(self, widget): self._set_value("corner_r", "entry_radius", 5)
    def on_thick_2_clicked(self, widget): self._set_value("thickness", "entry_thickness", 2)
    def on_thick_3_clicked(self, widget): self._set_value("thickness", "entry_thickness", 3)
    def on_thick_4_clicked(self, widget): self._set_value("thickness", "entry_thickness", 4)
    def on_thick_6_clicked(self, widget): self._set_value("thickness", "entry_thickness", 6)
    def on_dist_25_clicked(self, widget): self._set_value("distance", "entry_distance", 25)
    def on_dist_50_clicked(self, widget): self._set_value("distance", "entry_distance", 50)
    def on_dist_75_clicked(self, widget): self._set_value("distance", "entry_distance", 75)
    def on_dist_100_clicked(self, widget): self._set_value("distance", "entry_distance", 100)
    def on_axis_x_clicked(self, widget): self._set_value("axis", "entry_axis", 0)
    def on_axis_y_clicked(self, widget): self._set_value("axis", "entry_axis", 1)

    def on_refresh_clicked(self, widget):
        self._refresh_values()

    def on_run_clicked(self, widget):
        self._refresh_values()
        if self.width <= self.tool_dia or self.height <= self.tool_dia:
            self._set_status("ERROR: rectangle must be larger than tool diameter.")
            return
        if self.corner_r < 0 or self.corner_r > min(self.width, self.height) / 2.0:
            self._set_status("ERROR: corner radius is invalid.")
            return
        if self.thickness <= 0 or self.distance <= 0 or self.feed <= 0:
            self._set_status("ERROR: thickness, distance and feed must be greater than zero.")
            return
        if int(self.axis) not in (0, 1):
            self._set_status("ERROR: axis must be X or Y.")
            return

        mdi = "o<symmetric_rectangles> call [%g] [%g] [%g] [%g] [%g] [%g] [%g] [%g] [%d] [%d] [%d]" % (
            self.width, self.height, self.corner_r, self.thickness, self.tool_no, self.tool_dia, self.feed,
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
