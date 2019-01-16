import random
import math
import pygame
from pgwindow import FrameClock, PygameApp

AppInfo = {'iconname':'Stars',
           'icon':'stars.png',
           'description':'Star field animation',
           'class':'StarsApp',
           'framerate':100}

class StarsApp(PygameApp):
    def __init__(self, wndrect, screen):
        PygameApp.__init__(self, wndrect, screen)
        screenrect = screen.get_rect()
        self._origin = [screenrect.centerx, screenrect.centery]
        self.NUMSTARS = 150
        random.seed()
        self.stars = []
        self.initialize_stars()
        self.white = 255,240,200
        self.black = 20,20,40

        self._font = pygame.font.Font(None, 24)
        self._displayclock = pygame.time.Clock()

        self._fclock = FrameClock()
        self._fclock.ontick(15)

    def init_star(self):
        "creates new star values"
        dir = random.randrange(100000)
        velmult = random.random()*.6+.4
        vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]
        return vel, self._origin[:]

    def initialize_stars(self):
        "creates a new starfield"
        self.stars = []
        for x in range(self.NUMSTARS):
            star = self.init_star()
            vel, pos = star
            steps = random.randint(1, int(self._origin[0]))
            pos[0] = pos[0] + (vel[0] * steps)
            pos[1] = pos[1] + (vel[1] * steps)
            vel[0] = vel[0] * (steps * .09)
            vel[1] = vel[1] * (steps * .09)
            self.stars.append(star)
        self.move_stars()
  
    def draw_stars(self,color):
        "used to draw the stars"
        for vel, pos in self.stars:
            pos = (int(pos[0]), int(pos[1]))
            pygame.draw.circle(self._surface,color,pos,3,0)
        # Display FPS
        txt = self._font.render("FPS {}".format(int(self._displayclock.get_fps())), 1, self.white)
        self._surface.blit(txt, txt.get_rect(top=0,right=self._wndpos.width))
        self._displayclock.tick()

    def move_stars(self):
        "animate the star values"
        for vel, pos in self.stars:
            pos[0] = pos[0] + vel[0]
            pos[1] = pos[1] + vel[1]
            if not 0 <= pos[0] <= self._wndpos.width or not 0 <= pos[1] <= self._wndpos.height:
                vel[:], pos[:] = self.init_star()
            else:
                vel[0] = vel[0] * 1.05
                vel[1] = vel[1] * 1.05
  
    def do_work(self):
        if self._fclock.tick():
            self._surface.fill(self.black)
            self.move_stars()
            self.draw_stars(self.white)
    
    def window_touch(self, x,y,pressed):
        if not pressed:
            self._origin = (x, y)
        return True
    
