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
    return image

def collides(self, other):
        r = self.__class__.radius + other.__class__.radius
        dx = self.x-other.x
        dy = self.y-other.y
        if dx*dx<r*r and dy*dy<r*r: #abs
            return True
        else:
            return False

class World():

    a=0
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
        wdt = 700
        hgt = 400
        for row in range(int((y-hgt)//gridSize), int((y+hgt)//gridSize)):
            if row>=0 and row<len(self.tiles):
                for col in range(int((x-wdt)//gridSize), int((x+wdt)//gridSize)):
                    if col<len(self.tiles[row]):
                        self.tiles[row][col].draw()

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
        #print(world.a)
        world.a+=1
        x = x//gridSize
        y = y//gridSize
        return self.tiles[int(y)][int(x)]

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
    def searchMany(self,obj,filters=[lambda x:True]*2,range=1):
        objects=[]
        for objFilter in filters:
            closest=self.search(obj,filter=objFilter,range=range)
            if(closest):
                objects.append(closest)
                self.things.remove(closest)
            else:
                break
        if(len(objects)==len(filters)):
            return objects
        else:
            for obj in objects:
                self.things.append(obj)
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


    def generateThings(self):
        for i in range(100):
            x=random.randint(0,32*32/4-1)
            y=random.randint(0,18*32/4-1)
            if world.getTile(x,y).type!="water":
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

    def draw(self):
        world.camera.drawImage(self.images[self.type], self.x, self.y)

class Camera():

    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self):
        self.x = world.player.x-screenWidth//2
        self.y = world.player.y-screenHeight//2

    def drawImage(self, image, x, y):
        gameDisplay.blit(image, (x-self.x, y-self.y))

class Thing():
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.size =1

    def use(self):
        pass
        #self.drop() # kinda nice
    def update(self):
        pass
    def setSize(self, size):
        self.size=size
        self.image = loadImage(self.type+".png",int(self.size*gridSize))

    def drop(self):
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

class Flower(Thing):
    def __init__(self,x=0,y=0):
        super(Flower, self).__init__(x,y)
        self.type="flower"
        self.setSize(1)
    def drop(self):
        super().drop()
        if(world.getTile(self.x,self.y).type=="snow"):
            world.things.remove(self)
            world.makeThing(self, IceFlower, size=self.size)
class IceFlower(Thing):
    def __init__(self,x=0,y=0):
        super(IceFlower, self).__init__(x,y)
        self.type="iceflower"
        self.setSize(1)
    def use(self):
        ground = world.getTile(self.x, self.y)
        if ground.type=="lightWater":
            ground.type = "ice"
            ground.image=ground.images["ice"]
            world.player.holding=None
        elif(ground.type!="water" and ground.type!="snow" and ground.type!="ice"):
            ground.type = "snow"
            ground.image=ground.images["snow"]
            world.player.holding=None

class Hatchet(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="hatchet"
        self.uses=5
        self.setSize(1)
    def use(self):
        print("uses:",self.uses)
        filterer = lambda x: x.type in ["tree","stone","flower","iceflower"]
        thing = world.search(self, filterer)
        if thing:
            self.uses-=1
            world.things.remove(thing)
            if(thing.type=="tree"):
                for i in range(random.randint(1,2)):
                    world.makeThing(thing, Log, size=thing.size/2)
            elif(thing.type=="flower" or thing.type=="iceflower"):
                world.makeThing(thing, Stem, size=thing.size)
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
        print("uses:",self.uses)
        ground = world.getTile(self.x, self.y)
        if ground.type in Shovel.conversion:
            self.uses-=1
            ground.type = Shovel.conversion[ground.type]
            ground.image=ground.images[ground.type]
            if(self.uses<=0):
                world.player.holding=None

class Stone(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="stone"
        self.setSize(1)
class Tree(Thing):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="tree"
        self.setSize(2)

    def update(self):
        ground = world.getTile(self.x,self.y)

        super().update()
        if ground.type=="snow":
            if random.random()<0.1:
                self.setSize(self.size-0.01)
                if self.size<=0:
                    world.things.remove(self)
        if ground.type=="lightWater":
            if random.random()<0.1:
                self.setSize(self.size+0.01)
                if random.random()<0.1:
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
    
    def drop(self):
        ground = world.getTile(self.x,self.y)
        if ground.type=="water":
            world.things.remove(self)
            if(random.random()<0.3):
                world.makeThing(self, Sapphire, size=self.size)
class Pebble(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="pebble"
        self.setSize(1)
class Sapphire(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="sapphire"
        self.setSize(1)
    def drop(self):
        pass
class Stick(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="stick"
        self.setSize(1)
class Stem(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="stem"
        self.setSize(1)
class IceCrystal(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="icecrystal"
        self.setSize(1)
class IceWand(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="icewand"
        self.setSize(1)
        self.uses=50
        self.active=False
    def use(self):
        self.active=not self.active
class Animal(Thing): #pass lol
    pass

class Animus(Animal):

    def __init__(self,x,y):
        super().__init__(x,y)
        self.type = "animus"
        self.setSize(1)
        self.speed=2

    def update(self):
        super().update() #pass lol

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
        super().update() #pass lol

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

    speed = gridSize//8 # //2 är för sanbbt

    idleImage = loadImage("idle.png")
    
    def hatchet(things):
        rock=things[1]
        if(rock.type=="stone"):
            cls=Hatchet
        if(rock.type=="pebble"):
            cls=Shovel
        tool = world.makeThing(rock, cls, size=rock.size)
        tool.uses=max(int(tool.size**2)*tool.uses,1)
    def typeFunc(type):

        return lambda x:x.type==type
    def createObject(cls,tool=False):
        def func(things):
            obj = world.makeThing(things[0], cls, size=things[0].size)
            if(tool):
                 obj.uses=max(int(obj.size**2)*obj.uses,1)
        return func
    craftingTable = [
    [[lambda x:x.type=="tree" and x.size<=1,lambda x:x.type in ["stone", "pebble"]],hatchet],
    [[typeFunc("log"),typeFunc("stem")],createObject(Stick)],
    [[typeFunc("sapphire")]+[typeFunc("iceflower")]*3,createObject(IceCrystal)],
    [[typeFunc("icecrystal")]+[typeFunc("stick")],createObject(IceWand,tool=True)],
    ]

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
        if(self.holding and self.holding.type=="icewand"):
            if(self.holding.active):
                if ground.type=="lightWater":
                    print("uses:",self.holding.uses)
                    ground.type = "ice"
                    ground.image=ground.images["ice"]
                    self.holding.uses-=1
                    if(self.holding.uses==0):
                        self.holding=None
                elif(ground.type!="water" and ground.type!="snow" and ground.type!="ice"):
                    print("uses:",self.holding.uses)
                    ground.type = "snow"
                    ground.image=ground.images["snow"]
                    self.holding.uses-=1
                    if(self.holding.uses==0):
                        self.holding=None
        if ground.type=="water":
            speed*=0.25
        if ground.type=="lightWater":
            speed*=0.5 #<- else
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
        self.craft()
        self.holding = None

        
    def use(self):
        if(self.holding):
            self.holding.use()
    def craft(self):
        #add check if holding is in recipes to reduce lag
        for recipe in self.craftingTable:
            things = world.searchMany(world.player,filters=recipe[0],range=1)
            if(things):
                recipe[1](things)

    def draw(self, x, y): #becuase world sends these
        world.camera.drawImage(self.image, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
        if self.holding:
            self.holding.x=self.x
            self.holding.y=self.y-gridSize//4
            self.holding.draw(self.x,self.y)



world = World()
world.generateWorld()
#world.player.holding=Stick(x=world.player.x,y=world.player.x)
#world.makeThing(world.player, IceCrystal, size=2)
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