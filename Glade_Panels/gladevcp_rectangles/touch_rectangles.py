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
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0
        self.local_mode = False

        self.width_buttons = {20: "width_20", 30: "width_30", 40: "width_40", 50: "width_50", 60: "width_60", 80: "width_80"}
        self.height_buttons = {10: "height_10", 15: "height_15", 20: "height_20", 25: "height_25", 30: "height_30", 40: "height_40"}
        self.radius_buttons = {0: "radius_0", 2: "radius_2", 3: "radius_3", 5: "radius_5", 8: "radius_8", 10: "radius_10"}
        self.thick_buttons = {2: "thick_2", 3: "thick_3", 4: "thick_4"}

        self._set_entry("entry_width", self.width)
        self._set_entry("entry_height", self.height)
        self._set_entry("entry_radius", self.corner_r)
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
        self._set_status(
            "Selected: rectangle %.1f x %.1f mm | R%.1f | material %.1f mm | %s | T%d | tool %.2f mm | F%d" %
            (self.width, self.height, self.corner_r, self.thickness, mode_name, int(self.tool_no), self.tool_dia, int(self.feed))
        )

    def _set_button_label(self, name, active):
        btn = self._obj(name)
        if not btn:
            return
        text = btn.get_label().replace("* ", "")
        btn.set_label(("* " if active else "") + text)

    def _highlight_all(self):
        for value, name in self.width_buttons.items():
            self._set_button_label(name, abs(self.width - value) < 0.001)
        for value, name in self.height_buttons.items():
            self._set_button_label(name, abs(self.height - value) < 0.001)
        for value, name in self.radius_buttons.items():
            self._set_button_label(name, abs(self.corner_r - value) < 0.001)
        for value, name in self.thick_buttons.items():
            self._set_button_label(name, int(self.thickness) == value)

    def _refresh_values(self):
        self.width = self._get_float("entry_width", self.width)
        self.height = self._get_float("entry_height", self.height)
        self.corner_r = self._get_float("entry_radius", self.corner_r)
        self.tool_no = self._get_float("entry_tool_no", self.tool_no)
        self.tool_dia = self._get_float("entry_tool_dia", self.tool_dia)
        self.feed = self._get_float("entry_feed", self.feed)
        self.local_mode = self._get_bool("check_local_mode", self.local_mode)
        self._update_status()
        self._highlight_all()

    def _set_width(self, width):
        self.width = float(width)
        self._set_entry("entry_width", self.width)
        self._update_status()
        self._highlight_all()

    def _set_height(self, height):
        self.height = float(height)
        self._set_entry("entry_height", self.height)
        self._update_status()
        self._highlight_all()

    def _set_radius(self, radius):
        self.corner_r = float(radius)
        self._set_entry("entry_radius", self.corner_r)
        self._update_status()
        self._highlight_all()

    def _set_thickness(self, thick):
        self.thickness = float(thick)
        self._update_status()
        self._highlight_all()

    def on_width_20_clicked(self, widget): self._set_width(20)
    def on_width_30_clicked(self, widget): self._set_width(30)
    def on_width_40_clicked(self, widget): self._set_width(40)
    def on_width_50_clicked(self, widget): self._set_width(50)
    def on_width_60_clicked(self, widget): self._set_width(60)
    def on_width_80_clicked(self, widget): self._set_width(80)

    def on_height_10_clicked(self, widget): self._set_height(10)
    def on_height_15_clicked(self, widget): self._set_height(15)
    def on_height_20_clicked(self, widget): self._set_height(20)
    def on_height_25_clicked(self, widget): self._set_height(25)
    def on_height_30_clicked(self, widget): self._set_height(30)
    def on_height_40_clicked(self, widget): self._set_height(40)

    def on_radius_0_clicked(self, widget): self._set_radius(0)
    def on_radius_2_clicked(self, widget): self._set_radius(2)
    def on_radius_3_clicked(self, widget): self._set_radius(3)
    def on_radius_5_clicked(self, widget): self._set_radius(5)
    def on_radius_8_clicked(self, widget): self._set_radius(8)
    def on_radius_10_clicked(self, widget): self._set_radius(10)

    def on_thick_2_clicked(self, widget): self._set_thickness(2)
    def on_thick_3_clicked(self, widget): self._set_thickness(3)
    def on_thick_4_clicked(self, widget): self._set_thickness(4)

    def on_refresh_clicked(self, widget):
        self._refresh_values()

    def on_run_clicked(self, widget):
        self._refresh_values()

        if self.width <= self.tool_dia:
            self._set_status("CHYBA: sirka musi byt vetsi nez prumer nastroje.")
            return
        if self.height <= self.tool_dia:
            self._set_status("CHYBA: vyska musi byt vetsi nez prumer nastroje.")
            return
        if self.corner_r < 0:
            self._set_status("CHYBA: radius rohu nemuze byt zaporny.")
            return
        max_radius = min(self.width, self.height) / 2.0
        if self.corner_r > max_radius:
            self._set_status("CHYBA: radius rohu je prilis velky.")
            return

        mdi = "o<rectangle_cut> call [%g] [%g] [%g] [%g] [%g] [%g] [%g] [%d]" % (
            self.width, self.height, self.corner_r, self.thickness, self.tool_no, self.tool_dia, self.feed, int(self.local_mode)
        )

        try:
            self.stat.poll()
            self._set_status("Posilam MDI: " + mdi)
            self.command.mode(linuxcnc.MODE_MDI)
            self.command.wait_complete(2.0)
            self.command.mdi(mdi)
            self.command.wait_complete(2.0)
            self._set_status("Odeslano: " + mdi)
        except Exception as e:
            self._set_status("CHYBA MDI: " + str(e))


def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]
