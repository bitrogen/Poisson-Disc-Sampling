import numpy
import math
import random
from PIL import Image,ImageDraw,ImageFont
import os

# https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf
# https://github.com/SebLague/Poisson-Disc-Sampling/blob/master/Poisson%20Disc%20Sampling%20E01/PoissonDiscSampling.cs

class Bridson:
    def __init__(self):

        self.samples = []
        self.activeList = []
        self.radius = 30
        self.cellSize = self.radius/math.sqrt(2)
        self.sampleRegionSize2 =(1920, 1080)
        self.sampleRegionSize = (1720, 880)
        self.grid = numpy.zeros((math.ceil(self.sampleRegionSize[0]/self.cellSize), math.ceil(self.sampleRegionSize[0]/self.cellSize)))
        self.limitOfSamplesBeforeRejection = 1
        self.margin = 100
        self.imageIndex = 0
        self.sphere = 10
        self.trial = 0

        self.visualize()
        self.poissionDiscSampling()
        self.visualize()

    def poissionDiscSampling(self):


        initialSample = numpy.array([int(self.sampleRegionSize[0]/2), int(self.sampleRegionSize[1]/2)]) # start point
        self.activeList = [initialSample]
        self.visualize(spawnCentre=initialSample)

        while len(self.activeList) > 0:
            activeIndex = random.randrange(len(self.activeList))
            spawnCentre = self.activeList[activeIndex]
            candidateAccepted = False

            for _ in range(self.limitOfSamplesBeforeRejection):
                angle = random.random() * math.pi * 2
                direction = numpy.array([math.sin(angle), math.cos(angle)])
                candidate = spawnCentre + numpy.floor(direction * random.randrange(self.radius, 2*self.radius)).astype(int)
                self.trial += 1
                # self.visualize(candidate=candidate, spawnCentre=spawnCentre)

                if self.isValid(candidate):
                    self.samples.append(candidate)
                    self.grid[int(candidate[0]/self.cellSize)][int(candidate[1]/self.cellSize)] = len(self.samples)
                    candidateAccepted = True
                    self.activeList.append(candidate)
                    self.visualize(valid=candidate, spawnCentre=spawnCentre)
                    break

                else:    
                    self.visualize(notValid=candidate, spawnCentre=spawnCentre)

            if candidateAccepted is False:
                self.visualize()
                self.activeList.pop(activeIndex)

        return self.samples

    def isValid(self, candidate):
        # check if the candidate is outside of border
        if 0 <= candidate[0] < self.sampleRegionSize[0] and 0 <= candidate[1] < self.sampleRegionSize[1]:
            cellx = int(candidate[0]/self.cellSize)
            celly = int(candidate[1]/self.cellSize)
            searchStartX =max(0, cellx-2)
            searchEndX = min(cellx+2, self.grid.shape[0])

            searchStartY = max(0, celly-2)
            searchEndY = min(celly+2, self.grid.shape[1])

            for x in range(searchStartX, searchEndX):
                for y in range(searchStartY, searchEndY):
                    pointIndex = self.grid[x][y]-1

                    if pointIndex != -1:
                        distanceSquare = self.getDistanceSquare(self.samples[int(pointIndex)], candidate)

                        if distanceSquare < self.radius**2:
                            return False

            return True

        else:
            # Out of borders
            return False

    def getDistanceSquare(self, a, b):
        differenceInXAxis = abs(a[0] - b[0])
        differenceInYAxis = abs(a[1] - b[1])

        return differenceInXAxis**2 + differenceInYAxis**2

    def visualize(self, candidate=None, valid=None, notValid=None, spawnCentre=None):
        image = Image.new("RGB",self.sampleRegionSize2, (0,0,20))
        draw = ImageDraw.Draw(image)

        for point in self.samples:
            leftUpPoint = (int(point[0]+self.margin)-self.sphere, int(point[1]+self.margin)-self.sphere)
            rightDownPoint = (int(point[0]+self.margin)+self.sphere, int(point[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="gray")

        for point in self.activeList:
            leftUpPoint = (int(point[0]+self.margin)-self.sphere, int(point[1]+self.margin)-self.sphere)
            rightDownPoint = (int(point[0]+self.margin)+self.sphere, int(point[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="blue")

        if candidate is not None:
            leftUpPoint = (int(candidate[0]+self.margin)-self.sphere, int(candidate[1]+self.margin)-self.sphere)
            rightDownPoint = (int(candidate[0]+self.margin)+self.sphere, int(candidate[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="yellow")

        if valid is not None:
            leftUpPoint = (int(valid[0]+self.margin)-self.sphere, int(valid[1]+self.margin)-self.sphere)
            rightDownPoint = (int(valid[0]+self.margin)+self.sphere, int(valid[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="green")

        if notValid is not None:
            leftUpPoint = (int(notValid[0]+self.margin)-self.sphere, int(notValid[1]+self.margin)-self.sphere)
            rightDownPoint = (int(notValid[0]+self.margin)+self.sphere, int(notValid[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="red")

        if spawnCentre is not None:
            leftUpPoint = (int(spawnCentre[0]+self.margin)-self.sphere, int(spawnCentre[1]+self.margin)-self.sphere)
            rightDownPoint = (int(spawnCentre[0]+self.margin)+self.sphere, int(spawnCentre[1]+self.margin)+self.sphere)
            twoPointList = [leftUpPoint, rightDownPoint]
            draw.ellipse(twoPointList, fill="#FC0FC0")


        font = ImageFont.truetype(f"{os.getcwd()}//OpenSans-Light.ttf",size=25)
        text = f"Radius: {self.radius} | k: {self.limitOfSamplesBeforeRejection} | Trials: {self.trial} | Active List: {len(self.activeList)} | Samples: {len(self.samples)}"
        textSize = font.getsize(text)
        boxSize = (textSize[0]+20, textSize[1]+20)
        Box = Image.new("RGB", boxSize, "#005aab")
        boxDraw = ImageDraw.Draw(Box)
        boxDraw.text((10,10),text,font=font)
        image.paste(Box, (10, 10))

        image.save(f"{os.getcwd()}//frames//image-{self.imageIndex}.png")
        print(f"[{self.imageIndex}] image processed")
        self.imageIndex += 1


if __name__ == "__main__":
    bridson = Bridson()
