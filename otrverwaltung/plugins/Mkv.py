#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import subprocess
import time
import os.path

from otrverwaltung.GeneratorTask import GeneratorTask
from otrverwaltung.pluginsystem import Plugin

from otrverwaltung.constants import Section

class Mkv(Plugin):
    Name = "MKV"
    Desc = "Wandelt avi-Dateien mit Hilfe von mkvmerge in mkv-Dateien um."
    Author = "Benjamin Elbers"
    Configurable = True
    Config = { 'mkvmerge': 'mkvmerge' }
        
    def enable(self):
        self.toolbutton = self.gui.main_window.add_toolbutton(gtk.image_new_from_file(self.get_path('mkv.png')), 'In Mkv umwandeln', [Section.VIDEO_UNCUT, Section.VIDEO_CUT, Section.ARCHIVE])
        self.toolbutton.connect('clicked', self.on_mkv_clicked)                        
        
    def disable(self):
        self.gui.main_window.remove_toolbutton(self.toolbutton)
    
    def configurate(self, dialog):
        dialog.vbox.set_spacing(4) 
        
        dialog.vbox.pack_start(gtk.Label("Name von mkvmerge:"), expand=False)
        entry_mkvmerge = gtk.Entry()
        dialog.vbox.pack_start(entry_mkvmerge, expand=False)
                
        def on_entry_mkvmerge_changed(widget, data=None):
            self.Config['mkvmerge'] = widget.get_text()
               
        entry_mkvmerge.connect('changed', on_entry_mkvmerge_changed)
           
        # current config
        entry_mkvmerge.set_text(self.Config['mkvmerge'])
        
        return dialog

    def on_mkv_clicked(self, widget, data=None):
        self.toolbutton.set_sensitive(False)
        filenames = self.gui.main_window.get_selected_filenames()
        self.gui.main_window.set_tasks_visible(True)

        self.success = 0
        self.errors ={}
                
        def mkvmerge():
            for count, filename in enumerate(filenames):           
                yield 0, count
                self.progress = 0
                p = subprocess.Popen([self.Config['mkvmerge'], "-o", os.path.splitext(filename)[0] + ".mkv", filename], stdout=subprocess.PIPE)
                p.stdout.readline()

                line = ""                            
                while p.poll() == None:
                    # read progress from stdout 
                    char = p.stdout.read(1)
                    line += char
                    progress = ''
                    if char == ':':
                        if "Error" in line or "Warning" in line:                            
                            break
                    
                        while char != '%':
                            char = p.stdout.read(1)
                            progress += char
                      
                        try:
                            self.progress = int(progress.strip(' %'))
                            yield 1, self.progress                                
                        except ValueError:
                            pass
                
                exit_code = p.poll()

                if exit_code == 0:
                    self.success += 1
                else:
                    error = p.stdout.readline()
                    try:
                        error = error.split(":")[1]
                    except IndexError:
                        pass
                        
                    if "unknown type" in error:
                        error = "Datei konnte nicht gelesen werden."
                    self.errors[filename] = error
                  
        def loop(state, argument):            
            if state == 0:
                self.gui.main_window.set_tasks_text("In Mkv Umwandeln %s/%s" % (str(argument + 1), str(len(filenames))))
            else:                
                self.gui.main_window.set_tasks_progress(argument)
        
        def complete():
            if len(self.errors) == 0:
                self.gui.main_window.change_status(0, "Erfolgreich %s/%s Dateien umgewandelt." % (str(self.success), str(len(filenames))))
            else:
                self.gui.main_window.change_status(0, "Erfolgreich %s/%s Dateien umgewandelt. (Fehler: %s)" % (str(self.success), str(len(filenames)), " ".join(self.errors.values())))
            
            self.gui.main_window.set_tasks_visible(False)                
            if self.success > 0:
                self.app.show_section(self.app.section)
            self.toolbutton.set_sensitive(True)
                        
        GeneratorTask(mkvmerge, loop, complete).start() 
