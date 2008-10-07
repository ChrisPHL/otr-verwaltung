#!/bin/sh

gtk-builder-convert -r "main_window"            otr.glade gui/main_window.ui
gtk-builder-convert -r "status_menu"            otr.glade gui/status_menu.ui
gtk-builder-convert -r "preferences_window"     otr.glade gui/preferences_window.ui
gtk-builder-convert -r "dialog_email_password"  otr.glade gui/dialog_email_password.ui
gtk-builder-convert -r "dialog_archive"         otr.glade gui/dialog_archive.ui
gtk-builder-convert -r "dialog_conclusion"      otr.glade gui/dialog_conclusion.ui
gtk-builder-convert -r "dialog_cutlist"         otr.glade gui/dialog_cutlist.ui
gtk-builder-convert -r "dialog_cut"             otr.glade gui/dialog_cut.ui
gtk-builder-convert -r "dialog_rename"          otr.glade gui/dialog_rename.ui
gtk-builder-convert -r "dialog_close_minimize"  otr.glade gui/dialog_close_minimize.ui
