import pygame
import random
import math
import noise

class Terrain():
    def __init__(self):
        pass
    gridSize = 4
    noiseScale = 50 # 100
    biomeScale = 8 # 8
    biomePercentage=0.7 # 0.6
    biomeSettings=[1,0.5,2] # [1,0.5,2]
    terrainSettings=[5,0.6,2] # [5,0.6,2] 
    islandFactor=0.7 
    islandSize=40

    noiseBase = random.randrange(0,100)
    noiseBiomeBase = random.randrange(0,100)
    noiseMap = []
    biomeNoiseScale = noiseScale*biomeScale
    for y in range(int(32*18/gridSize)):
        noiseMap.append([])

    waterlevel = 50 #20 if worley
    snowlevel = 75 #40 if worely
    scheme = [[waterlevel-10,0],[waterlevel,1],[waterlevel+5,2],[waterlevel+15,3],[snowlevel,4],[101,5]]
    colors = [[8, 59, 140],[14, 85, 199],[222, 214, 122],[84, 168, 69],[26, 102, 12],[243, 247, 225]]

    def draw(self):
        for x in range(int(32*32/self.gridSize)):
                for y in range(int(32*18/self.gridSize)):
                    c = self.colors[self.noiseMap[y][x]]
                    pygame.draw.rect(gameDisplay,c,pygame.Rect(x*self.gridSize,y*self.gridSize,self.gridSize,self.gridSize))
    
    def generate(self):
        for x in range(int(32*32/self.gridSize)):
                for y in range(int(32*18/self.gridSize)):
                    
                    distanceToEdge=min(min(x,2*32*16/self.gridSize-x),min(y,2*18*16/self.gridSize-y))
                    if(distanceToEdge<self.islandSize):
                        noiseMultiple=1-self.islandFactor*((self.islandSize-distanceToEdge)/self.islandSize)
                    else:
                        noiseMultiple=1

                    
                    noiseBiome=generateNoise(x,y,self.gridSize/self.biomeNoiseScale,self.noiseBiomeBase,self.biomeSettings[0],self.biomeSettings[1],self.biomeSettings[2],multiple=noiseMultiple)
                    noiseTerrain=generateNoise(x,y,self.gridSize/self.noiseScale,self.noiseBase,self.terrainSettings[0],self.terrainSettings[1],self.terrainSettings[2],multiple=noiseMultiple)*(1-self.biomePercentage)+noiseBiome*self.biomePercentage
                    c = generateTerrain(noiseTerrain,self.scheme)

                    self.noiseMap[y].append(c)
    
    def returnWorld(self):
        return self.noiseMap

def coord(*arg):
    return [x*32*scaleFactor for x in arg]
def generateNoise(x,y,noiseFactor,noiseBase,octaves=5,persistence=0.3,lacunarity=3.0,multiple=1):
    noiseLayers = noise.snoise2(noiseFactor*x,noiseFactor*y,base=noiseBase,octaves=octaves,persistence=persistence,lacunarity=lacunarity)
    return multiple*((noiseLayers+1)/2)
def generateTerrain(noiseValue,scheme):
    elevation = 100*noiseValue
    for elevationColor in scheme:
        if(elevation<elevationColor[0]):
            return elevationColor[1]










#all
if(__name__=="__main__"):
    terrain=Terrain()
    terrain.generate()
    scaleFactor = 1/4
    global gameDisplay
    gameDisplay = pygame.display.set_mode((32*32, 32*18))

    jump_out = False
    changed=0



    while jump_out == False:
        #s = input("rule: ")

        if(changed==0):
            
            

                
            terrain.draw()   
            changed=0
        jump_out = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jump_out = True
        if jump_out:
            pygame.display.quit()
            quit()
        pygame.display.update()
        

    pt.end_program()    
