from math import *
import numpy as np
import os

def sign(a):
    return 1 if a>=0 else -1

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
        self.aspectRatio = ratio = sizeY/sizeX*17/7
        #set coordinate range
        self.rangeX = np.array([-10,10])
        self.rangeY = -self.rangeX*ratio
        #create coordinate matrices
        self.coordsX =  np.linspace(self.rangeX[0], self.rangeX[1],sizeX)
        self.coordsY =  np.linspace(self.rangeY[0], self.rangeY[1],sizeY)
        self.coords = np.zeros((winY,winX))  #array with numerical coords 

        self.framebuffer = np.full(self.coords.shape,' ') #array with pixels
        self.charMap = {' ':' ', '<':'<', '>':'>', '_':'─','^':'˄','v':'˅','|':'│','+':'┼','.':'¤'}


    def drawAxes(self):
        for i in range(self.sizeY):
            for j in range(self.sizeX):
                c = ' '
                if i == round(self.sizeY/2):
                    if j == 0:
                        c = self.charMap['<']
                    elif j == self.sizeX-1:
                        c = self.charMap['>']
                    else:
                        c = self.charMap['_']
                if j == round(self.sizeX/2):
                    if i == 0:
                        c = self.charMap['^']
                    elif i == self.sizeY-1:
                        c = self.charMap['v']
                    else:
                        c = self.charMap['|']
                if j == round((self.sizeX)/2) and i == round((self.sizeY)/2):
                    c = self.charMap['+']
                self.framebuffer[i][j] = c


    def render(self):
        for row in self.framebuffer:
            for pixel in row:
                print(str(pixel)[0], end='')

    def plot(self):
        for row in range(self.sizeY):
            for col in range(self.sizeX):
                eq = 'y-tan(x)' #((1/4*y)^2+(1/4*x)^2-1)^3-(1/4*x)^2*(1/4*y)^3
                eq = eq.replace('x','self.coordsX[col]').replace('y','self.coordsY[row]').replace('^','**')
                val=eval(eq)
                if row == 0 or col == 0:
                    sgneq=sign(val)
                if sign(val) != sgneq:
                    self.framebuffer[row][col] = self.charMap['.'] 
                    sgneq=sign(val)               
                




if __name__ == '__main__':
    plot = Framebuffer()
    plot.drawAxes()
    plot.plot()
    plot.render()

