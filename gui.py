#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# OTR-Verwaltung 0.9 (Beta 1)
# Author: Benjamin Elbers
#         elbersb@googlemail.com
#
#
# LICENSE: CREATIVE COMMONS
#          Attribution-Noncommercial-Share Alike 2.0 Generic
# http://creativecommons.org/licenses/by-nc-sa/2.0/
#

import sys
import base64
import os
import time

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    import pango
except:
    print "PyGTK missing."
    sys.exit(-1)
    
from constants import Section, Action, Save_Email_Password, Cut_action, Status

class GUI:
    def construct_dict(self, builder, descriptions):  
        return_dict = dict()     
        for desc in descriptions:
            return_dict[desc] = builder.get_object(desc)
                    
        return return_dict

    def __init__(self, app_instance, builder_file):   
        """ Setup gui. Connect signals """
               
        # configs
        self.app = app_instance
    
        # init builder     
        builder = gtk.Builder()


            
        builder.add_from_file(builder_file)
                
        # dicts for widgets
        self.windows = self.construct_dict(builder, [
            'main_window', 
            'preferences_window',
            'dialog_email_password',
            'dialog_action',
            'dialog_archive',
            'dialog_conclusion',
            'dialog_cut',
            'dialog_cutlist',
            'dialog_rename'
            ])
            
        self.windows['main_window'].realize()
        self.windows['main_window'].window.set_decorations(gtk.gdk.DECOR_ALL & ~gtk.gdk.DECOR_MAXIMIZE)
            
        self.main_window = self.construct_dict(builder, [
            'toolbar',
            'toolbuttonDecode',
            'toolbuttonDecodeAll',
            'toolbuttonCut',
            'toolbuttonCutAll',
            'toolbuttonDecodeAndCut',
            'toolbuttonDecodeAndCutAll',    

            # sidebar
            'entrySearch',
            'radioUndecoded',            
            'separator1',
            'labelAvi',
            'radioUncut',
            'radioCut',
            'separator2',
            'radioArchive',
            'separator3',
            'radioTrash',
            'labelOtrkeysCount',
            'labelUncutCount',
            'labelCutCount',
            'labelArchiveCount',
            'labelTrashCount',

            'labelMessage',
            'treeviewFiles'
            ])
        
        
        self.preferences_window = self.construct_dict(builder, [
            'notebook',
 
            # Allgemein
            'checkCut',
            'checkTest',
            # Speicherorte
            'folderArchive',
            # Dekodieren
            'filechooserDecoder',
            'entryEMail',
            'entryPassword',      
            'checkCorrect'
            # Schneiden
            ])
                       
        self.dialog_email_password = self.construct_dict(builder, [           
            'entryDialogEMail',
            'entryDialogPassword'
            ])
            
        self.dialog_action = self.construct_dict(builder, [
            'labelCaption',
            'labelActionDecode',
            'labelActionCut',
            'progressbar_decode',
            'progressbar_cut',
            'dialog_action_buttonCancel'
            ])
        
        self.dialog_conclusion = self.construct_dict(builder, [
            'buttonBack',
            'buttonForward',
            'buttonClose',
            'labelCount',
            'tableConclusion',
            'labelConclusionFilename',
            'labelConclusionCutStatus',
            'labelConclusionDecodeStatus',
            'labelConclusionCut',
            'labelConclusionDecode',
            'vboxRating',
            'vboxButtons',
            'radiobuttonRate0',
            'radiobuttonRate1',
            'radiobuttonRate2',
            'radiobuttonRate3',
            'radiobuttonRate4',
            'radiobuttonRate5'
            ])
            
        self.dialog_archive = self.construct_dict(builder, [
            'labelFiles',
            'treeviewFolders',
            'treeviewFolders_store',
            'treeviewFilesRename',
            'treeviewFilesRename_store'
            ])
                
        self.dialog_cut = self.construct_dict(builder, [
            'labelCutFile',
            'radioCutBestCutlist',
            'radioCutChooseCutlist',
            'radioCutManually',
            'labelWarning'
            ])
        
        self.dialog_cutlist = self.construct_dict(builder, [
            'labelCutlistFile',
            'treeviewCutlists',
            'treeviewCutlists_store'
            ])
            
        self.dialog_rename = self.construct_dict(builder, [
            'vboxRename'
            ])
                              
        # setup different guis
        self.setup_main_window(builder)
        self.setup_preferences_window(builder)
        self.setup_dialog_archive(builder)          
        self.setup_dialog_cutlist(builder)
        self.setup_dialog_cut(builder)
        self.setup_dialog_conclusion(builder)
                       
        # set icons
        for window in self.windows:
            self.windows[window].set_icon(gtk.gdk.pixbuf_new_from_file(self.get_image_path('icon3.png')))

        # connect signals    
        builder.connect_signals(self)
        
       
    # run method     
    def run(self):
        self.windows['main_window'].show()        

        if self.app.config_dic['folders']['new_otrkeys'] == "":      
            self.message_box("Dies ist offenbar das erste Mal, dass OTR-Verwaltung gestartet wird.\n\nEs müssen zunächst einige wichtige Einstellungen vorgenommen werden. Klicken Sie dazu auf OK.", gtk.MESSAGE_INFO, gtk.BUTTONS_OK)  
            self.windows['preferences_window'].show()
        gtk.main()

    ###
    ### "Setup windows" methods
    ###

    def get_image_path(self, image):
        return os.path.join(os.path.join(sys.path[0], 'images'), image)

    def setup_main_window(self, builder):
        # sidebar
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU)
        builder.get_object('buttonClear').set_image(image)
    
        # tool buttons           
        images = [
            gtk.image_new_from_file(self.get_image_path('decode.png')),
            gtk.image_new_from_file(self.get_image_path('decodeandcut.png')),
            gtk.image_new_from_file(self.get_image_path('delete.png')),
            gtk.image_new_from_file(self.get_image_path('archive.png')),
            gtk.image_new_from_file(self.get_image_path('cut.png')),
            gtk.image_new_from_file(self.get_image_path('play.png')),
            gtk.image_new_from_file(self.get_image_path('restore.png')),
            gtk.image_new_from_file(self.get_image_path('rename.png')),
            gtk.image_new_from_file(self.get_image_path('new_folder.png')),
            gtk.image_new_from_file(self.get_image_path('play.png'))                        
        ]
                       
        for img in images:
            img.show()   
                       
        toolbar_buttons = {
                'decode':       gtk.ToolButton(images[0], "Dekodieren"),
                'decodeandcut': gtk.ToolButton(images[1], "Dekodieren und Schneiden"),
                'delete':       gtk.ToolButton(images[2], "In den Müll verschieben"),
                'archive':      gtk.ToolButton(images[3], "Archivieren"),
                'cut':          gtk.ToolButton(images[4], "Schneiden"),
                'play':         gtk.ToolButton(images[5], "Abspielen"),
                'restore':      gtk.ToolButton(images[6], "Wiederherstellen"),
                'rename':       gtk.ToolButton(images[7], "Umbenennen"),
                'new_folder':   gtk.ToolButton(images[8], "Neuer Ordner"),
                'cut_play':     gtk.ToolButton(images[9], "Geschnitten Abspielen")
            }

        toolbar_buttons['decode'].connect("clicked", self.on_toolbutton_clicked, Action.DECODE)
        toolbar_buttons['decodeandcut'].connect("clicked", self.on_toolbutton_clicked, Action.DECODEANDCUT)
        toolbar_buttons['delete'].connect("clicked", self.on_toolbutton_clicked, Action.DELETE)
        toolbar_buttons['archive'].connect("clicked", self.on_toolbutton_clicked, Action.ARCHIVE)
        toolbar_buttons['cut'].connect("clicked", self.on_toolbutton_clicked, Action.CUT)
        toolbar_buttons['play'].connect("clicked", self.on_toolbutton_clicked, Action.PLAY)
        toolbar_buttons['restore'].connect("clicked", self.on_toolbutton_clicked, Action.RESTORE)   
        toolbar_buttons['rename'].connect("clicked", self.on_toolbutton_clicked, Action.RENAME)        
        toolbar_buttons['new_folder'].connect("clicked", self.on_toolbutton_clicked, Action.NEW_FOLDER)                                    
        toolbar_buttons['cut_play'].connect("clicked", self.on_toolbutton_clicked, Action.CUT_PLAY)  
          
        # create sets of toolbuttons
        self.sets_of_toolbars = {
            Section.OTRKEY :    [ toolbar_buttons['decode'], toolbar_buttons['decodeandcut'], toolbar_buttons['delete'] ],
            Section.AVI_UNCUT:  [ toolbar_buttons['cut'], toolbar_buttons['delete'], toolbar_buttons['archive'], toolbar_buttons['play'], toolbar_buttons['cut_play'] ],
            Section.AVI_CUT:    [ toolbar_buttons['archive'], toolbar_buttons['delete'], toolbar_buttons['cut'], toolbar_buttons['play'], toolbar_buttons['rename'] ],
            Section.ARCHIVE:    [ toolbar_buttons['cut'], toolbar_buttons['delete'], toolbar_buttons['play'], toolbar_buttons['rename'], toolbar_buttons['new_folder'] ],
            Section.TRASH:      [ toolbar_buttons['delete'], toolbar_buttons['restore'] ]
        }
        
        self.dialog_email_password['entryDialogPassword'].set_visibility(False)
              
        # connect other signals
        self.main_window['radioUndecoded'].connect('clicked', self.on_sidebar_toggled, Section.OTRKEY)
        self.main_window['radioUncut'].connect('clicked', self.on_sidebar_toggled, Section.AVI_UNCUT)
        self.main_window['radioCut'].connect('clicked', self.on_sidebar_toggled, Section.AVI_CUT)
        self.main_window['radioArchive'].connect('clicked', self.on_sidebar_toggled, Section.ARCHIVE)  
        self.main_window['radioTrash'].connect('clicked', self.on_sidebar_toggled, Section.TRASH)
        
        # change background of sidebar
        eventbox = builder.get_object('eventboxSidebar')
        cmap = eventbox.get_colormap()
        colour = cmap.alloc_color("gray")
        style = eventbox.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = colour
        eventbox.set_style(style)
        
        # change font of sidebar
        builder.get_object('labelFilter').modify_font(pango.FontDescription("bold 12"))
        
        for label in ['labelOtrkeysCount', 'labelUncutCount', 'labelCutCount', 'labelArchiveCount', 'labelTrashCount', 'labelSearch',   'labelOtrkey', 'labelAvi']:
            builder.get_object(label).modify_font(pango.FontDescription("bold"))
        
        # setup the file treeview
        treeview = self.main_window['treeviewFiles']
        self.main_window['treeviewFiles_store'] = gtk.TreeStore(object, long, float)             
        treeview.set_model(self.main_window['treeviewFiles_store'])
            
        # constants for 
        self.FILENAME = 0
        self.SIZE =     1
        self.DATE =     2
                           
        # create the TreeViewColumns to display the data
        column_names = ['Dateiname', 'Größe', 'Geändert']
        tvcolumns = [None] * len(column_names)
                       
        # first column: pixbuf and filename
        cell_renderer_pixbuf = gtk.CellRendererPixbuf()
        tvcolumns[0] = gtk.TreeViewColumn(column_names[0], cell_renderer_pixbuf)
        cell_renderer_text_name = gtk.CellRendererText()
        tvcolumns[0].pack_start(cell_renderer_text_name, False)
        tvcolumns[0].set_cell_data_func(cell_renderer_pixbuf, self.file_pixbuf)
        tvcolumns[0].set_cell_data_func(cell_renderer_text_name, self.file_name)

        # second column: size
        cell_renderer_text_size = gtk.CellRendererText()
        cell_renderer_text_size.set_property('xalign', 1.0) 
        tvcolumns[1] = gtk.TreeViewColumn(column_names[1], cell_renderer_text_size, text=1)
        tvcolumns[1].set_cell_data_func(cell_renderer_text_size, self.file_size)        
        
        # third column: date
        cell_renderer_text_date = gtk.CellRendererText()
        tvcolumns[2] = gtk.TreeViewColumn(column_names[2], cell_renderer_text_date, text=2)
        tvcolumns[2].set_cell_data_func(cell_renderer_text_date, self.file_date)        
                
        # append the columns
        for col in tvcolumns:
            col.set_resizable(True)
            treeview.append_column(col)
        
        # allow multiple selection
        treeselection = treeview.get_selection()
        treeselection.set_mode(gtk.SELECTION_MULTIPLE)
               
        # sorting
        self.main_window['treeviewFiles_store'].set_sort_func(0, self.sort, None)
        self.main_window['treeviewFiles_store'].set_sort_column_id(0, gtk.SORT_ASCENDING)
        
        # load pixbufs for treeview
        self.pix_avi = gtk.gdk.pixbuf_new_from_file(self.get_image_path('avi.png'))      
        self.pix_otrkey = gtk.gdk.pixbuf_new_from_file(self.get_image_path('decode.png'))
        self.pix_folder = gtk.gdk.pixbuf_new_from_file(self.get_image_path('folder.png'))
        
    def setup_preferences_window(self, builder):
        # preferences fonts (little explanations)
        labels = [  builder.get_object('labelDescNewOtrkeys'),
                    builder.get_object('labelDescTrash'),
                    builder.get_object('labelBestCutlist'),
                    builder.get_object('labelChooseCutlist'),
                    builder.get_object('labelManually'),
                    builder.get_object('labelDescAvidemux')]
        for label in labels:
            label.modify_font(pango.FontDescription("8"))            
        
        builder.get_object('labelHeadline').modify_font(pango.FontDescription("bold"))
          
        # fill combobox of player
        player_store = gtk.ListStore(str)
        player_store.append(["vlc"])
        player_store.append(["totem"])
        player_store.append(["mplayer"])
        builder.get_object('comboboxPlayer').set_model(player_store)
        builder.get_object('comboboxPlayer').set_text_column(0)
        builder.get_object('comboboxentry-player').set_text(self.app.config_dic['play']['player'])
        
        # fill combobox of mplayer
        mplayer_store = gtk.ListStore(str)
        mplayer_store.append(["mplayer"])
        builder.get_object('comboboxMPlayer').set_model(mplayer_store)
        builder.get_object('comboboxMPlayer').set_text_column(0)
        builder.get_object('comboboxentry-mplayer').set_text(self.app.config_dic['play']['mplayer'])
        
        # fill combobox avidemux
        avidemux_store = gtk.ListStore(str)
        avidemux_store.append(["avidemux"])
        avidemux_store.append(["avidemux2"])        
        builder.get_object('comboboxAvidemux').set_model(avidemux_store)
        builder.get_object('comboboxAvidemux').set_text_column(0)
        builder.get_object('comboboxentry-avidemux').set_text(self.app.config_dic['cut']['avidemux'])
        
        # fill combobox servers
        server_store = gtk.ListStore(str)
        server_store.append(["http://cutlist.de/"])
        server_store.append(["http://cutlist.mbod.net/"])
        server_store.append(["http://cutlist.at/"])
        builder.get_object('comboboxServer').set_model(server_store)
        builder.get_object('comboboxServer').set_text_column(0)
        builder.get_object('comboboxentry-server').set_text(self.app.config_dic['cut']['server'])
        
        # fill values from config_dic
               
        # check boxes on common tab
        builder.get_object('checkCut').set_active(bool(self.app.config_dic['common']['activate_cut']))
        builder.get_object('checkArchive').set_active(bool(self.app.config_dic['common']['use_archive']))

        # folder choosers on folders tab           
        builder.get_object('folderNewOtrkeys').set_current_folder(self.app.config_dic['folders']['new_otrkeys'])
        builder.get_object('folderTrash').set_current_folder(self.app.config_dic['folders']['trash'])
        builder.get_object('folderArchive').set_current_folder(self.app.config_dic['folders']['archive'])     
              
        # decode tab
        self.preferences_window['filechooserDecoder'].set_filename(self.app.config_dic['decode']['path'])  
        if self.app.config_dic['decode']['save_email_password'] == Save_Email_Password.DONT_SAVE:
            builder.get_object('radioDontSave').set_active(True)
            self.on_radioDontSave_toggled(builder.get_object('radioDontSave'))
        else:
            builder.get_object('radioSave').set_active(True)
            self.preferences_window['entryEMail'].set_text(self.app.config_dic['decode']['email'])
            self.preferences_window['entryPassword'].set_text(base64.b64decode(self.app.config_dic['decode']['password']))
           
        self.preferences_window['entryPassword'].set_visibility(False)
            
        self.preferences_window['checkCorrect'].set_active(bool(self.app.config_dic['decode']['correct']))
    
        # radio buttons on cut tab
        radiobuttons = [ 'radioAsk', 'radioBestCutlist', 'radioChooseCutlist', 'radioManually' ]
        builder.get_object(radiobuttons[self.app.config_dic['cut']['cut_action']]).set_active(True)
    
        builder.get_object('checkbutton_use_cut_play').set_active(bool(self.app.config_dic['play']['use_cut_play']))
    
    def setup_dialog_archive(self, builder):
        # create folder treestore
        treeview = self.dialog_archive['treeviewFolders']
        self.dialog_archive['treeviewFolders_store'] = gtk.TreeStore(str)             
        treeview.set_model(self.dialog_archive['treeviewFolders_store'])

        cell_renderer_folder_name = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn(None, cell_renderer_folder_name, text = 0)
        tvcolumn.set_cell_data_func(cell_renderer_folder_name, self.folder_name)        
        
        treeview.append_column(tvcolumn)

        # create files-rename liststore
        treeview = self.dialog_archive['treeviewFilesRename']
        self.dialog_archive['treeviewFilesRename_store'] = gtk.ListStore(str)
        treeview.set_model(self.dialog_archive['treeviewFilesRename_store'])
        
        cell_renderer_new = gtk.CellRendererText()
        cell_renderer_new.set_property('editable', True)
        #cell_renderer_new.set_property('ellipsize', pango.ELLIPSIZE_END)
        cell_renderer_new.connect('edited', self.new_name_cell_edited, self.dialog_archive['treeviewFilesRename_store'])
        tvcolumn_new = gtk.TreeViewColumn("Neuer Name (Doppelklick zum Bearbeiten):", cell_renderer_new, text=0)     
        
        treeview.append_column(tvcolumn_new)
        
        selection = treeview.get_selection()

        # change label
        self.dialog_archive['labelFiles'].modify_font(pango.FontDescription("bold"))        
    
    def setup_dialog_cutlist(self, builder):   
        # font
        self.dialog_cutlist['labelCutlistFile'].modify_font(pango.FontDescription("bold"))          
        
        # setup the file treeview
        treeview = self.dialog_cutlist['treeviewCutlists']
        self.dialog_cutlist['treeviewCutlists_store'] = gtk.ListStore(
            str, # 0 id
            str, # 1 author
            str, # 2 ratingbyauthor
            str, # 3 rating
            str, # 4 ratingcount
            str, # 5 cuts
            str, # 6 actualcontent
            str, # 7 usercomment
            str, # 8 filename
            str, # 9 withframes
            str, # 10 withtime
            str # 11 duration
            )             
        treeview.set_model(self.dialog_cutlist['treeviewCutlists_store'])
            
        # create the TreeViewColumns to display the data
        column_names = ['Autor', 'Autorenwertung', 'Benutzerwertung', 'Benutzerkommentar' ]
        tvcolumns = [None] * len(column_names)
        
        renderer_left = gtk.CellRendererText()
        renderer_left.set_property('xalign', 0.0) 

        tvcolumns[0] = gtk.TreeViewColumn(column_names[0], renderer_left, text=1)
        tvcolumns[1] = gtk.TreeViewColumn(column_names[1], renderer_left, text=2)       
        tvcolumns[2] = gtk.TreeViewColumn(column_names[2], renderer_left, text=3)
        tvcolumns[3] = gtk.TreeViewColumn(column_names[3], renderer_left, text=7)        
        
        # append the columns
        for col in tvcolumns:
            col.set_resizable(True)        
            treeview.append_column(col)
    
    def setup_dialog_cut(self, builder):   
        self.dialog_cut['labelWarning'].modify_font(pango.FontDescription("8"))          
        self.dialog_cut['labelCutFile'].modify_font(pango.FontDescription("bold"))
    
    def setup_dialog_conclusion(self, builder):   
        self.dialog_conclusion['labelConclusionFilename'].modify_font(pango.FontDescription("bold"))
        
        for radio in range(6):
            self.dialog_conclusion["radiobuttonRate"+str(radio)].connect('toggled', self.on_radiobuttonRating_toggled, radio)

    ###
    ### helper methods
    ###
    
    def message_box(self, message_text, message_type, buttons):
        dialog = gtk.MessageDialog(
                self.windows['main_window'], 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                message_type,
                buttons,
                message_text)
                
        result = dialog.run()
        dialog.destroy()
    
    def question_box(self, message_text):
        dialog = gtk.MessageDialog(
                self.windows['main_window'], 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, 
                gtk.BUTTONS_YES_NO,
                message_text)
                
        result = dialog.run()
        dialog.destroy()
        
        if result==gtk.RESPONSE_YES:
            return True
        else:
            return False    
          
    ###
    ### MAIN_WINDOW
    ###
       
    def on_menuHelpAbout_activate(self, widget, data=None):
        about_dialog = gtk.AboutDialog()        
        about_dialog.set_transient_for(self.windows['main_window'])
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("OTR-Verwaltung")
        about_dialog.set_version("0.1")
        about_dialog.set_comments("Zum Verwalten von Dateien von onlinetvrecorder.com.")
        about_dialog.set_copyright("Copyright \xc2\xa9 2008 Benjamin Elbers")
        about_dialog.set_authors(["Benjamin Elbers <elbersb@googlemail.com>"])
        about_dialog.set_logo_icon_name(gtk.STOCK_EDIT)            
        about_dialog.run()
        about_dialog.destroy()
    
    def on_menuEditPreferences_activate(self, widget, data=None):
        self.windows['preferences_window'].show()
    
    def on_MainWindow_destroy(self, widget, data=None):        
        gtk.main_quit()
        
    def on_menuFileQuit_activate(self, widget, data=None):        
        gtk.main_quit()
    
    def on_menuEditSearch_activate(self, widget, data=None):
        self.main_window['entrySearch'].grab_focus()
    
    # toolbar actions
    def on_toolbutton_clicked(self, button, action):
        """ Raised when a toolbutton is being clicked. """
                
        filenames = self.get_selected_filenames() 
        self.app.perform_action(action, filenames)             
              
    def set_toolbar(self, section):
        for toolbutton in self.main_window['toolbar'].get_children():
            self.main_window['toolbar'].remove(toolbutton)
        
        for toolbutton in self.sets_of_toolbars[section]: 
            toolbutton.show()      
            self.main_window['toolbar'].insert(toolbutton, -1)
    
    def get_selected_filenames(self):
        """ Return the selected filenames """
        selection = self.main_window['treeviewFiles'].get_selection()
            
        def selected_row(model, path, iter, filenames):
            filenames += [self.get_filename(iter)]
        
        filenames = []        
        selection.selected_foreach(selected_row, filenames)      

        return filenames

    # sidebar
    def on_sidebar_toggled(self, widget, section):
        if widget.get_active() == True:
            self.app.show_section(section)            
    
    def on_buttonClear_clicked(self, widget, data=None):
        self.main_window['entrySearch'].set_text("")
    
    def on_entrySearch_changed(self, widget, data=None):
        search = widget.get_text()

        if search == "":
            self.app.stop_search()
            
            for label in ['labelOtrkeysCount', 'labelUncutCount', 'labelCutCount', 'labelArchiveCount', 'labelTrashCount']:
                self.main_window[label].set_text("")
        else:
            counts_of_section = self.app.start_search(search)
                  
            self.main_window['labelOtrkeysCount'].set_text(counts_of_section[Section.OTRKEY])
            self.main_window['labelUncutCount'].set_text(counts_of_section[Section.AVI_UNCUT])
            self.main_window['labelCutCount'].set_text(counts_of_section[Section.AVI_CUT])                            
            self.main_window['labelArchiveCount'].set_text(counts_of_section[Section.ARCHIVE])    
            self.main_window['labelTrashCount'].set_text(counts_of_section[Section.TRASH])

    # related to treeview on main window  
    def append_row_treeviewFiles(self, parent, filename):       
        filestat = os.stat(filename)
        date = filestat.st_mtime
        size = os.path.getsize(filename)
        
        data = [filename, size, date]
    
        iter = self.main_window['treeviewFiles_store'].append(parent, data)
        return iter
      
    def get_filename(self, iter):
        return self.main_window['treeviewFiles_store'].get_value(iter, self.FILENAME)
          
    def sort(self, model, iter1, iter2, data):
        # sort_func should return: -1 if the iter1 row should precede the iter2 row; 0, if the rows are equal; and, 1 if the iter2 row should precede the iter1 row
        filename_iter1 = self.get_filename(iter1)    
        filename_iter2 = self.get_filename(iter2)
        # why???
        if filename_iter2 == None:
            return -1
        
        iter1_isdir = os.path.isdir(filename_iter1)
        iter2_isdir = os.path.isdir(filename_iter2)
        
        if iter1_isdir and iter2_isdir: # both are folders
            # put names into array
            folders = [ filename_iter1, filename_iter2 ]
            # sort them
            folders.sort()
            # check if the first element is still iter1
            if folders[0] == filename_iter1:
                return -1
            else:
                return 1
        elif iter1_isdir: # only iter1 is a folder
            return -1
        elif iter2_isdir: # only iter2 is a folder
            return 1
        else: # none of them is a folder
            return 0
            
    # displaying methods for treeviewFiles
    def file_pixbuf(self, column, cell, model, iter):
        filename = model.get_value(iter, self.FILENAME)
        
        if os.path.isdir(filename):
            cell.set_property('pixbuf', self.pix_folder)
        else:
            if filename.endswith('.otrkey'):
                cell.set_property('pixbuf', self.pix_otrkey)
            else:
                cell.set_property('pixbuf', self.pix_avi)

    def file_name(self, column, cell, model, iter):            
        cell.set_property('text', os.path.basename(model.get_value(iter, self.FILENAME)))

    def file_size(self, column, cell, model, iter):
        filename = model.get_value(iter, self.FILENAME)
        if os.path.isdir(filename):
            cell.set_property('text', '')
        else:
            cell.set_property('text', self.humanize_size(model.get_value(iter, self.SIZE)))

    def file_date(self, column, cell, model, iter):
        cell.set_property('text', time.strftime("%a, %d.%m.%Y, %H:%M", time.localtime(model.get_value(iter, self.DATE))))
    
    def humanize_size(self, size):
        abbrevs = [
            (1<<30L, 'GB'), 
            (1<<20L, 'MB'), 
            (1<<10L, 'k'),
            (1, '')
        ]

        for factor, suffix in abbrevs:
            if size > factor:
                break
        return `int(size/factor)` + ' ' + suffix
    
    def on_header_checkbox_clicked(self, tvcolumn):
        tvcolumn.get_widget().set_active(not tvcolumn.get_widget().get_active())

        self.main_window['treeviewFiles_store'].foreach(self.foreach_toggle_checkbox, tvcolumn.get_widget().get_active())

    def foreach_toggle_checkbox(self, model, path, iter, user_data):
        # set boolean value in first column
        model.set_value(iter, self.CHECK, user_data)

    def on_tv_checkbox_clicked(self, cell, path, model):
        model[path][self.CHECK] = not model[path][self.CHECK]
        self.set_checkbox_children(model[path], model[path][self.CHECK])

    # set value recursively
    def set_checkbox_children(self, treemodelrow, value):
        for row in treemodelrow.iterchildren():
            row[self.CHECK] = value
            self.set_checkbox_children(row, value)
    
    #
    # PREFERENCES_WINDOW
    #
    
    def on_preferences_buttonClose_clicked(self, widget, data=None):    
        self.windows['preferences_window'].hide()    

    def on_preferences_window_delete_event(self, window, event):        
        window.hide()
        return True
        
    # common tab
    # check box toggled save status to config_dic
    def on_preferences_checkCut_toggled(self, widget, data=None):
        self.app.config_dic['common']['activate_cut'] = int(widget.get_active())
        
    def on_preferences_checkArchive_toggled(self, widget, data=None):          
        self.app.config_dic['common']['use_archive'] = int(widget.get_active())
               
    # folders tab
    # folder changed, save to config dictionary
    def on_folderNewOtrkeys_current_folder_changed(self, widget, data=None):        
        self.app.config_dic['folders']['new_otrkeys'] = widget.get_filename()
        self.app.show_section(self.app.section)
    
    def on_folderTrash_current_folder_changed(self, widget, data=None):
        self.app.config_dic['folders']['trash'] = widget.get_filename()
        self.app.show_section(self.app.section)

    def on_folderArchive_current_folder_changed(self, widget, data=None):        
        self.app.config_dic['folders']['archive'] = widget.get_filename()
        self.app.show_section(self.app.section)
                
    # decode tab
    def on_filechooserDecoder_file_set(self, widget, data=None):
        self.app.config_dic['decode']['path'] = widget.get_filename()      
    
    def on_radioDontSave_toggled(self, widget, data=None):
        if widget.get_active() == True:
            self.app.config_dic['decode']['save_email_password'] = Save_Email_Password.DONT_SAVE
            self.preferences_window['entryEMail'].set_text("")
            self.preferences_window['entryEMail'].set_sensitive(False)
            self.preferences_window['entryPassword'].set_text("")
            self.preferences_window['entryPassword'].set_sensitive(False)
        
    def on_radioSave_toggled(self, widget, data=None):
        if widget.get_active() == True:
            self.app.config_dic['decode']['save_email_password'] = Save_Email_Password.SAVE
            self.preferences_window['entryEMail'].set_sensitive(True)
            self.preferences_window['entryPassword'].set_sensitive(True)
            
    def on_entryEMail_changed(self, widget, data=None):
        self.app.config_dic['decode']['email'] = widget.get_text()
        
    def on_entryPassword_changed(self, widget, data=None):
        self.app.config_dic['decode']['password'] = base64.b64encode(widget.get_text())
    
    def on_checkCorrect_toggled(self, widget, data=None):
        self.app.config_dic['decode']['correct'] = int(widget.get_active())    
  
    # cut tab
    def on_radioAsk_toggled(self, widget, data=None):
        if widget.get_active()==True:
            self.app.config_dic['cut']['cut_action'] = Cut_action.ASK
            
    def on_radioBestCutlist_toggled(self, widget, data=None):
        if widget.get_active()==True:
           self.app.config_dic['cut']['cut_action'] = Cut_action.BEST_CUTLIST
                
    def on_radioChooseCutlist_toggled(self, widget, data=None):
        if widget.get_active()==True:
            self.app.config_dic['cut']['cut_action'] = Cut_action.CHOOSE_CUTLIST        
                
    def on_radioManually_toggled(self, widget, data=None):
        if widget.get_active()==True:
            self.app.config_dic['cut']['cut_action'] = Cut_action.MANUALLY

    def on_comboboxentry_avidemux_changed(self, widget, data=None):
        self.app.config_dic['cut']['avidemux'] = widget.get_text()
    
    def on_comboboxentry_server_changed(self, widget, data=None):
        self.app.config_dic['cut']['server'] = widget.get_text()
        
    # play tab
    def on_comboboxentry_player_changed(self, widget, data=None):
        self.app.config_dic['play']['player'] = widget.get_text()
    
    def on_comboboxentry_mplayer_changed(self, widget, data=None):
        self.app.config_dic['play']['mplayer'] = widget.get_text()      
        
    def on_checkbutton_use_cut_play_toggled(self, widget, data=None):
        self.app.config_dic['play']['use_cut_play'] = int(widget.get_active())
    
    #
    # DIALOG ACTION
    #
    def on_dialog_action_buttonCancel_clicked(self, widget, user_data=None):
        if self.question_box("Wirklich abbrechen?"):
            self.windows['dialog_action'].hide()
    
    def build_action_window(self, filenames, action):
        dialog = self.windows['dialog_action']

        # clean up  
        for widget in [self.dialog_action['labelActionDecode'], self.dialog_action['progressbar_decode'], self.dialog_action['labelActionCut'], self.dialog_action['progressbar_cut']]:
            widget.show()
            
        self.dialog_action['progressbar_decode'].set_fraction(0)
        self.dialog_action['progressbar_cut'].set_fraction(0)
        
        message = "Es "
        if len(filenames)==1:
            message += "wird 1 Datei "
        else:
            message += "werden %s Dateien " % len(filenames)
  
        if action==Action.DECODE:
            for widget in [self.dialog_action['labelActionCut'], self.dialog_action['progressbar_cut']]:
                widget.hide()
            self.dialog_action['labelCaption'].set_text(message + "dekodiert.")
            
        elif action==Action.CUT:
            for widget in [self.dialog_action['labelActionDecode'], self.dialog_action['progressbar_decode']]:
                widget.hide()
            self.dialog_action['labelCaption'].set_text(message + "geschnitten.")
            
        elif action==Action.DECODEANDCUT:
            self.dialog_action['labelCaption'].set_text(message + "dekodiert und geschnitten.")
                                            
        return dialog
        
    #
    # DIALOG CONCLUSION
    #                      
    def build_conclusion_dialog(self, filenames_action_status, action):
        dialog = self.windows['dialog_conclusion']

        dialog.show_all()
        for radio in ['radiobuttonRate0', 'radiobuttonRate1', 'radiobuttonRate2', 'radiobuttonRate3', 'radiobuttonRate4', 'radiobuttonRate5' ]:
            self.dialog_conclusion[radio].set_sensitive(False)
        
        self.action = action
        if self.action == Action.DECODE or self.action == Action.DECODEANDCUT:
            self.dialog_conclusion['labelConclusionCutStatus'].hide()
            self.dialog_conclusion['labelConclusionCut'].hide()
                
            # hide play button and rating
            self.dialog_conclusion['vboxRating'].hide()
            self.dialog_conclusion['vboxButtons'].hide()
                
        if self.action == Action.CUT or self.action == Action.DECODEANDCUT:
            self.dialog_conclusion['labelConclusionDecodeStatus'].hide()
            self.dialog_conclusion['labelConclusionDecode'].hide()   
          
        self.filenames_action_status = []
        # build list from dict
        count = -1
        for filename in filenames_action_status:
            count += 1
            self.filenames_action_status.append({ 'filename': filename, 'action_status' : filenames_action_status[filename], 'rate': -1 })
                
        self.show_conclusion(0)       
        return dialog        
        
    def on_buttonConclusionPlay_clicked(self, widget, data=None):        
        status, data = self.filenames_action_status[self.conclusion_iter]['action_status'][Action.CUT]
        filename = data[0]

        self.app.perform_action(Action.PLAY, [filename])      
        
    def on_radiobuttonRating_toggled(self, widget, rate):
        if widget.get_active()==True:
            print "Changed rate to ", str(rate)
            self.filenames_action_status[self.conclusion_iter]['rate'] = rate 
       
    def on_checkbuttonRate_toggled(self, widget, data=None):
        status = widget.get_active()
        if status==True:
            self.filenames_action_status[self.conclusion_iter]['rate'] = 0
            self.dialog_conclusion['radiobuttonRate0'].set_active(True)
        else:
            self.filenames_action_status[self.conclusion_iter]['rate'] = -1
        
        for radio in ['radiobuttonRate0', 'radiobuttonRate1', 'radiobuttonRate2', 'radiobuttonRate3', 'radiobuttonRate4', 'radiobuttonRate5' ]:
            self.dialog_conclusion[radio].set_sensitive(status)
        
    def on_buttonBack_clicked(self, widget, data=None):
        self.show_conclusion(self.conclusion_iter - 1)
    
    def on_buttonForward_clicked(self, widget, data=None):
        self.show_conclusion(self.conclusion_iter + 1)
        
    def show_conclusion(self, new_iter):
        self.conclusion_iter = new_iter
        
        self.dialog_conclusion['labelCount'].set_text("Zeige Datei %s/%s" % (self.conclusion_iter + 1, len(self.filenames_action_status)))
        
        # enable back-button?
        if self.conclusion_iter==0:
            self.dialog_conclusion['buttonBack'].set_sensitive(False)
        else:
            self.dialog_conclusion['buttonBack'].set_sensitive(True)
        
        # enable forward-button?
        if self.conclusion_iter + 1 == len(self.filenames_action_status):
            self.dialog_conclusion['buttonForward'].set_sensitive(False)
        else:
            self.dialog_conclusion['buttonForward'].set_sensitive(True)
                
        item = self.filenames_action_status[self.conclusion_iter]                
                
        self.dialog_conclusion['labelConclusionFilename'].set_text(os.path.basename(item['filename']))
                
        if self.action == Action.DECODE or self.action == Action.DECODEANDCUT:
            status, message = item['action_status'][Action.DECODE]
            text = self.app.status_to_s(status) + ": " + message
            self.dialog_conclusion['labelConclusionDecodeStatus'].set_text(text)
                
        if self.action == Action.CUT or self.action == Action.DECODEANDCUT:
            text = ""
            
            status, message = item['action_status'][Action.CUT]
            if status == Status.OK:
            
                status, array = item['action_status'][Action.CUT] 
                if len(array)==2: # this means the file was cut by a cutlist
                    text = "OK: Geschnitten mit Cutlist #%s" % array[1]
                    
                    self.dialog_conclusion['vboxRating'].show()
                    self.dialog_conclusion['vboxButtons'].show()
                else: # file was cut manually...
                    text = "OK: Datei wurde manuell geschnitten"
                
                    # ...so don't show rating options, and we don't know the filename
                    # so we also can't play it
                    self.dialog_conclusion['vboxButtons'].hide()
                    self.dialog_conclusion['vboxRating'].hide()
                    
            else:
                # hide play button and rating
                self.dialog_conclusion['vboxRating'].hide()
                self.dialog_conclusion['vboxButtons'].hide()
                
                status, message = item['action_status'][Action.CUT]
                text = self.app.status_to_s(status) + ": " + message
            
            self.dialog_conclusion['labelConclusionCutStatus'].set_text(text)
        
    def on_buttonConclusionClose_clicked(self, widget, data=None):
        self.windows['dialog_conclusion'].hide()

    #
    # DIALOG ARCHIVE
    #
    def on_archive_buttonCancel_clicked(self, widget, data=None):
        if self.question_box("Wirklich abbrechen?"):
            self.windows['dialog_archive'].hide()
    
    # methods for folder treeview
    def append_row_treeviewFolders(self, parent, filename):   
        iter = self.dialog_archive['treeviewFolders_store'].append(parent, [filename])
        return iter
    
    def folder_name(self, column, cell, model, iter):
        cell.set_property('text', os.path.basename(model.get_value(iter, 0)))

    # methods for file-rename treeview    
    def append_row_treeviewFilesRename(self, filename):
        iter = self.dialog_archive['treeviewFilesRename_store'].append([filename])    
        return iter
        
    def new_name_cell_edited(self, cell, path, new_text, model):
        # update new name of file in model
        model[path][0] = new_text
     
    #
    # DIALOG CUTLIST
    #
    def add_cutlist(self, data):
        self.dialog_cutlist['treeviewCutlists_store'].append(data)    
        
if __name__ == "__main__":
    print "Use otr"
    sys.exit(-1)       
