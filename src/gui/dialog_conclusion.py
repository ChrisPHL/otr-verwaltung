#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import basename

import gtk

from basewindow import BaseWindow
from constants import Action, Status, Cut_action

class DialogConclusion(BaseWindow):
    
    def __init__(self, app, parent):
        self.app = app
    
        widgets = [
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
            'checkbuttonRate',
            'vboxRating',           
            'buttonConclusionPlay',
            'check_delete_uncut',
            'button_conclusion_play_cut',
            'radiobuttonRate0',
            'radiobuttonRate1',
            'radiobuttonRate2',
            'radiobuttonRate3',
            'radiobuttonRate4',
            'radiobuttonRate5'            
            ]
        
        builder = self.create_builder("dialog_conclusion.ui")
            
        BaseWindow.__init__(self, builder, "dialog_conclusion", widgets, parent)
                
        # setup widgets
        for radio in range(6):
            self.get_widget("radiobuttonRate" + str(radio)).connect('toggled', self.on_radiobuttonRating_toggled, radio)
    
    ###
    ### Convenience
    ###        
    
    def build(self, file_conclusions, action):
        dialog = self.get_window()
        dialog.show_all()
        
        for radio in ['radiobuttonRate0', 'radiobuttonRate1', 'radiobuttonRate2', 'radiobuttonRate3', 'radiobuttonRate4', 'radiobuttonRate5' ]:
            self.get_widget(radio).set_sensitive(False)
        
        self.action = action

        # show status/rating for decode/cut?
        if self.action==Action.DECODE:
            self.get_widget('labelConclusionCutStatus').hide()
            self.get_widget('labelConclusionCut').hide()   
            self.get_widget('vboxRating').hide()
            self.get_widget('check_delete_uncut').hide()
            self.get_widget('button_conclusion_play_cut').hide()
            
        elif self.action==Action.CUT:
            self.get_widget('labelConclusionDecodeStatus').hide()
            self.get_widget('labelConclusionDecode').hide()   
                        
        self.file_conclusions = file_conclusions
                
        self.show_conclusion(0)       
        return dialog        
     
    ###
    ### Helpers
    ###
     
    def __status_to_s(self, status):
        if status == Status.OK:
            return "OK"
        elif status == Status.ERROR:
            return "Fehler"
        elif status == Status.NOT_DONE:
            return "Nicht durchgeführt"
     
    ###
    ### Signals handlers
    ###
             
    def on_buttonConclusionPlay_clicked(self, widget, data=None):    
        if self.action == Action.DECODE or self.file_conclusions[self.conclusion_iter].cut.status != Status.OK:
            filename = self.file_conclusions[self.conclusion_iter].uncut_avi
        else:    
            filename = self.file_conclusions[self.conclusion_iter].cut_avi

        self.app.perform_action(Action.PLAY, [filename])      
        
    def on_radiobuttonRating_toggled(self, widget, rate):
        if widget.get_active() == True:            
            self.file_conclusions[self.conclusion_iter].cut.rating = rate 
    
    def on_check_delete_uncut_toggled(self, widget, data=None):
        print "set to: ", widget.get_active()
        self.file_conclusions[self.conclusion_iter].cut.delete_uncut = widget.get_active()
       
    def on_checkbuttonRate_toggled(self, widget, data=None):
        status = widget.get_active()

        if status == False:
            self.get_widget('radiobuttonRate0').set_active(True)
            self.file_conclusions[self.conclusion_iter].cut.rating = -1
        
        for radio in ['radiobuttonRate0', 'radiobuttonRate1', 'radiobuttonRate2', 'radiobuttonRate3', 'radiobuttonRate4', 'radiobuttonRate5' ]:
            self.get_widget(radio).set_sensitive(status)
    
    def on_button_conclusion_play_cut_clicked(self, widget, data=None):
        file_conclusion = self.file_conclusions[self.conclusion_iter]
    
        if not file_conclusion.cut.local_cutlist:
            print "Lokale Cutlist nicht vorhanden!"
        else:
            self.app.show_cuts(file_conclusion.uncut_avi, file_conclusion.cut.local_cutlist)
        
    def on_buttonBack_clicked(self, widget, data=None):
        self.show_conclusion(self.conclusion_iter - 1)
    
    def on_buttonForward_clicked(self, widget, data=None):
        self.show_conclusion(self.conclusion_iter + 1)
        
    def show_conclusion(self, new_iter):
        self.conclusion_iter = new_iter
        
        # reset dialog        
        self.get_widget('labelCount').set_text("Zeige Datei %s/%s" % (self.conclusion_iter + 1, len(self.file_conclusions)))
        self.get_widget('vboxRating').hide()
        self.get_widget('buttonConclusionPlay').hide()
        self.get_widget('check_delete_uncut').hide()
        self.get_widget('button_conclusion_play_cut').hide()
        
        # enable back-button?
        if self.conclusion_iter == 0:
            self.get_widget('buttonBack').set_sensitive(False)
        else:
            self.get_widget('buttonBack').set_sensitive(True)
        
        # enable forward-button?
        if self.conclusion_iter + 1 == len(self.file_conclusions):
            self.get_widget('buttonForward').set_sensitive(False)
        else:
            self.get_widget('buttonForward').set_sensitive(True)
                
        # conclusion of file
        file_conclusion = self.file_conclusions[self.conclusion_iter]
        
        # filename
        if self.action == Action.DECODE:
            filename = basename(file_conclusion.otrkey)
        else:
            filename = "%s\n%s" % (basename(file_conclusion.uncut_avi), basename(file_conclusion.cut_avi))
                          
        self.get_widget('labelConclusionFilename').set_markup("<b>%s</b>" % filename)
        
        # decode status
        if self.action != Action.CUT:
            text = self.__status_to_s(file_conclusion.decode.status)
            message = file_conclusion.decode.message
            if message != "":
                text += " (%s)" % message
            
            if file_conclusion.decode.status == Status.OK:
                self.get_widget('buttonConclusionPlay').show()
                            
            self.get_widget('labelConclusionDecodeStatus').set_text(text)
        
        # cut status
        if self.action != Action.DECODE:
            text = self.__status_to_s(file_conclusion.cut.status)
            message = file_conclusion.cut.message
            
            if message != "":
                text += " (%s)" % message
           
            # removed: file_conclusion.cut.cut_action != -1 and
            if file_conclusion.cut.status == Status.OK:
                
                self.get_widget('check_delete_uncut').set_active(True)
                file_conclusion.cut.delete_uncut = True
                self.get_widget('check_delete_uncut').show()                
                
                if file_conclusion.cut.cut_action == Cut_action.MANUALLY:
                    text += ", Manuell geschnitten"
                else:
                    text += ", Geschnitten mit Cutlist #%s" % file_conclusion.cut.cutlist
                    # enable rating and play options
                    self.get_widget('vboxRating').show()
                    self.get_widget('buttonConclusionPlay').show()
                    self.get_widget('button_conclusion_play_cut').show()
                    
                    # already rated?
                    if file_conclusion.cut.rating > -1:                               
                        self.get_widget('checkbuttonRate').set_active(True)
                        self.get_widget('radiobuttonRate' + str(file_conclusion.cut.rating)).set_active(True)
                    else:
                        self.get_widget('checkbuttonRate').set_active(False)            
             
            print text                           
            self.get_widget('labelConclusionCutStatus').set_text(text) 
