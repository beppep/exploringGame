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
    
    def makeThing(self, creator, cls, size=None):
        spread = gridSize//4 #spread kan vara ett argument i guess
        thing=cls(x=creator.x+random.randrange(-spread,spread),y=creator.y+random.randrange(-spread,spread))
        if size:
            thing.setSize(size)
        self.things.append(thing)
        return thing

    def getTile(self, x, y):
        x = x/gridSize
        y = y/gridSize
        if len(self.tiles)>y:
            if len(self.tiles[int(y)])>x:
                return self.tiles[int(y)][int(x)]
        return None

    def search(self, obj,filter=lambda x:True,range=1):
        closest = None
        best = range*gridSize
        x, y = obj.x, obj.y
        for thing in self.things:
            if filter(thing) and thing != obj:
                dist = abs(x-thing.x)+abs(y-thing.y)
                if dist<best:
                    best = dist
                    closest = thing
        return closest

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


    def generateThings(self):
        for i in range(100):
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
        #self.image=self.images[self.type]
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
            world.camera.drawImage(self.images[self.type], self.x, self.y)
        

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
        self.size =1

    def use(self):
        pass
    def drop(self):
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

    def drop(self):
        if(world.getTile(self.x,self.y).type=="snow"):
            world.things.remove(self)
            world.makeThing(self, IceFlower, size=self.size)

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
        filterer = lambda x: x.type in ["tree","stone"]
        thing = world.search(self, filterer)
        if thing:
            self.uses-=1
            world.things.remove(thing)
            if(thing.type=="tree"):
                for i in range(random.randint(1,2)):
                    world.makeThing(thing, Log, size=thing.size/2)
            elif(thing.type=="stone"):
                for i in range(random.randint(1,2)):
                    world.makeThing(thing, Pebble, size=thing.size)
                if(random.random()<0.2):
                    world.makeThing(thing, Ruby, size=thing.size)
        if(self.uses<=0):
            world.player.holding=None

class Shovel(Thing):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="shovel"
        self.uses=10
        self.setSize(1)
    
    conversion = {"snow":"darkGrass","darkGrass":"sand","grass":"sand","sand":"lightWater","ice":"lightWater"}

    def use(self):
        print(self.uses)
        ground = world.getTile(self.x, self.y)
        if ground.type in Shovel.conversion:
            self.uses-=1
            ground.type = Shovel.conversion[ground.type]
            ground.image=ground.images[ground.type]
            if(self.uses<=0):
                world.player.holding=None

class Tree(Thing):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="tree"
        self.setSize(2)

    def drop(self):
        if self.size<1:
            rock = world.search(self, filter=lambda x:x.type in ["stone", "pebble"])
            if rock:
                world.things.remove(rock)
                world.things.remove(self)
                if(rock.type=="stone"):
                    cls=Hatchet
                if(rock.type=="pebble"):
                    cls=Shovel
                tool = world.makeThing(rock, cls, size=rock.size)
                print("made tool")
                tool.uses=max(int(tool.size)*tool.uses,1)
                world.things.append(tool)

    def update(self):
        ground = world.getTile(self.x,self.y)

        super().update()
        if ground.type=="snow":
            self.size-=0.1 #0.001
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
        super().__init__(x,y)
        self.type="log"
        self.setSize(1)
class Ruby(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="ruby"
        self.setSize(1)
class Pebble(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="pebble"
        self.setSize(1)

class Animal(Thing):
    def __init__(self, x=0, y=0):
        super().__init__(x,y)

class Animus(Animal):

    def __init__(self,x,y):
        super().__init__(x,y)
        self.type = "animus"
        self.setSize(1)
        self.speed=2

    def update(self):
        super().update()

        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type!="water": #likeit?()
            self.x+=dx
            self.y+=dy

class Gremlin(Animal):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="gremlin"
        self.speed=2

        self.setSize(1)

    def update(self):
        super().update()

        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type=="snow":
            self.x+=dx
            self.y+=dy

        if random.random()<0.001:
            self.eat()

    def eat(self):
        tree = world.search(self, filter=lambda x:x.type=="tree")
        if tree:
            world.things.remove(tree)
            world.makeThing(self, Stone, size=tree.size/2)

class Player():

    speed = gridSize//2

    dropToUse = False

    idleImage = loadImage("idle.png")

    def __init__(self, x=16*32//worldgen.Terrain.gridSize*gridSize, y=16*18//worldgen.Terrain.gridSize*gridSize):
        self.x = x
        self.y = y
        self.size = 1
        self.image = Player.idleImage
        self.holding = None
        self.spaceDown = False
        self.eDown = False

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
        thing = world.search(self, range=1)
        if thing:
            self.holding = thing
            world.things.remove(thing)

    def release(self):
        self.holding.x = self.x
        self.holding.y = self.y
        world.things.append(self.holding)
        self.holding.drop() #after adding!
        if self.dropToUse:
            self.holding.use()
        self.holding = None
        
    def use(self):
        if(self.holding) and not self.dropToUse:
            self.holding.use()
    def draw(self, x, y): #becuase world sends these
        world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
        if self.holding:
            self.holding.x=self.x
            self.holding.y=self.y-gridSize//4
            self.holding.draw(self.x,self.y)



world = World()
world.generateWorld()
world.player.holding=Hatchet(x=world.player.x,y=world.player.x)

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