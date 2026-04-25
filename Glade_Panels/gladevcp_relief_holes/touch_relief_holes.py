#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import linuxcnc
import hal
import gtk

class HandlerClass:
    def __init__(self, halcomp, builder, useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.command = linuxcnc.command()

        self.diameter = 20.0
        self.thickness = 4.0
        self.tool_no = 4.0
        self.tool_dia = 1.0
        self.feed = 200.0

        self.dia_buttons = {
            10: "dia_10", 15: "dia_15", 20: "dia_20", 25: "dia_25", 30: "dia_30",
            35: "dia_35", 40: "dia_40", 45: "dia_45", 50: "dia_50", 55: "dia_55", 60: "dia_60"
        }
        self.thick_buttons = {2: "thick_2", 3: "thick_3", 4: "thick_4"}

        self._set_entry("entry_custom_dia", self.diameter)
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

    def _set_status(self, text):
        label = self._obj("label_status")
        if label:
            label.set_text(text)

    def _update_status(self):
        self._set_status(
            "Vybrano: otvor %.1f mm | preklizka %.1f mm | T%d | nastroj %.2f mm | F%d" %
            (self.diameter, self.thickness, int(self.tool_no), self.tool_dia, int(self.feed))
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
        self._update_status()
        self._highlight_all()

    def on_thick_2_clicked(self, widget): self._set_thickness(2)
    def on_thick_3_clicked(self, widget): self._set_thickness(3)
    def on_thick_4_clicked(self, widget): self._set_thickness(4)

    def on_refresh_clicked(self, widget):
        self.tool_no = self._get_float("entry_tool_no", self.tool_no)
        self.tool_dia = self._get_float("entry_tool_dia", self.tool_dia)
        self.feed = self._get_float("entry_feed", self.feed)
        self.diameter = self._get_float("entry_custom_dia", self.diameter)
        self._update_status()
        self._highlight_all()

    def _confirm(self):
        msg = (
            "Vyfrezovat otvor?\n\n"
            "Prumer otvoru: %.1f mm\n"
            "Tloustka preklizky: %.1f mm\n"
            "Nastroj: T%d\n"
            "Prumer nastroje: %.2f mm\n"
            "Feed: F%d" %
            (self.diameter, self.thickness, int(self.tool_no), self.tool_dia, int(self.feed))
        )
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title("Potvrzeni frezovani")
        result = dialog.run()
        dialog.destroy()
        return result == gtk.RESPONSE_OK

    def on_run_clicked(self, widget):
        self.on_refresh_clicked(widget)

        if self.diameter <= self.tool_dia:
            self._set_status("CHYBA: prumer otvoru musi byt vetsi nez prumer nastroje.")
            return

        if not self._confirm():
            self._set_status("Zruseno.")
            return

        mdi = "o<relief_hole> call [%.3f] [%.3f] [%.0f] [%.3f] [%.0f]" % (
            self.diameter, self.thickness, self.tool_no, self.tool_dia, self.feed
        )

        try:
            self.command.mode(linuxcnc.MODE_MDI)
            self.command.wait_complete()
            self.command.mdi(mdi)
            self._set_status("Spusteno: " + mdi)
        except Exception as e:
            self._set_status("CHYBA pri spusteni MDI: %s" % e)

def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]
