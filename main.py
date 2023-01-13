import pygame, math, random

class game:
    def __init__(self, fps, width, height, title):
        pygame.init()
        global screen
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.__clock = pygame.time.Clock()
        self.gameobjects = []
        self.eventhandlers = {}
        self.__fps = fps
        self.worldoffset = [0, 0]

    def addobject(self, object):
        self.gameobjects.append(object)

    def addeventlistener(self, event, handler):
        self.eventhandlers |= {event: handler}

    def gametick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        for k, v in self.eventhandlers.items():
            if pygame.key.get_pressed()[k]:
                v()

        screen.fill((193, 154, 107))
        if len(self.gameobjects) > 0:
            for i in self.gameobjects:
                i.draw(screen, self.worldoffset)
        pygame.display.update()
        self.__clock.tick(self.__fps)

class gameobject:
    def __init__(self, x, y, x2, y2, color:tuple[int, int, int], type, width, *objects, **params):
        self.pos = [x, y]
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.__objects = [*objects]
        self.type = type
        self.width = width

    def draw(self, screen, offset=(0, 0)):
        if self.type != "collection":
            pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.x2+self.pos[0], self.y2+self.pos[1]))
        else:
            for object in self.__objects:
                object.draw(screen)


class road(gameobject):
    def draw(self, screen, worldoffset=[0, 0]):
        pygame.draw.line(screen, self.color, (self.pos[0]-worldoffset[0], self.pos[1]-worldoffset[1]), (self.x2-worldoffset[0], self.y2-worldoffset[1]), self.width)
        pygame.draw.circle(screen, self.color, (self.x2-worldoffset[0], self.y2+1-worldoffset[1]), self.width//2-1)
        self.draw_dashed_line(screen, (230, 230, 0), (self.pos[0]-worldoffset[0], self.pos[1]-worldoffset[1]), (self.x2-worldoffset[0], self.y2-worldoffset[1]), 2, 3)

    def draw_dashed_line(self, surf, color, start_pos, end_pos, width=1, dash_length=10):
        # draw a dashed line on a surface from start_pos to end_pos in color with a given width and dash_length
        # surf: the surface to draw on
        # color: the color of the line
        # start_pos: the start position of the line
        # end_pos: the end position of the line
        # width: the width of the line
        # dash_length: the length of the dashes
        # doesnt work but im happy with the result :D
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dash_count = int(distance / dash_length)
        dx = dx / dash_count
        dy = dy / dash_count
        for i in range(dash_count):
            pygame.draw.line(surf, color, (x1, y1), (x1 + dx, y1 + dy), width)
            x1 += dx
            y1 += dy


class player():
    def __init__(self, x, y, w, h, color:tuple[int, int, int]=(255, 0, 0), image=None):
        self.pos = [x, y]
        self.w = w
        self.h = h
        self.color = color
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        if image is not None:
            im=pygame.image.load(f'{__file__}\\..\\{image}').convert_alpha()
            self.surface.blit(im, (0, 0))
        else:
            self.surface.fill(self.color)

        self.started = False
        self.angle = 0
        self.type = 'player'

        self.cameralockx = False
        self.cameralocky = True
        self.worldoffset = [0, 0]

        self.speed = 0.05 # 3
        self.roadnum = 0
        self.center = [x + w//2, y + h//2]
        self.__won = False

    def getdist(self, x1, y1, x2, y2):
        self.center = [self.pos[0]+self.surface.get_width()//2, self.pos[1]+self.surface.get_height()//2]

        l2 = (x1-x2)**2 + (y1-y2)**2
        if l2 == 0:
            return (self.center[0]-x1)**2 + (self.center[1]-y1)**2
        t = ((self.center[0]-x1)*(x2-x1) + (self.center[1]-y1)*(y2-y1)) / l2
        t = max(0, min(1, t))
        return math.sqrt((self.center[0]-x1-t*(x2-x1))**2 + (self.center[1]-y1-t*(y2-y1))**2)

    def draw(self, screen, *overflow):
        if self.pos[0]>=screen.get_width()//2:
            self.cameralockx = True
        global g
        if self.speed > 0 and self.started:
            if self.cameralockx:
                self.worldoffset[0] += math.cos(math.radians(self.angle)) * self.speed
                g.worldoffset[0] = self.worldoffset[0]
            else:
                self.pos[0] += math.cos(math.radians(self.angle)) * self.speed
            if self.cameralocky:
                self.worldoffset[1] += math.sin(math.radians(self.angle)) * self.speed
                g.worldoffset[1] = self.worldoffset[1]
            else:
                self.pos[1] += math.sin(math.radians(self.angle)) * self.speed

        if self.roadnum == len(g.gameobjects):
            print('you win')

        near_road = False
        for i, j in enumerate(g.gameobjects):
            if j.type == "road":
                d1 = self.getdist(j.pos[0]-self.worldoffset[0], j.pos[1]-self.worldoffset[1], j.x2-self.worldoffset[0], j.y2-self.worldoffset[1])
                if abs(d1) < 25 and self.speed > 0 and self.speed <= 3:
                    self.roadnum = i
                    near_road = True
                    # print(self.roadnum)
                    if self.roadnum == len(g.gameobjects)-2:
                        self.__won = True
                        print('you win')
                    if not self.__won:
                        self.speed = round(self.speed + 0.01, 2)
                    else:
                        self.speed = round(self.speed - 0.03, 2)
        if self.speed < 0.05 and not self.__won:
            print('you lose')

        if self.speed > 0 and not near_road:
            self.speed = round(self.speed - 0.05, 2)
            # print('slow down')
        screen.blit(pygame.transform.rotate(self.surface, - self.angle), (self.pos[0], self.pos[1]))





if __name__ == "__main__":
    # game setup
    g = game(60, 800, 600, "Pygame thing")

    # event handlers - turn left, turn right
    def left_key():
        global g
        g.gameobjects[-1].angle = (g.gameobjects[-1].angle - 1 + 360) % 360
    def right_key():
        global g
        g.gameobjects[-1].angle = (g.gameobjects[-1].angle + 1 + 360) % 360
    def space_key():
        global g
        g.gameobjects[-1].started = True
    g.addeventlistener(pygame.K_LEFT, left_key)
    g.addeventlistener(pygame.K_RIGHT, right_key)
    g.addeventlistener(pygame.K_SPACE, space_key)

    # game objects - first road
    g.addobject(road(0, 350, 100, 350, (25, 25, 25), "road", 50))
    # level setup
    angle = random.randrange(-10, 10)
    lastx = 100
    lasty = 350
    newx = lastx + 100 * math.cos(angle * (math.pi/180))
    newy = lasty + 100 * math.sin(math.radians(angle))
    for i in range(0, 99):
        angle += random.randrange(-30, 30)
        r = road(lastx, lasty, newx, newy, (25, 25, 25), "road", 50)
        g.addobject(r)
        lastx = newx
        lasty = newy
        newx = lastx + 100 * math.cos(angle * (math.pi/180))
        newy = lasty + 100 * math.sin(math.radians(angle))
    g.addobject(road(lastx, lasty, newx, newy, (25, 25, 25), "road", 100))

    # game objects - player
    g.addobject(player(10, 340, 30, 20, (255, 0, 0), "player.png"))

    while True:
        g.gametick()


# TODO:
    # - fix ending player snapping to angle 0