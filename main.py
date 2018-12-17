# Main application loop for Pgappmgr
# Implements the System and App objects
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

from appmsg import *
from config import *
import threading
import pygame
import time
import socket
import signal
from msgqueue import AppPublisher, AppSubscriber, MessageQueue
from syswnd import SystemWindow
from events import DeviceEvents

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
        try:
            self._battstatus_f = open(BATT_DEVICE + BATT_STATUS)
            self._battstatus = True
            self._battstatus_t = 0
        except (FileNotFoundError, IOError):
            pass

        self._battcapacity = False
        try:
            self._battcapacity_f = open(BATT_DEVICE + BATT_CAPACITY)
            self._battcapacity = True
            self._battcapacity_t = 0
        except (FileNotFoundError, IOError):
            pass

        self._network_query_t = 0
        self._last_network_ip = ''

        if THREADED_SYSTEM:
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
                    if ROTATE90:
                        tmp = evt['x']
                        evt['x'] = WINSIZE[1] - evt['y']
                        evt['y'] = tmp
                    self.message_queue.post_message(MSG_TOUCH_INPUT, INPUT_ABSOLUTE, evt)

    def close(self):
        self._quit = True
        if THREADED_SYSTEM:
            self._ithread.join(8.0)
        
    def do_work(self):
        'Do some work. This should operate quickly and return'
        t = time.time()

        if not THREADED_SYSTEM:
            evt = self._input.get_event()
            while evt:
                if evt['type'] == 'key':
                    self.message_queue.post_message(MSG_KEY_INPUT, INPUT_ABSOLUTE, evt)
                elif evt['type'] == 'touch':
                    if ROTATE90:
                        tmp = evt['x']
                        evt['x'] = WINSIZE[1] - evt['y']
                        evt['y'] = tmp
                    self.message_queue.post_message(MSG_TOUCH_INPUT, INPUT_ABSOLUTE, evt)
                evt = self._input.get_event()

        if self._battcapacity:
            if t > self._battcapacity_t+BATT_QUERY_TIME:
                self._battcapacity_t = t
                try:
                    self._battcapacity_f.seek(0)
                    self.message_queue.post_message(MSG_SYS_BATTERY, 'capacity', self._battcapacity_f.read().rstrip())
                except IOError:
                    pass

        if self._battstatus:
            if t > self._battstatus_t+BATT_QUERY_TIME:
                self._battstatus_t = t
                try:
                    self._battstatus_f.seek(0)
                    self.message_queue.post_message(MSG_SYS_BATTERY, 'status', self._battstatus_f.read().rstrip())
                except IOError:
                    pass

        if t > self._network_query_t+NETWORK_QUERY_TIME:
            self._network_query_t = t
            ipstr = System.get_network_ip()
            if (ipstr != self._last_network_ip):
                self._last_network_ip = ipstr
                self.message_queue.post_message(MSG_SYS_NETWORK, None, ipstr)


class App(MessageQueue):
    def __init__(self):
        MessageQueue.__init__(self)
        self._clock = pygame.time.Clock()
        pygame.init()
        # Close mixer to prevent 100% CPU
        # https://github.com/pygame/pygame/issues/331
        pygame.mixer.quit()
        self._screen = pygame.display.set_mode(WINSIZE,MODE)
        screensize = self._screen.get_size()
        if ROTATE90:
            self._softscreen = pygame.Surface((screensize[1],screensize[0])).convert()
        else:
            self._softscreen = pygame.Surface(screensize).convert()
        self._quit = False
        self._framerate = FRAMERATE
        self._subscribe_message(self, MSG_APP_FRAMERATE, None, self._change_framerate)

    def _change_framerate(self, id, context, fr):
        if fr is None:
            self._framerate = FRAMERATE
        else:
            self._framerate = fr
        
    def run(self):
        sys = System(self)
        wnd = SystemWindow(self, self._softscreen)
        wnd.focused = True
        while not self._quit:
            try:
                sys.do_work()
                wnd.do_work()
                if ROTATE90:
                    newsoftscreen = pygame.transform.rotate(self._softscreen,90)
                    self._screen.blit(newsoftscreen,(0,0))
                else:
                    self._screen.blit(self._softscreen, (0,0))      
                pygame.display.flip()
                if self._framerate:
                    self._clock.tick(self._framerate)
            except KeyboardInterrupt:
                print("Quitting...")
                self._quit = True
                sys.close()
                pygame.quit()

def sigkill(a,b):
    pygame.quit()
    quit()
    
# Run the app
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, sigkill)
    myapp = App()
    myapp.run()


