#!/usr/bin/env python
# -*- coding: utf-8 -*-

from constants import Action
import os.path

from cutlists import Cutlist

class Decode:
    def __init__(self):
        self.status = -1
        self.message = ""
    
class Cut:
    def __init__(self):
        self.status = -1
        self.message = ""
        self.create_cutlist_error = ""      # couldn't get cuts from project file                                           
        
        self.cut_action = -1                # manually, best cutlist ...
        self.cutlist = Cutlist()            # cutlist class instance

        # filled in by dialog_conclusion
        self.my_rating = None               # rating, when cut by cutlist        
        self.rename = 0                     # by autoname, filename ...
        self.create_cutlist = False         # create a cutlist?
        self.delete_uncut = True            # delete the uncut video after cut?

class FileConclusion:
    def __init__(self, action, otrkey="", uncut_video=""):
        if action == Action.DECODE or action == Action.DECODEANDCUT:
            self.otrkey = otrkey
            self.decode = Decode()
        
        self.uncut_video = uncut_video

        if action == Action.CUT or action == Action.DECODEANDCUT:
            self.cut_video = ""
            self.cut = Cut() 

    def get_extension(self):    
        return os.path.splitext(self.uncut_video)[1]
