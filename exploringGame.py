import pygame
import random
import time
import os
import worldgen

screenWidth = 1300
screenHeight = 700
gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
gridSize = 64
tiles = []

def loadImage(textureName, size=gridSize):
    image = pygame.image.load(os.path.join("textures", textureName))
    image = pygame.transform.scale(image, (size, size))
    #image = pygame.transform.flip(image, True, False)
    return image

def collides(self, other):
        r = self.__class__.radius + other.__class__.radius
        dx = self.x-other.x
        dy = self.y-other.y
        if abs(dx)<r and abs(dy)<r:
            return True
        else:
            return False

class World():

    def __init__(self):
        self.tiles = []
        self.player=None
        self.camera=None
        self.things = []
        
    def generateWorld(self):
        
        self.generateTiles()        
        self.generateThings()
        self.player = Player()
        self.camera = Camera()

    def update(self, pressed):
        self.player.move(pressed)
        self.camera.move()
        for thing in self.things:
            thing.update()

    def draw(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()
        thingsToDraw = self.things + [self.player]
        thingsToDraw.sort(key=lambda x:x.y)
        for thing in thingsToDraw:
            thing.draw()
            

    def getTile(self, x, y):
        x = x/gridSize
        y = y/gridSize
        if len(self.tiles)>y:
            if len(self.tiles[int(y)])>x:
                return self.tiles[int(y)][int(x)]
        return None

    def generateTiles(self):
        terrain = worldgen.Terrain()
        terrain.generate()
        tiles = terrain.returnWorld()
        snowtiles = []
        for y in range(len(tiles)):
            self.tiles.append([])
            for x in range(len(tiles[y])):
                tile=tiles[y][x]
                #print(tile)
                tile = Tile(tile,x=x*gridSize,y=y*gridSize)
                self.tiles[y].append(tile)
                if tile.type=="snow":
                    snowtiles.append(tile)

        tileOfTheGremlin = random.choice(snowtiles)
        world.things.append(Gremlin(tileOfTheGremlin.x, tileOfTheGremlin.y))

        """
        for i in range(20):
            self.tiles.append([])
            for j in range(20):
                self.tiles[-1].append(Tile(random.choice(Tile.types),j*gridSize,i*gridSize))
        """

    def generateThings(self):
        for i in range(500):
            x=random.randint(0,32*32/4-1)
            y=random.randint(0,18*32/4-1)
            self.things.append(Animus(x*gridSize,y*gridSize))

class Tile():

    types = ["grass","sand","water","lightWater","darkGrass","snow"]

    images = {string:loadImage(string+".png") for string in types}

    def __init__(self, typee, x=0, y=0):
        self.x = x
        self.y = y
        self.type = typee
        self.image=self.images[self.type]
        if self.type == "grass" and random.random()<0.2:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == "darkGrass" and random.random()<0.5:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == "snow" and random.random()<0.5:
            world.things.append(Stone(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))

    def draw(self):
        if(abs(self.x-world.player.x)<screenWidth and abs(self.y-world.player.y)<screenHeight):
            world.camera.drawImage(self.image, self.x, self.y)

class Camera():

    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self):
        self.x = world.player.x
        self.y = world.player.y

    def drawImage(self, image, x, y):
        r = gridSize//2
        gameDisplay.blit(image, (x-self.x+screenWidth//2-r, y-self.y+screenHeight//2-r))

class Thing():
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.size=1

    def setSize(self, size):
        self.size=size
        self.image = loadImage(self.type+".png",int(self.size*gridSize))

    def update(self):
        ground = world.getTile(self.x,self.y)
        if ground.type=="water":
            world.things.remove(self)
            print("aj")

    def draw(self):
        world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
class Stone(Thing):
    def __init__(self,x=0,y=0):
        super(Stone, self).__init__(x,y)
        self.type="stone"
        self.setSize(1)

class Tree(Thing):

    def __init__(self,x=0,y=0):
        super(Tree, self).__init__(x,y)
        self.type="tree"
        self.setSize(2)

    def update(self):
        ground = world.getTile(self.x,self.y)

        super(Tree, self).update()
        if ground.type=="snow":
            self.size-=0.001
            if self.size<=0:
                world.things.remove(self)
            else:
                self.image = loadImage("tree.png",int(self.size*gridSize))
        if ground.type=="lightWater":
            self.setSize(self.size+0.001)
            if random.random()<0.01:
                world.tiles[ground.y//gridSize][ground.x//gridSize]=Tile("sand",ground.x,ground.y)

class Animal(Thing):
    def __init__(self, x=0, y=0):
        super(Animal, self).__init__(x,y)

class Animus(Animal):

    def __init__(self,x,y):
        super(Animus, self).__init__(x,y)
        self.type = "animus"
        self.setSize(1)
        self.speed=2

    def update(self):
        super(Animus, self).update()

        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type!="water": #likeit?()
            self.x+=dx
            self.y+=dy

class Gremlin(Animal):

    def __init__(self,x=0,y=0):
        super(Gremlin, self).__init__(x,y)
        self.type="gremlin"
        self.speed=2

        self.setSize(1)

    def update(self):
        super(Gremlin, self).update()

        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type=="snow":
            self.x+=dx
            self.y+=dy

        if random.random()<0.001:
            self.eat()

    def eat(self):
        closest = None
        best = 100
        for thing in world.things:
            if thing.type=="tree":
                dist = abs(self.x-thing.x)+abs(self.y-thing.y)
                if dist<best:
                    best = dist
                    closest = thing
        if closest:
            world.things.remove(closest)
            stone=Stone(x=closest.x,y=closest.y)
            stone.setSize(closest.size/2)
            world.things.append(stone)

class Player():

    hp = 3
    speed = 2

    idleImage = loadImage("idle.png")

    def __init__(self, x=16*32//worldgen.Terrain.gridSize*gridSize, y=16*18//worldgen.Terrain.gridSize*gridSize):
        self.x = x
        self.y = y
        self.size = 1
        self.image = Player.idleImage
        self.holding = None
        self.spaceDown = False

    def move(self, pressed):
        speed = self.speed
        ground = world.getTile(self.x, self.y).type
        if ground=="water":
            speed*=0.25
        if ground=="lightWater":
            speed*=0.5
        if(pressed[pygame.K_d]):
            self.x+=speed
        if(pressed[pygame.K_a]):
            self.x-=speed
        if(pressed[pygame.K_s]):
            self.y+=speed
        if(pressed[pygame.K_w]):
            self.y-=speed

        if(not pressed[pygame.K_SPACE]):
            self.spaceDown = False
        if(pressed[pygame.K_SPACE] and not self.spaceDown):
            self.spaceDown = True
            if not self.holding:
                self.grab()
            else:
                self.release()

    def grab(self):
        closest = None
        best = 100
        for thing in world.things:
            dist = abs(self.x-thing.x)+abs(self.y-thing.y)
            if dist<best:
                best = dist
                closest = thing
        if closest:
            self.holding = closest
            world.things.remove(closest)

    def release(self):
        self.holding.x = self.x
        self.holding.y = self.y
        world.things.append(self.holding)
        self.holding = None

    def draw(self):
        world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
        if self.holding:
            self.holding.x=self.x
            self.holding.y=self.y-10
            self.holding.draw()


world = World()
world.generateWorld()


clock = pygame.time.Clock()
while not pygame.QUIT in [event.type for event in pygame.event.get()]:

    # DO THINGS
    pressed = pygame.key.get_pressed()
    world.update(pressed)


    # DRAW
    gameDisplay.fill((25,25,105))
    world.draw()

    pygame.display.update()
    #print(clock.tick(20000))


pygame.quit()
quit()