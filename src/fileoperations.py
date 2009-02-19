#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk

import os
from os.path import join, basename, exists

# TODO: Achten auf :/\* etc. in Dateiname!
# TODO: Fehler abfangen, fehlerwert zurückgeben, damit das Programm weitermachen kann

def error(message_text):
    dialog = gtk.MessageDialog(
                    None,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, 
                    gtk.BUTTONS_OK, 
                    message_text)
                    
    dialog.run()
    dialog.destroy()
                    
def remove_file(filename):
    try:
        os.remove(filename)
    except Exception, e:
        error("Fehler beim Löschen von %s (%s)." % (filename, e))
    
def rename_file(old_filename, new_filename):

    if old_filename == new_filename:
        error("Umbenennen: Die beiden Dateinamen stimmen überein. Dies ist vermutlich ein Bug! (%s)" % old_filename)
        return

    count = 1
    while exists(new_filename):        
        print "EXISTS ", count
        new_filename += ".%s" % count
        count += 1
    
    try:
        os.rename(old_filename, new_filename)
    except Exception, e:
        error("Fehler beim Umbenennen/Verschieben von %s nach %s (%s)." % (old_filename, new_filename, e))

def move_file(filename, target):
    rename_file(filename, join(target, basename(filename)))

def get_size(filename):
    """ Returns a file's size."""
    filestat = os.stat(filename)
    size = filestat.st_size
    
    return size

def get_date(filename):
    """ Returns a file's last changed date."""
    filestat = os.stat(filename)
    date = filestat.st_mtime
    
    return date
