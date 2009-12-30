#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Section:
    """ Die verschiedenen Ansichten """
    PLANNING    = 6
    """ Geplante Sendungen"""
    OTRKEY      = 0
    """ Nicht dekodiert """
    VIDEO_UNCUT = 1
    VIDEO_CUT   = 2
    ARCHIVE     = 3
    TRASH       = 4
        
class Action:
    # planning
    PLAN_ADD        = 11
    PLAN_REMOVE     = 12
    PLAN_EDIT       = 13
    PLAN_SEARCH     = 14
    PLAN_RSS        = 15
    # decode and cut
    DECODE          = 0
    DECODEANDCUT    = 1
    CUT             = 2
    # file movement
    DELETE          = 3
    ARCHIVE         = 4
    RESTORE         = 6
    RENAME          = 7
    NEW_FOLDER      = 8
    REAL_DELETE     = 10

class Cut_action:
    ASK             = 0
    BEST_CUTLIST    = 1
    CHOOSE_CUTLIST  = 2
    MANUALLY        = 3
    LOCAL_CUTLIST   = 4

class Status:
    OK          = 0
    ERROR       = 1
    NOT_DONE    = 2
    
class Format:
    AVI = 0
    HQ  = 1
    MP4 = 2
    
class Program:
    AVIDEMUX    = 0
    VIRTUALDUB  = 1
