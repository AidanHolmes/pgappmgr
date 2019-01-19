# The main application launcher window. This runs all the time and acts
# as a proxy to running applications within the main system window
#
# Copyright (C) 2018 Aidan Holmes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Email: aidanholmes@orbitalfruit.co.uk

import pygame
import importlib
import time
import sys
from appmsg import *
from config import Config
from os import listdir
from os.path import join, isfile
from msgqueue import AppSubscriber, AppPublisher
from threading import Lock
from pgwindow import PygameApp

def app_guard(func,handler=None):
    def guard_call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("DEBUG - app call failed: {}".format(e))
            if handler is not None:
                handler() 
    return guard_call
            

class PygameLauncher(AppSubscriber, AppPublisher, PygameApp):
    def __init__(self, mq, *args, **kwargs):
        AppSubscriber.__init__(self,mq)
        PygameApp.__init__(self, *args, **kwargs)
        sys.path.insert(0, Config.launcher.launcherdir)
        self._apps = []
        self._defaulticon = pygame.image.load(join(Config.system.resourcedir,Config.launcher.defaulticon))
        self._defaulticon = pygame.transform.scale(self._defaulticon, Config.launcher.iconsize)
        self._iconfont = pygame.font.Font(None, Config.launcher.fontsize)

        self.read_apps()
        self._redraw = True
        self._keydown = None
        self._runningappmodule = None
        self._appobj = None

        self._lock = Lock()

        self._background = Config.launcher.background
        self._iconstride = Config.launcher.stride
        self._iconrowheight = Config.launcher.rowheight
        
    def keyinput(self,message):
        # override key dispatcher
        self._lock.acquire()
        try:
            if not message['press']:
                if message['key'] == 'KEY_HOME' or message['key'] == 'KEY_ESC':
                    if self._appobj:
                        self.stop_app()
            # forward key presses apart from Home/Esc key
            if self._appobj:
                # pass through
                app_guard(self._appobj.keyinput,self.stop_app)(message)
                return True
        
            if not message['press'] and message['key'] == 'KEY_ENTER':
                # Alternative select key for app
                appinfo = self.select_active_icon()
                if appinfo:
                    self.run_app(appinfo)
        finally:
            self._lock.release()
            
        if message['press']:
            if message['key'] == 'KEY_RIGHT':
                self.select_next_icon()
            elif message['key'] == 'KEY_LEFT':
                self.select_prev_icon()

        return True 
                
    def touch(self, message):
        # Touch input messages are global. A window needs
        # to normalise the input to its display surface
        # TO DO: migrate to use window_touch call to sub windows
        norm = message.copy()
        if self.screen_position.collidepoint(message['x'], message['y']):
            # Redefine x,y for client window
            norm['x'] = message['x'] - self.screen_position.x
            norm['y'] = message['y'] - self.screen_position.y
        else:
            # Touch input is outside client window
            return False

        self._lock.acquire()
        try:
            if self._appobj:
                # Pass through touch inputs to running app
                ret = app_guard(self._appobj.touch,self.stop_app)(message)
                return True
        finally:
            self._lock.release()

        if norm['press']:
            self._keydown = norm.copy()
            for icon in self._apps:
                state = icon['active']
                if icon['rect'].collidepoint(norm['x'], norm['y']):
                    icon['active'] = True
                else:
                    icon['active'] = False

                if state != icon['active']:
                    #state of an icon changed
                    self._redraw = True

        elif self._keydown:
            # Touch pressed and now up
            self._keydown = None
            for icon in self._apps:
                if icon['rect'].collidepoint(
                        norm['x'],
                        norm['y']) and icon['active']:
                    self.run_app(icon)

        # Never declare the input to be handled
        return False
    
    def select_active_icon(self):
        for icon in self._apps:
            if icon['active']:
                return icon
        return None

    def select_prev_icon(self):
        prev = None
        active_found = False
        if not len(self._apps):
            return None

        for icon in self._apps:
            if icon['active']:
                active_found = True
                if prev:
                    prev['active'] = True
                    icon['active'] = False
                    break
            prev = icon
        self._redraw = True
        if not active_found:
            self._apps[-1]['active'] = True
            
    def select_next_icon(self):
        prev = None
        if not len(self._apps):
            return None

        for icon in self._apps:
            if icon['active']:
                prev = icon
            elif prev:
                icon['active'] = True
                prev['active'] = False
                break
        self._redraw = True
        if not prev:
            self._apps[0]['active'] = True

    def stop_app(self):
        if self._appobj:
            # App is running. Call close
            app_guard(self._appobj.close)()
            
            # Delete import and app object
            del self._appobj
            self._appobj = None
            del self._runningappmodule
            self._runningappmodule = None

            # Restore framerate
            self.message_queue.post_message(MSG_APP_FRAMERATE, None, None)

            # refresh screen
            self._redraw = True
            
    def run_app(self, appinfo):
        try:    
            self._runningappmodule = importlib.import_module(appinfo['module'])
            runclass = Config.launcher.defaultclass
            if 'class' in appinfo:
                runclass = appinfo['class']

            if 'framerate' in appinfo and isinstance(appinfo['framerate'], int):
                self.message_queue.post_message(MSG_APP_FRAMERATE, None, appinfo['framerate'])

            if hasattr(self._runningappmodule, runclass):
                class_ = getattr(self._runningappmodule, runclass)
                
                self._appobj = class_(self._wndpos, self._surface)
            else:
                print("DEBUG - cannot find class {}".format(runclass))
                del self._runningappmodule
                self._runningappmodule = None
        except ImportError:
            self._runningappmodule = None
            self._appobj = None
    
    def read_apps(self):
        self._apps = []
        for f in listdir(Config.launcher.launcherdir):
            if isfile(join(Config.launcher.launcherdir,f)) and f[-3:] == '.py':
                module_name = f[:-3]
                try:
                    m = importlib.import_module(module_name)
                    modinfo = m.AppInfo.copy()
                    modinfo['module'] = module_name
                    modinfo['active'] = False
                    self._apps.append(modinfo)
                except ImportError:
                    pass

    def draw(self):
        stride = self._iconstride
        row = self._iconrowheight
        drawx = 0
        drawy = 0
        self._surface.fill(self._background)
        for icon in self._apps:
            if not hasattr(icon, 'wnd'):
                wnd = pygame.Surface((stride,row)).convert()
                icon['wnd'] = wnd
                wnd.fill(self._background)
                icon['rect'] = wnd.get_rect(left=drawx, top=drawy)
                iconrect = self._defaulticon.get_rect(center=(stride/2,row/2))
                wnd.blit(self._defaulticon, iconrect)
                text = self._iconfont.render(icon['iconname'], 1, (10,10,10))
                wnd.blit(text, text.get_rect(centerx=stride/2,top=iconrect.bottom))
            if icon['active']:
                wnd = icon['wnd'].copy()
                wnd.fill(self._background)
                wnd.blit(icon['wnd'],(0,0),None, pygame.BLEND_SUB)
                self._surface.blit(wnd, icon['rect'])
            else:
                self._surface.blit(icon['wnd'], icon['rect'])

            # advance and wrap the icons until no more room
            drawx = stride + drawx
            if drawx + stride > self._wndpos.width:
                drawx = 0
                drawy = row + drawy
            if drawy + row > self._wndpos.height:
                break
        
    def work(self):
        # work and key/touch events are separate threads. Lock the check
        # of _appobj to protect race conditions
        self._lock.acquire()
        try:
            if self._appobj:
                # Pass through touch inputs to running app
                app_guard(self._appobj.do_work, self.stop_app)()
                return None
        finally:
            self._lock.release()

        # Only redraw when required. Screen presses
        # and other events will trigger redraw
        if self._redraw:
            self.draw()
            self._redraw = False

    def suspend(self):
        pass

    def close(self):
        pass
