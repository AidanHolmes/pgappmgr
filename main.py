# Main application loop for Pgappmgr
# Implements the System and App objects
#
# Copyright (C) 2019 Aidan Holmes
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

from appmsg import *
from config import Config
import threading
import pygame
import time
import socket
import signal
from msgqueue import AppPublisher, AppSubscriber, MessageQueue
from syswnd import SystemWindow
from events import DeviceEvents
from os.path import join
import argparse

# Python 2.7 does not have FileNotFoundError exception
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

class System(AppPublisher):
    def __init__(self, mq):
        AppPublisher.__init__(self, mq)
        self.register_message(MSG_TOUCH_INPUT)
        self.register_message(MSG_KEY_INPUT)
        self.register_message(MSG_SYS_BATTERY)
        self.register_message(MSG_SYS_POWER_WARN)
        self.register_message(MSG_SYS_POWER_OFF)
        self.register_message(MSG_SYS_NETWORK)

        self._quit = False
        self._input = DeviceEvents()

        self._battstatus = False
        self._battcapacity = False
        if Config.battery.driver == 'BQ27510':
            try:
                self._battstatus_f = open(Config.battery.config.get('status'))
                self._battstatus = True
                self._battstatus_t = 0
            except (FileNotFoundError, IOError):
                pass

            try:
                self._battcapacity_f = open(Config.battery.config.get('capacity'))
                self._battcapacity = True
                self._battcapacity_t = 0
            except (FileNotFoundError, IOError):
                pass

        self._network_query_t = 0
        self._last_network_ip = ''

        if Config.system.threaded:
            self._ithread = threading.Thread(target=self._do_inputs)
            self._ithread.start()
                            
    @staticmethod
    def get_network_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Try any address. Connection won't happen as UDP doesn't send packets
            s.connect(('192.168.255.255', 1))
            ipstr = s.getsockname()[0]
        except:
            ipstr = '127.0.0.1'
        finally:
            s.close()
            return ipstr
        
    def _do_inputs(self):
        while not self._quit:
            evt = self._input.get_blocking_event(4.0)
            if evt:
                if evt['type'] == 'key':
                    self.message_queue.post_message(MSG_KEY_INPUT, INPUT_ABSOLUTE, evt)
                elif evt['type'] == 'touch':
                    evt['x'] *= Config.display.scalex
                    evt['y'] *= Config.display.scaley
                    if Config.display.rotate90:
                        tmp = evt['x']
                        evt['x'] = pygame.display.get_surface().get_height() - evt['y']
                        evt['y'] = tmp
                    self.message_queue.post_message(MSG_TOUCH_INPUT, INPUT_ABSOLUTE, evt)

    def close(self):
        self._quit = True
        if Config.system.threaded:
            self._ithread.join(8.0)
        
    def do_work(self):
        'Do some work. This should operate quickly and return'
        t = time.time()

        if not Config.system.threaded:
            evt = self._input.get_event()
            while evt:
                if evt['type'] == 'key':
                    self.message_queue.post_message(MSG_KEY_INPUT, INPUT_ABSOLUTE, evt)
                elif evt['type'] == 'touch':
                    if Config.display.rotate90:
                        tmp = evt['x']
                        evt['x'] = pygame.display.get_surface().get_height() - evt['y']
                        evt['y'] = tmp
                    self.message_queue.post_message(MSG_TOUCH_INPUT, INPUT_ABSOLUTE, evt)
                evt = self._input.get_event()

        if self._battcapacity:
            if t > self._battcapacity_t+Config.battery.getint('poll'):
                self._battcapacity_t = t
                try:
                    self._battcapacity_f.seek(0)
                    self.message_queue.post_message(MSG_SYS_BATTERY, 'capacity', self._battcapacity_f.read().rstrip())
                except IOError:
                    pass

        if self._battstatus:
            if t > self._battstatus_t+Config.battery.getint('poll'):
                self._battstatus_t = t
                try:
                    self._battstatus_f.seek(0)
                    self.message_queue.post_message(MSG_SYS_BATTERY, 'status', self._battstatus_f.read().rstrip())
                except IOError:
                    pass

        if t > self._network_query_t+Config.network.statuspoll:
            self._network_query_t = t
            ipstr = System.get_network_ip()
            if (ipstr != self._last_network_ip):
                self._last_network_ip = ipstr
                self.message_queue.post_message(MSG_SYS_NETWORK, None, ipstr)

class App(MessageQueue):
    def __init__(self, args):
        MessageQueue.__init__(self)
        self._clock = pygame.time.Clock()
        self._init_pygame()

        # Open the Config singleton
        Config.open(args.config)

        if Config.display.fullscreen:
            modes = pygame.display.list_modes(0,pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
            if len(modes) == 0:
                print("No hardware supported fullscreen modes found")
                quit()
            print ("Available modes: {}".format(modes))
            print ("Selecting screen mode: {}".format(modes[0]))
            self._screen = pygame.display.set_mode(modes[0],pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            if Config.display.size is None:
                print("Window mode requires a size setting in configuration")
                quit()
            self._screen = pygame.display.set_mode(Config.display.size,pygame.DOUBLEBUF | pygame.HWSURFACE)
        
        screensize = self._screen.get_size()
        if Config.display.rotate90:
            self._softscreen = pygame.Surface((screensize[1],screensize[0])).convert()
        else:
            self._softscreen = pygame.Surface(screensize).convert()
        self._quit = False
        self._framerate = Config.system.framerate
        self._subscribe_message(self, MSG_APP_FRAMERATE, None, self._change_framerate)
        self._sys = System(self)
        self._wnd = SystemWindow(self, self._softscreen)
        self._wnd.focused = True

    def _init_pygame(self):
        pygame.init()
        # Close mixer to prevent 100% CPU
        # https://github.com/pygame/pygame/issues/331
        pygame.mixer.quit()
        pygame.event.set_allowed(None)
        pygame.mouse.set_visible(False)

    def _change_framerate(self, id, context, fr):
        if fr is None:
            self._framerate = Config.system.framerate
        else:
            self._framerate = fr

    def _quitapp(self):
        print("Quitting...")
        self._quit = True
        self._sys.close()
        pygame.quit()
        
    def run(self):
        while not self._quit:
            try:
                self._sys.do_work()
                self._wnd.do_work()
                if Config.display.rotate90:
                    newsoftscreen = pygame.transform.rotate(self._softscreen,90)
                    self._screen.blit(newsoftscreen,(0,0))
                else:
                    self._screen.blit(self._softscreen, (0,0))      
                pygame.display.flip()
                if self._framerate:
                    self._clock.tick(self._framerate)
            except KeyboardInterrupt:
                self._quitapp()

def sigkill(a,b):
    self._quitapp()
    quit()
    
# Run the app
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, sigkill)
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='config filename', metavar='File')
    args = parser.parse_args()
    myapp = App(args)
    myapp.run()


