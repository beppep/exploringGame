import pygame
import random
import time
import os
import worldgen
import math
import pickle

screenWidth = 1300
screenHeight = 700
gridSize = 64 

if __name__ == "__main__":
    gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()

def loadImage(textureName, size=gridSize):
    name = os.path.join("textures", textureName)
    image = pygame.image.load(name).convert_alpha()
    image = pygame.transform.scale(image, (size, size))

    #img_surface = image
    #image = pygame.transform.flip(image, True, False)
    return image
"""
def collides(self, other):
        r = self.__class__.radius + other.__class__.radius
        dx = self.x-other.x
        dy = self.y-other.y
        if dx*dx<r*r and dy*dy<r*r: #abs
            return True
        else:
            return False
"""
class Camera():

    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self):
        self.x = world.player.x-screenWidth//2
        self.y = world.player.y-screenHeight//2

    def drawImage(self, image, x, y):
        gameDisplay.blit(image, (x-self.x, y-self.y))

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
                if tile.type==5:
                    snowtiles.append(tile)

        tileOfTheGremlin = random.choice(snowtiles)
        world.things.append(Gremlin(tileOfTheGremlin.x, tileOfTheGremlin.y))


    def generateThings(self):
        for i in range(100):
            x=random.randint(0,32*32*gridSize/4-1)
            y=random.randint(0,18*32*gridSize/4-1)
            if world.getTile(x,y).type!=0:
                self.things.append(Animus(x,y))

class Tile():

    types = {"water":0,"lightWater":1,"sand":2,"grass":3,"darkGrass":4,"snow":5,"ice":6,"swamp":7}

    images = (lambda types=types:{types[key]:loadImage(key+".png") for key in types})() #list comprehension scope error solution. dont ask

    def __init__(self, typee, x=0, y=0):
        self.x = x
        self.y = y
        self.type = typee
        if self.type == 3 and random.random()<0.03:
            world.things.append(Flower(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == 3 and random.random()<0.2:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == 4 and random.random()<0.5:
            world.things.append(Tree(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == 4 and random.random()<0.1:
            world.things.append(Stone(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
        elif self.type == 5 and random.random()<0.3:
            world.things.append(Stone(self.x+(random.random())*gridSize, self.y+(random.random())*gridSize))
    def draw(self):
        world.camera.drawImage(self.images[self.type], self.x, self.y)

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
        if ground.type==Tile.types["water"]:
            world.things.remove(self)

    def draw(self, x, y):

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
        if(world.getTile(self.x,self.y).type==Tile.types["snow"]):
            world.things.remove(self)
            world.makeThing(self, IceFlower, size=self.size)
class IceFlower(Thing):
    def __init__(self,x=0,y=0):
        super(IceFlower, self).__init__(x,y)
        self.type="iceflower"
        self.setSize(1)
    def drop(self):
        super().drop()
        if(world.getTile(self.x,self.y).type==Tile.types["lightWater"]):
            world.things.remove(self)
            world.makeThing(self, Flower, size=self.size)
    def use(self):
        ground = world.getTile(self.x, self.y)
        if ground.type==Tile.types["lightWater"]:
            ground.type = Tile.types["ice"]
            world.player.holding=None
        elif not ground.type in [Tile.types["water"],Tile.types["snow"],Tile.types["ice"]]:
            ground.type = Tile.types["snow"]
            world.player.holding=None

class Hatchet(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="hatchet"
        self.uses=5
        self.setSize(1)
    def use(self):
        print("uses:",self.uses)
        filterer = lambda x: x.type in ["tree","stone","flower","iceflower","animus"]
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
                    if(self.type=="mosshatchet"):
                        world.makeThing(thing, Emerald, size=thing.size)
                    else:
                        world.makeThing(thing, Ruby, size=thing.size)
            if(self.uses<=0):
                world.player.holding=None
class MossHatchet(Hatchet):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="mosshatchet"
        self.uses=5
        self.setSize(1)
class Shovel(Thing):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="shovel"
        self.uses=10
        self.setSize(1)
    
    conversion = {5:4,4:3,3:2,2:1,6:1,7:3}

    def use(self):
        print("uses:",self.uses)
        ground = world.getTile(self.x, self.y)
        if ground.type in Shovel.conversion:
            self.uses-=1
            ground.type = Shovel.conversion[ground.type]
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
        if random.random()<0.1:
            ground = world.getTile(self.x,self.y)
            if ground.type==5:
                self.setSize(self.size-0.01)
                if self.size<=0:
                    world.things.remove(self)
            if ground.type==1:
                self.setSize(self.size+0.01)
                if random.random()<0.05:
                    ground.type = Tile.types["sand"]
class SwampTree(Tree):

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="swamptree"
        self.setSize(2)
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
        if ground.type < 2:
            world.things.remove(self)
            if(random.random()<0.3):
                world.makeThing(self, Sapphire, size=self.size)
class Pebble(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="pebble"
        self.setSize(1)

    def use(self):
        ground = world.getTile(self.x,self.y)
        if ground.type == Tile.types["grass"]:
            ground.type = Tile.types["darkGrass"]
            world.player.holding = None
class MossPebble(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="mosspebble"
        self.setSize(1)

    def drop(self):
        super().drop()
        if(world.getTile(self.x,self.y).type==Tile.types["lightWater"]):
            world.things.remove(self)
            world.makeThing(self, WetMossPebble, size=self.size)
class WetMossPebble(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="wetmosspebble"
        self.setSize(1)
    def use(self):
        ground = world.getTile(self.x,self.y)
        if ground.type in [Tile.types["grass"],Tile.types["darkGrass"]]:
            ground.type = Tile.types["swamp"]
            world.player.holding = None

class Sapphire(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="sapphire"
        self.setSize(1)
class Emerald(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="emerald"
        self.setSize(1)
class Stick(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="stick"
        self.setSize(1)

    def use(self):
        ground = world.getTile(self.x,self.y)
        if ground.type == Tile.types["grass"]:
            world.makeThing(world.player, Flower, size=self.size)
            world.player.holding = None
class Stem(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="stem"
        self.setSize(1)
class Berry(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="berry"
        self.setSize(1)
class Mushroom(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="Mushroom"
        self.setSize(1)
class Crystal(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="crystal"
        self.setSize(1)
class MossCrystal(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="mosscrystal"
        self.setSize(1)
class Wand(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="wand"
        self.setSize(1)
        self.uses=5
        self.active=False
    def use(self):
        ground = world.getTile(self.x,self.y)
        if ground.type == Tile.types["grass"]:
            self.uses-=1
            for i in range(math.ceil(random.randint(1,3))):
                world.makeThing(world.player, Flower)
            for i in range(math.ceil(random.randint(0,2))):
                world.makeThing(world.player, Tree, size=1.5)
            if self.uses<=0:
                world.player.holding = None
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
class MossWand(Thing):
    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="mosswand"
        self.setSize(1)
        self.uses=1
        self.active=False
    def use(self):
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                ground = world.getTile(self.x+dx*gridSize,self.y+dy*gridSize)
                if(ground.type > 1):
                    ground.type = Tile.types["swamp"]
        mushrooms=random.randint(4,7)
        berries=random.randint(1,2)
        trees=random.randint(3,4)
        for i in range(mushrooms):
            thing=Mushroom(x=int(self.x/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize),y=int(self.y/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize))
            thing.setSize(min(random.random()*2,0.3))
            world.things.append(thing)
        for i in range(berries):
            thing=Berry(x=int(self.x/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize),y=int(self.y/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize))
            world.things.append(thing)
        for i in range(trees):
            thing=SwampTree(x=int(self.x/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize),y=int(self.y/gridSize)*gridSize+random.randrange(-gridSize,2*gridSize))
            world.things.append(thing)
        self.uses-=1
        if(self.uses==0):
            world.player.holding=None

          
class Animal(Thing): #pass lol
    pass

class Animus(Animal):

    speed = gridSize//16

    def __init__(self,x,y):
        super().__init__(x,y)
        self.type = "animus"
        self.setSize(1)

    def update(self):
        super().update() #pass lol
        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type!=0: #likeit?()
            self.x+=dx
            self.y+=dy
class Gremlin(Animal):
    
    speed = gridSize//16

    def __init__(self,x=0,y=0):
        super().__init__(x,y)
        self.type="gremlin"

        self.setSize(1)

    def update(self):
        super().update() #pass lol

        dx=random.choice([-self.speed,0,self.speed])
        dy=random.choice([-self.speed,0,self.speed])
        if world.getTile(self.x+dx, self.y+dy).type==Tile.types["snow"]:
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

    speed = gridSize//16 # //2 är för sanbbt

    idleImage = loadImage("idle.png")
    def typeFunc(type):

        return lambda x:x.type==type
    def createObject(cls,tool=False):
        def func(things):
            obj = world.makeThing(things[0], cls, size=things[0].size)
            if(tool):
                 obj.uses=max(int(obj.size**1*obj.uses),1)
        return func

    craftingTable = [
    [[typeFunc("stone"), lambda x:x.type=="tree" and x.size<=1],createObject(Hatchet,tool=True)],
    [[typeFunc("pebble"), lambda x:x.type=="tree" and x.size<=1],createObject(Shovel,tool=True)],
    [[typeFunc("log"),typeFunc("stem")],createObject(Stick)],
    [[typeFunc("sapphire")]+[typeFunc("iceflower")]*3,createObject(IceCrystal)],
    [[typeFunc("ruby")]+[typeFunc("flower")]*3,createObject(Crystal)],
    [[typeFunc("icecrystal")]+[typeFunc("stick")],createObject(IceWand,tool=True)],
    [[typeFunc("crystal")]+[typeFunc("stick")],createObject(Wand,tool=True)],
    [[typeFunc("pebble"),typeFunc("stem")],createObject(MossPebble)],
    [[typeFunc("hatchet"),typeFunc("mosspebble")],createObject(MossHatchet,tool=True)],
    [[typeFunc("emerald")]+[typeFunc("wetmosspebble")]*3,createObject(MossCrystal)],
    [[typeFunc("mosscrystal")]+[typeFunc("stick")],createObject(MossWand,tool=True)],

    ]

    def __init__(self, x=16*32//worldgen.Terrain.gridSize*gridSize, y=16*18//worldgen.Terrain.gridSize*gridSize):
        self.x = x
        self.y = y
        self.size = 1
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
                    ground.type = Tile.types["ice"]
                    self.holding.uses-=1
                    if(self.holding.uses==0):
                        self.holding=None
                elif not ground.type in [Tile.types["water"], Tile.types["snow"], Tile.types["ice"]]:
                    print("uses:",self.holding.uses)
                    ground.type = Tiles.types["snow"]
                    self.holding.uses-=1
                    if(self.holding.uses==0):
                        self.holding=None
        if ground.type==0:
            speed*=0.25
        if ground.type==1:
            speed*=0.5
        if ground.type==6:
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
        self.holding.drop() #after appending!
        self.craft() #can craft something else lol
        self.holding = None
        
    def use(self):
        if(self.holding):
            self.holding.use()
        else:
            self.craft()
    def craft(self):
        #add check if holding is in recipes to reduce lag
        for recipe in self.craftingTable:
            things = world.searchMany(world.player,filters=recipe[0],range=1)
            if(things):
                recipe[1](things)

    def draw(self, x, y): #becuase world sends these
        world.camera.drawImage(Player.idleImage, self.x-gridSize*self.size//2, self.y-gridSize*self.size)
        if self.holding:
            self.holding.x=self.x
            self.holding.y=self.y-gridSize//4
            self.holding.draw(self.x,self.y)

def saveWorld():
    print("saving...")
    file = open(world.fileName, "wb")

    for thing in world.things:
        thing.image= None #save picklen
    if world.player.holding:
        world.player.holding.image = None #pkl

    pickle.dump(world, file)
    file.close()
def loadWorld():
    name = "worlds/"+input("World name: ")+".broor"
    try:
        file = open(name, "rb") #read
        world = pickle.load(file)

        for thing in world.things:
            thing.setSize(thing.size) #images back
        holdd = world.player.holding
        if holdd:
            holdd.setSize(holdd.size)

    except Exception as e:
        file = open(name, "x") #create
        world = None
        print("Creating new world...")
    print("worldobject:",world)
    file.close()
    return world, name

def main():
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
        clock.tick(60)

    saveWorld()

    pygame.quit()
    quit()

if __name__ == "__main__":
    world, fileName = loadWorld()
    if world == None:
        world = World() #tthis needs to be global...
        world.generateWorld() #...because this
    world.fileName = fileName
    main()