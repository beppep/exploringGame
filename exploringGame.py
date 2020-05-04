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
    name = os.path.join("textures", textureName)
    image = pygame.image.load(name).convert_alpha()
    image = pygame.transform.scale(image, (size, size))

    #img_surface = image
    #image = pygame.transform.flip(image, True, False)
    img_rect = image.get_rect()
    img_surface = pygame.Surface((img_rect.width, img_rect.height), pygame.SRCALPHA)
    img_surface.fill((0, 0, 0, 0))
    img_surface.blit(image, img_rect)
    return img_surface

def collides(self, other):
        r = self.__class__.radius + other.__class__.radius
        dx = self.x-other.x
        dy = self.y-other.y
        if dx*dx<r*r and dy*dy<r*r: #abs
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
        x,y = self.player.x, self.player.y
        for row in self.tiles:
            for tile in row:
                tile.draw(x, y)
        thingsToDraw = self.things + [self.player]
        thingsToDraw.sort(key=lambda x:x.y)
        for thing in thingsToDraw:
            thing.draw(x,y)
            

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

    types = ["grass","sand","water","lightWater","darkGrass","snow","ice"]

    images = {string:loadImage(string+".png") for string in types}

    def __init__(self, typee, x=0, y=0):
        self.x = x
        self.y = y
        self.type = typee
        self.image=self.images[self.type]
        if self.type == "grass" and random.random()<0.01:
            world.things.append(Flower(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        if self.type == "grass" and random.random()<0.2:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == "darkGrass" and random.random()<0.5:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == "snow" and random.random()<0.3:
            world.things.append(Stone(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))

    def draw(self, x,y):
        
        #pl = world.player
        dx = (self.x-x)
        dy = (self.y-y)
        wdt = 1400
        hgt = 800
        
        if(2*dx<wdt and 2*dy<hgt) and (2*-dx<wdt and 2*-dy<hgt):
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
    def search(self,filter=lambda x:True,range=100):
        closest = None
        best = range
        for thing in world.things:
            if filter(thing) and thing != self:
                dist = abs(self.x-thing.x)+abs(self.y-thing.y)
                if dist<best:
                    best = dist
                    closest = thing
        return closest

    def use(self):
        pass
    def setSize(self, size):
        self.size=size
        self.image = loadImage(self.type+".png",int(self.size*gridSize))

    def update(self):
        ground = world.getTile(self.x,self.y)
        if ground.type=="water":
            world.things.remove(self)

    def draw(self, x, y):
        #pl = world.player
        dx = (self.x-x)
        dy = (self.y-y)
        wdt = 1400
        hgt = 800
        
        if(2*dx<wdt and 2*dy<hgt) and (2*-dx<wdt and 2*-dy<hgt):
            world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)

class Stone(Thing):
    def __init__(self,x=0,y=0):
        super(Stone, self).__init__(x,y)
        self.type="stone"
        self.setSize(1)

class Flower(Thing):
    def __init__(self,x=0,y=0):
        super(Flower, self).__init__(x,y)
        self.type="flower"
        self.setSize(1)
class IceFlower(Thing):
    def __init__(self,x=0,y=0):
        super(IceFlower, self).__init__(x,y)
        self.type="iceflower"
        self.setSize(1)

class Hatchet(Thing):
    def __init__(self,x=0,y=0):
        super(Hatchet, self).__init__(x,y)
        self.type="hatchet"
        self.uses=5
        self.setSize(1)
    def use(self):
        print(self.uses)
        closest = self.search()
        if closest:
            self.uses-=1
            if(closest.type=="tree"):
                world.things.remove(closest)
                logs=random.randint(1,2)
                for i in range(logs):
                    log=Log(x=closest.x+random.randrange(-32,32),y=closest.y+random.randrange(-32,32))
                    log.setSize(closest.size/2)
                    world.things.append(log)
            elif(closest.type=="stone"):
                world.things.remove(closest)
                pebbles=random.randint(1,2)
                for i in range(pebbles):
                    pebble=Pebble(x=closest.x+random.randrange(-32,32),y=closest.y+random.randrange(-32,32))
                    pebble.setSize(closest.size)
                    world.things.append(pebble)
                if(random.random()<0.2):
                    ruby=Ruby(x=closest.x+random.randrange(-32,32),y=closest.y+random.randrange(-32,32))
                    pebble.setSize(closest.size)
                    world.things.append(ruby)
            else:
                self.uses+=1
        if(self.uses<=0):
            world.player.holding=None
class Shovel(Thing):
    def __init__(self,x=0,y=0):
        super(Shovel, self).__init__(x,y)
        self.type="shovel"
        self.uses=10
        self.setSize(1)
    def use(self):
        print(self.uses)
        ground = world.getTile(self.x, self.y)
        conversion = {"snow":"darkGrass","darkGrass":"grass","grass":"sand","sand":"lightWater","ice":"lightWater","water":"water","lightWater":"lightWater"}
        ground.type = conversion[ground.type]
        ground.image=ground.images[ground.type]
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
class Log(Thing):
    def __init__(self,x=0,y=0):
        super(Log, self).__init__(x,y)
        self.type="log"
        self.setSize(1)
class Ruby(Thing):
    def __init__(self,x=0,y=0):
        super(Ruby, self).__init__(x,y)
        self.type="ruby"
        self.setSize(1)
class Pebble(Thing):
    def __init__(self,x=0,y=0):
        super(Pebble, self).__init__(x,y)
        self.type="pebble"
        self.setSize(1)

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
        closest = self.search(filter=lambda x:x.type=="tree")
        if closest:
            world.things.remove(closest)
            stone=Stone(x=closest.x,y=closest.y)
            stone.setSize(closest.size/2)
            world.things.append(stone)

class Player():

    hp = 3
    speed = 4

    idleImage = loadImage("idle.png")

    def __init__(self, x=16*32//worldgen.Terrain.gridSize*gridSize, y=16*18//worldgen.Terrain.gridSize*gridSize):
        self.x = x
        self.y = y
        self.size = 1
        self.image = Player.idleImage
        self.holding = None
        self.spaceDown = False
        self.eDown = False
    def search(self,filter=lambda x:True,range=100):
        closest = None
        best = range
        for thing in world.things:
            if filter(thing) and thing != self:
                dist = abs(self.x-thing.x)+abs(self.y-thing.y)
                if dist<best:
                    best = dist
                    closest = thing
        return closest

    def move(self, pressed):
        speed = self.speed
        ground = world.getTile(self.x, self.y)
        if ground.type=="water":
            speed*=0.25
        if ground.type=="lightWater":
            speed*=0.5
            if(self.holding):
                if(self.holding.type=="iceflower"):
                    ground.type = "ice"
                    ground.image=ground.images["ice"]
        if ground.type=="ice":
            speed*=2           
        if(pressed[pygame.K_d]):
            self.x+=speed
        if(pressed[pygame.K_a]):
            self.x-=speed
        if(pressed[pygame.K_s]):
            self.y+=speed
        if(pressed[pygame.K_w]):
            self.y-=speed

        if(not pressed[pygame.K_e]):
            self.eDown = False
        if(pressed[pygame.K_e] and not self.eDown):
            self.eDown = True
            self.use()

        if(not pressed[pygame.K_SPACE]):
            self.spaceDown = False
        if(pressed[pygame.K_SPACE] and not self.spaceDown):
            self.spaceDown = True
            if not self.holding:
                self.grab()
            else:
                self.release()

    def grab(self):
        closest = self.search(range=60)
        if closest:
            self.holding = closest
            world.things.remove(closest)

    def release(self):
        def releaseNormal():
            self.holding.x = self.x
            self.holding.y = self.y
            world.things.append(self.holding)
            self.holding = None
        if(self.holding.type=="tree" and self.holding.size<=1):            
            closest = self.search(filter=lambda x:x.type=="stone" or x.type=="pebble")
            if closest:
                world.things.remove(closest)
                if(closest.type=="stone"):
                    hatchet=Hatchet(x=closest.x,y=closest.y)
                if(closest.type=="pebble"):
                    hatchet=Shovel(x=closest.x,y=closest.y)
                hatchet.setSize(closest.size)
                hatchet.uses=max(int(hatchet.size)*hatchet.uses,1)
                world.things.append(hatchet)
                self.holding = None
            else:
                releaseNormal()
        elif(self.holding.type=="flower"):
            if(world.getTile(self.x,self.y).type=="snow"):
                flower=IceFlower(x=self.x,y=self.y)
                flower.setSize(self.holding.size)
                world.things.append(flower)
                self.holding = None
            else:
                releaseNormal()
        else:
            releaseNormal()

    def use(self):
        if(self.holding):
            self.holding.use()
    def draw(self, x, y): #becuase world sends these
        world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
        if self.holding:
            self.holding.x=self.x
            self.holding.y=self.y-10
            self.holding.draw()



world = World()
world.generateWorld()
#world.player.holding=Shovel(x=world.player.x,y=world.player.x)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # DO THINGS
    pressed = pygame.key.get_pressed()
    world.update(pressed)


    # DRAW
    gameDisplay.fill((25,25,105))
    world.draw()

    pygame.display.update() # flip?
    clock.tick(20000)



pygame.quit()
quit()