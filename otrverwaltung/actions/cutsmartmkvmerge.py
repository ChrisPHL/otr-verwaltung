# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Markus Liebl <lieblm@web.de>
#This program is free software: you can redistribute it and/or modify it
#under the terms of the GNU General Public License version 3, as published
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranties of
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


from gtk import events_pending, main_iteration, RESPONSE_OK
import re
import os
import subprocess

from otrverwaltung.actions.cut import Cut
from otrverwaltung.constants import Action, Cut_action, Status, Format, Program
from otrverwaltung import path

class CutSmartMkvmerge(Cut):

    def __init__(self, app, gui):
        self.update_list = True
        self.app = app
        self.config = app.config
        self.gui = gui
        self.encode_nr = 0                                     # index for encoded video parts - for the smart rendering simulation
        self.copy_nr = 0                                         # index for copied video parts - for the smart rendering simulation
        self.workingdir = '/tmp'
        self.video_files = []                                     # temporary video files
        self.audio_files = []                                    # temporary audio files
        self.rawstreams = {}                                # temporary eac3to files
        
    def __del__(self):
        # clean up
        try:
            if os.path.isfile (self.workingdir + '/audio_copy.mkv'):
                os.remove(self.workingdir + '/audio_copy.mkv')
            if os.path.isfile (self.workingdir + '/video_copy.mkv'):
                os.rename(self.workingdir + '/video_copy.mkv', self.workingdir + '/video_copy-001.mkv')
            for n in self.video_files + self.audio_files:
                if os.path.isfile(n.lstrip('+')):
                    os.remove(n.lstrip('+'))
            if os.path.isfile (self.workingdir + '/audio_encode.mkv'):
                os.remove(self.workingdir + '/audio_encode.mkv')
            for index in sorted(self.rawstreams.keys()):
                if os.path.isfile(self.workingdir + '/' + self.rawstreams[index]):
                    os.remove(self.workingdir + '/' + self.rawstreams[index])
        except:
            pass
        

    def cut_file_by_cutlist(self, filename, cutlist=None, program_config_value=None):
        """ Cuts a otr file with x264 and mkvmerge frame accurate. 
            returns: name of cut video, error_message """
        # configuration
        videolist = []                                              # result list for smart rendering simulation
        audio_import_files = [filename]                 # otr files which have audio streams  and needs to be cutted (e.g. OTR avi and ac3) 
        process_list = []                                        # list of started processes
        mkvmerge_list = []                                     # list of started mkvmerge processes
        video_splitframes = ''                               # mkvmerge split string for cutting the video at keyframes 
        audio_timecodes = ''                                # mkvmerge split timecodes for cutting the audio
        ac3_file = None                                         # AC3 source file
        
        # x264 option string
        format, ac3_file = self.get_format(filename)
        if format == Format.HQ:
            x264_opts = self.complete_x264_opts(self.config.get('smartmkvmerge', 'x264_hq_string').split(' '),  filename)
        elif format == Format.HD:
            x264_opts = self.complete_x264_opts(self.config.get('smartmkvmerge', 'x264_hd_string').split(' '),  filename)
        elif format == Format.MP4:
            x264_opts = self.complete_x264_opts(self.config.get('smartmkvmerge', 'x264_mp4_string').split(' '),  filename)
        else:
            return None, "Format nicht unterstützt (Nur MP4 H264, HQ H264 und HD H264 sind möglich)."
        
        # test workingdir
        if os.access(self.config.get('smartmkvmerge', 'workingdir').rstrip('/'),  os.W_OK):
            self.workingdir = os.path.abspath(self.config.get('smartmkvmerge', 'workingdir')).rstrip('/')
        else:
            return None, "Ungültiges Temp Verzeichnis. Schreiben nicht möglich."

        # audio part 1 - cut audio 
        if ac3_file:
            audio_import_files.append(ac3_file)

        audio_timecodes = (',+'.join([self.get_timecode(start) + '-' + self.get_timecode(start+duration) for start, duration in cutlist.cuts_seconds]))        
        audio_timecodes = audio_timecodes.lstrip(',+')
        
        try:
            blocking_process = subprocess.Popen([self.config.get_program('mkvmerge'), '--ui-language',  'en_US',  '-D',  '--split',  'parts:'+audio_timecodes,  '-o',  self.workingdir + '/audio_copy.mkv'] + audio_import_files, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except OSError as e:
            return None, "Fehler: %s Filename: %s Error: %s" % str(e.errno),  str(e.filename),  str(e.strerror)
        
        mkvmerge_list.append(blocking_process)

        # video part 1 - read keyframes
        keyframes, error = self.get_keyframes_from_file(filename)
        if keyframes == None:
            return None,  "Keyframes konnten nicht ausgelesen werden."

        # video part 2 - simulate smart rendering process
        for frame_start, frames_duration in cutlist.cuts_frames:
            result = self.__simulate_smart_mkvmerge(int(frame_start), int(frames_duration), keyframes)
            if result != None:
                videolist += result
            else:
                return None,  'Cutlist oder zu schneidende Datei passen nicht zusammen oder sind fehlerhaft.'
        
        # video part 3 - encode small parts - smart rendering part (1/2) 
        for encode, start,  duration,  video_part_filename in videolist:
            self.video_files.append('+'+ self.workingdir +'/' + video_part_filename)
            if encode:
                try:
                    non_blocking_process = subprocess.Popen([self.config.get_program('x264')] + x264_opts + ['--seek',  str(start),'--frames',  str(duration),  '--output',  self.workingdir + '/' + video_part_filename,  filename ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                except OSError as e:
                    return None, "Fehler: %s Filename: %s Error: %s" % str(e.errno),  str(e.filename),  str(e.strerror)
                process_list.append(non_blocking_process)
            else:
                video_splitframes += ','+str(start)+'-'+str(duration)

        self.video_files[0]=self.video_files[0].lstrip('+')
        video_splitframes = video_splitframes.lstrip(',')
        
        # video part 4 - cut the big parts out the file (keyframe accurate) - smart rendering part (2/2)
        try:
            non_blocking_process = subprocess.Popen([self.config.get_program('mkvmerge'),  '--ui-language',  'en_US','-A',  '--split',  'parts-frames:'+video_splitframes,  '-o',  self.workingdir + '/video_copy.mkv', filename ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except OSError as e:
            return None, "Fehler: %s Filename: %s Error: %s" % str(e.errno),  str(e.filename),  str(e.strerror)
        mkvmerge_list.append(non_blocking_process)

        # audio part 2 - encode audio to AAC
        if 'MP3 Spur kopieren' in self.config.get('smartmkvmerge', 'first_audio_stream') and 'AC3 Spur kopieren' in self.config.get('smartmkvmerge', 'second_audio_stream'):
            self.audio_files.append(self.workingdir + '/audio_copy.mkv')
        else:
                blocking_process.wait()
                ffmpeginput_file = self.workingdir + '/audio_copy.mkv'
                ffmpegoutput_file = self.workingdir + '/audio_encode.mkv'
                
                # convert first audio stream to aac
                if 'AAC' in self.config.get('smartmkvmerge', 'first_audio_stream') and 'AAC' in self.config.get('smartmkvmerge', 'second_audio_stream'):
                    aacaudiostreams = '-c:a'
                elif 'AAC' in self.config.get('smartmkvmerge', 'second_audio_stream') and 'MP3' in self.config.get('smartmkvmerge', 'first_audio_stream'):
                    aacaudiostreams = '-c:a:1'
                elif 'AAC' in self.config.get('smartmkvmerge', 'first_audio_stream'):
                    aacaudiostreams = '-c:a:0'
                else:
                    aacaudiostreams = '-c:a:2'
                    
                ffmpeg = self.config.get_program('ffmpeg')
                if 'nonfree' in ffmpeg:
                    # nonfree ffmpeg version with fdk support available
                    audiocodec = ['-c:a',  'copy',  aacaudiostreams,  'libfdk_aac',  '-flags',  '+qscale',  '-profile:a',  'aac_low',  '-global_quality',  '5' ,'-afterburner',  '1']
                else:
                    # only gpl version of ffmpeg available -> use standard aac codec
                    audiocodec = ['-c:a',  'copy',  aacaudiostreams,  'aac', '-strict', '-2','-profile:a',  'aac_low',  '-ab' ,'192k',  '-cutoff',  '18000']
                    
                if '2-Kanal' in self.config.get('smartmkvmerge', 'first_audio_stream'):
                    audiocodec.extend(['-ac:0',  '2'])

                if ac3_file == None:
                    # no ac3 stream found - all streams are muxed 
                    map = ['-map',  '0']
                else:
                    if 'AC3' in self.config.get('smartmkvmerge', 'first_audio_stream') :
                        map = ['-map',  '0:a:1']
                    else:
                        map = ['-map',  '0:a:0']
                    if not 'AC3 Spur entfernen' in self.config.get('smartmkvmerge', 'second_audio_stream') :
                        map.extend(['-map',  '0:a:1'])
                    
                args = [ffmpeg, "-loglevel", "info", "-y", "-i", ffmpeginput_file, "-vn", "-vsync", "1", '-async',  '1000',  "-dts_delta_threshold", "100", "-drc_scale", "1.0", '-threads',  '0',   ffmpegoutput_file]
                map.extend(audiocodec)
                args[6:6] = map
                try:
                    non_blocking_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                except OSError as e:
                    return None, "Fehler: %s Filename: %s Error: %s" % str(e.errno),  str(e.filename),  str(e.strerror)
                process_list.append(non_blocking_process)
                self.audio_files.append(self.workingdir + '/audio_encode.mkv')

        # wait until all threads are terminated
        for blocking_process in mkvmerge_list + process_list:
            self.show_progress(blocking_process)

        # check all processes
        for blocking_process in mkvmerge_list:
            returncode = blocking_process.wait()
            if returncode != 0 and returncode != 1:
                return None,  'beim Schneiden der Originaldatei...'
        for blocking_process in process_list:
            returncode = blocking_process.wait()
            if returncode != 0:
                return None,  'beim Kodieren ...'

        # clean up
        if os.path.isfile (self.workingdir + '/video_copy.mkv'):
            os.rename(self.workingdir + '/video_copy.mkv', self.workingdir + '/video_copy-001.mkv')
        if vars().has_key('ffmpeginput_file'):
            if os.path.isfile (ffmpeginput_file):
                os.remove(ffmpeginput_file)        
            
        # mux all together
        if self.config.get('smartmkvmerge', 'remux_to_mp4'):
            cut_video = self.workingdir + '/' + os.path.basename(os.path.splitext(self.generate_filename((filename),1))[0] + ".mkv")
        else:
            cut_video = os.path.splitext(self.generate_filename(filename,1))[0] + ".mkv"
        try:
            blocking_process = subprocess.Popen([self.config.get_program('mkvmerge'),  '--ui-language',  'en_US',  '-o',  cut_video] + self.video_files + self.audio_files, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except OSError:
            return None, "MKVMerge konnte nicht aufgerufen werden."
        self.show_progress(blocking_process)
        
        returncode = blocking_process.wait()
        if returncode != 0 and returncode != 1:
            return None,  'Allgemeine Schutzverletzung beim Erstellen des MKV...'

        # remove all temporary files
        for n in self.video_files + self.audio_files:
            if os.path.isfile(n.lstrip('+')):
                os.remove(n.lstrip('+'))

        # mux to mp4 
        if self.config.get('smartmkvmerge', 'remux_to_mp4'):
            # split files with eac3to
            with ChangeDir(self.workingdir):
                try:
                    blocking_process = subprocess.Popen(['wine', path.get_tools_path('intern-eac3to/eac3to.exe'), os.path.basename(cut_video),  '-demux',  '-silence',  '-keepDialnorm'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                except OSError:
                    return None, 'Eac3to konnte nicht aufgerufen werden'
                
                file_match = re.compile(r".*\"(.* - (\d{1,}) - .*)\".*")
                self.gui.main_window.set_tasks_text('Extrahiere Streams')
                self.gui.main_window.set_tasks_progress(50)
                while events_pending():
                    main_iteration(False)

                while blocking_process.poll() == None:
                    line = blocking_process.stdout.readline().strip()
                    if 'Creating file' in line:
                        m = re.search(file_match,line)
                        if m:
                            self.rawstreams[m.group(2)] = m.group(1)
                        else:
                            pass
                            
                returncode = blocking_process.wait()
                if returncode != 0:
                    if os.path.isfile(cut_video):
                        os.remove(cut_video)
                    return None,  'Fehler beim Extrahieren der Streams mit Eac3to'
                
                # remove mkv + log file
                if os.path.isfile(cut_video):
                    os.remove(cut_video)
                if os.path.isfile(os.path.splitext(cut_video)[0]+ ' - Log.txt'):
                    os.remove(os.path.splitext(cut_video)[0]+ ' - Log.txt')

                args = [self.config.get_program('mp4box'), '-new',  '-keep-all']
                
                for index in sorted(self.rawstreams.keys()):
                    args.append('-add')
                    args.append(self.rawstreams[index])

                cut_video = os.path.splitext(self.generate_filename(filename,1))[0] + ".mp4"
                args.append(cut_video)
                
                # mux to mp4 (mp4box)    
                try:
                    blocking_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                except OSError:
                    return None, 'MP4Box konnte nicht aufgerufen werden'
                    
                self.gui.main_window.set_tasks_text('Muxe MP4')                    
                self.show_progress(blocking_process)
                returncode = blocking_process.wait()
                if returncode != 0:
                    return None,  'Fehler beim Erstellen der MP4'
                    
        return cut_video, None

    def __simulate_smart_mkvmerge(self, start,  duration,  keyframes):
        end = start + duration
        if start in keyframes:
            if (end) in keyframes:
                if end <= start:
                    return
                # copy keyframe to keyframe
                self.copy_nr +=1
                return [(False, start+1, end+1, 'video_copy-00'+str(self.copy_nr) + '.mkv')]
            else:
                # copy to keyframe before end
                try:
                    lt_kf_before_end = self.get_keyframe_in_front_of_frame(keyframes, end)
                except:
                    return None
                if lt_kf_before_end <= start:
                    self.encode_nr += 1
                    encode = [(True, start, duration, 'video_encode-00'+str(self.encode_nr)+'.mkv')]
                    return encode
                else:
                    self.copy_nr +=1
                    copy = [(False, start+1, lt_kf_before_end+1, 'video_copy-00'+str(self.copy_nr)+'.mkv')]
                    # encode to end of interval
                    self.encode_nr += 1
                    encode = [(True, lt_kf_before_end, end-lt_kf_before_end , 'video_encode-00'+str(self.encode_nr)+'.mkv')]
                    return copy + encode
        else:
            try:
                nt_kf_from_start = self.get_keyframe_after_frame(keyframes, start)
            except:
                return None
            duration_nt_kf = nt_kf_from_start-start
            if end <= nt_kf_from_start:
                self.encode_nr += 1
                encode = [(True, start, duration, 'video_encode-00'+str(self.encode_nr)+'.mkv')]
                return encode
            else:
                self.encode_nr += 1
                encode = [(True, start, duration_nt_kf, 'video_encode-00'+str(self.encode_nr)+'.mkv')]
                if  duration-duration_nt_kf > 0:
                    result = self.__simulate_smart_mkvmerge(nt_kf_from_start, duration-duration_nt_kf,  keyframes)
                    if result != None:
                        return encode + result
                    else: 
                        return None
                else:
                    return encode


class ChangeDir:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
