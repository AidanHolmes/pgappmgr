from pgwindow import PygameApp, PygameButton
import pygame
import psutil
import time
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
    
AppInfo = {'iconname':'System Info',
           'icon':'app.png',
           'description':'System Information',
           'class':'SystemInfo',
           'framerate':5}

class RefreshBtn(PygameButton):
    def __init__(self, *arg, **kwargs):
        PygameButton.__init__(self, *arg, **kwargs)

    def window_key(self, press, keyid, key):
        if (not press and key == 'KEY_ENTER'):
            self._refreshscreen
        return True

    def window_touch(self, x, y, pressed):
        if pressed:
            self._refreshscreen()
        return True

    def _refreshscreen(self):
        try:
            self._einkrefresh_f = open("/sys/class/graphics/fb0/epd_refresh", "w+")
            self._einkrefresh_f.write("1")
            self._einkrefresh_f.close()
        except (FileNotFoundError, IOError):
            print ("DEBUG: Cannot refresh e-ink display")
            raise
        
class SystemInfo(PygameApp):
    def __init__(self, screen, wndrect):
        PygameApp.__init__(self, screen, wndrect)
        self._refreshbtn = RefreshBtn(rect = pygame.Rect(10,10,80,50))
        self._refreshbtn.name = "Refresh"
        self.add_child(self._refreshbtn)
        self._screenfont = pygame.font.Font(None, 24)
        self._system_poll_t = 0
        self._system_poll = 2
        self._memory = psutil.virtual_memory()
        self._cpu = psutil.cpu_percent(None,True)
        self.focused = True
        
    def do_work(self):
        t = time.time()
        if t > self._system_poll_t+self._system_poll:
            self._system_poll_t = t
            self._memory = psutil.virtual_memory()
            self._cpu = psutil.cpu_percent(None,True)
            
            self._isdirty = True

        if self._isdirty:
            self.draw()

    def draw(self):
        self._surface.fill((255,255,255))
        lines = []
        pos = pygame.Rect(10,10,0,0)
        val_start_at = 0
        lines.append(("Total memory", ": {:d}Mb".format(int(self._memory.total/(1024*1024)))))
        lines.append(("Available memory", ": {:.2f}Mb".format(self._memory.available/1048576)))
        lines.append(("Used memory",": {:.2f}Mb".format(self._memory.used/1048576)))
        lines.append(("Free memory",": {:.2f}Mb".format(self._memory.free/1048576)))
        lines.append(("Percent memory", ": {:.1f}%".format(self._memory.percent)))
        lines.append((" ", " "))
        for cpu in range(len(self._cpu)):
            lines.append(("CPU {:d}".format(cpu), ": {:.1f}%".format(self._cpu[cpu])))
        
                                                               
        for line in lines:
            # Draw labels first and work out max width
            text = self._screenfont.render(line[0], 1, (10,10,10))
            pos = text.get_rect(top=pos.bottom,left=pos.left)
            val_start_at = max(val_start_at, pos.right)
            self._surface.blit(text, pos)

        self._refreshbtn.draw()
        self._refreshbtn.position = (pos.left, pos.bottom, None, None)
        self._refreshbtn.copy_to(self._surface)

        pos = pygame.Rect(val_start_at, 10,0,0)
        for line in lines:
            text = self._screenfont.render(line[1], 1, (10,10,10))
            pos = text.get_rect(top=pos.bottom,left=pos.left)
            self._surface.blit(text, pos)

        
    def window_touch(self, x, y, pressed):
        return False

    def window_key(self, press, keyid, key):
        if press and key == 'KEY_RIGHT':
            pass
        return False
