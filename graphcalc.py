from cmath import pi
import numpy as np
import os


def map(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


class Framebuffer():
    def __init__(self, sizeX=-1, sizeY=-1):
        #detect screen size
        if sizeX < 0 or sizeY < 0:
            winX, winY = os.get_terminal_size()
            winY -= 2
            if sizeX < 0:
                sizeX = winX
            if sizeY < 0:
                sizeY = winY
        #set size
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.aspectRatio = ratio = sizeY/sizeX
        #set coordinate range
        self.rangeX = np.array([-10,10])
        self.rangeY = self.rangeX*ratio
        #create coordinate matrices
        self.coordsX =  np.linspace(self.rangeX[0], self.rangeX[1],sizeX)
        self.coordsY =  np.linspace(self.rangeY[0], self.rangeY[1],sizeY)
        self.coords = np.zeros((winY,winX))  #array with numerical coords 

        self.framebuffer = np.full(self.coords.shape,' ') #array with pixels


    def drawAxes(self):
        for i in range(self.sizeY):
            for j in range(self.sizeX):
                c = ' '
                if i == self.sizeY//2:
                    if j == 0:
                        c = '<'
                    elif j == self.sizeX-1:
                        c = '>'
                    else:
                        c = '─'
                if j == self.sizeX//2:
                    if i == 0:
                        c = '^'
                    elif i == self.sizeY-1:
                        c = 'v'
                    else:
                        c='│'
                if j == self.sizeX//2 and i == self.sizeY//2:
                    c='┼'
                self.framebuffer[i][j] = c


    def render(self):
        for row in self.framebuffer:
            for pixel in row:
                print(str(pixel)[0], end='')




if __name__ == '__main__':
    plot = Framebuffer()
    plot.drawAxes()
    plot.render()

