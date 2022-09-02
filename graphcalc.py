import numpy as np
import os
from numpy import sqrt, sin, cos, tan, sign, abs

def reverseDict(d):
    return dict([(val,key) for key,val in list(d.items())])

class SquareMap():
    def __init__(self):
        self.boundary = {'[[1, -1], [-1, -1]]':'/', 
                        '[[-1, 1], [-1, -1]]':'\\',
                        '[[-1, -1], [1, -1]]':'\\',
                        '[[-1, -1], [-1, 1]]':'/',
                        '[[1, 1], [-1, -1]]':'─',
                        '[[-1, -1], [1, 1]]':'─',
                        '[[1, -1], [1, -1]]':'│',
                        '[[-1, 1], [-1, 1]]':'│',
                        '[[1, -1], [-1, 1]]':'╲',
                        '[[-1, 1], [1, -1]]':'╱',
                        '[[-1, 1], [1, 1]]':'/',
                        '[[1, -1], [1, 1]]':'\\',
                        '[[1, 1], [-1, 1]]':'\\',
                        '[[1, 1], [1, -1]]':'/'}

        self.fillin = { '[[1, 1], [1, 1]]':'▓',
                        '[[0, 0], [0, 0]]': ' ' }

        self.fillout = {'[[-1, -1], [-1, -1]]':'░'}

        self.all = {}
        self.all.update(self.boundary)
        self.all.update(self.fillin)
        self.all.update(self.fillout)

class Framebuffer():
    def __init__(self, sizeX=-1, sizeY=-1):
        #
        self.setSize(sizeX=-1, sizeY=-1)
        self.setRange(-10,-10,10,10)
        self.fixAspectRatio()
        #
        self.antialiasing = 2
        self.charMap = {' ': ' ', '<': '<', '>': '>', '_': '─',
                        '^': '˄', 'v': '˅', '|': '│', '+': '┼',
                        '.': '¤'}
        self.symbols = { '*':'*','^':'**','+':'+','-':'-','/':'/',')':')'}
        self.modes = {'=':'=','>':'>','<':'<','>=':'≥','<=':'≤','!=':'≠'}
        self.symbols.update(self.modes)

        self.squareStates = SquareMap()

    def setSize(self, sizeX=-1, sizeY=-1):
        # detect screen size
        if sizeX < 0 or sizeY < 0:
            winX, winY = os.get_terminal_size()
            winY -= 2
            if sizeX < 0:
                sizeX = winX
            if sizeY < 0:
                sizeY = winY
        # set size
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.aspectRatio = sizeY/sizeX*17/7

        self.framebuffer = np.full((self.sizeY, self.sizeX), ' ')  # array with 

    def setRange(self, minX, minY, maxX, maxY):
        self.rangeX = np.array([minX,maxX])
        self.rangeY = np.array([minY,maxY])

    def fixAspectRatio(self, axis=1):
        if axis == 1:
            self.rangeY = self.rangeX * self.aspectRatio
        elif axis == 0:
            self.rangeX = self.rangeY / self.aspectRatio

        
    def drawAxes(self):
        # for i in range(self.sizeY):
        #     for j in range(self.sizeX):
        #         c = ' '
        #         if i == round(self.sizeY/2):
        #             if j == 0:
        #                 c = self.charMap['<']
        #             elif j == self.sizeX-1:
        #                 c = self.charMap['>']
        #             else:
        #                 c = self.charMap['_']
        #         if j == round(self.sizeX/2):
        #             if i == 0:
        #                 c = self.charMap['^']
        #             elif i == self.sizeY-1:
        #                 c = self.charMap['v']
        #             else:
        #                 c = self.charMap['|']
        #         if j == round((self.sizeX)/2) and i == round((self.sizeY)/2):
        #             c = self.charMap['+']
        #         self.framebuffer[i][j] = c

        pass

    def render(self):
        for row in self.framebuffer:
            for pixel in row:
                print(str(pixel)[0], end='')

    def parseEquation(self, equationString):
        # convert <= and >= to single cahrs for check
        for key, val in self.symbols.items():
            equationString = equationString.replace(key,val)

                    
        #reorder equation
        mode = self.equationMode(equationString)
        if mode in equationString:
            left,right = equationString.split(mode)
        else:
            left, right = equationString, '0'
        equationString = left + '-(' + right + ')'+mode+'0'
                    
        # add multiplications
        i = 0
        while True:
            if i < len(equationString)-1:
                char = equationString[i]
                nextChar = equationString[i+1]
                if char.isdigit() and not nextChar.isdigit() and not nextChar in self.symbols:
                    equationString = equationString[:i+1] + '*' + equationString[i+1:]
                i += 1
            else:
                break

        return equationString

    def equationMode(self, equationString): # return 'equaton (=, !=)' or 'inequality (>, <, >=, <=)'
        mode = ''
        for key, val in self.modes.items():
            if val in equationString:
                mode=val
                break
            elif key in equationString:
                mode = key
                break
        return mode if mode != '' else '='

    def plot(self, equationString):
        eq = self.parseEquation(equationString)
        mode = self.equationMode(eq)
        asciiMode = reverseDict(self.modes)[mode]
        if mode in eq:
            eq = eq.split(mode)[0]
        print(eq)
        # create coordinate matrices
        self.coordsX = np.array([np.linspace(self.rangeX[0], self.rangeX[1], self.sizeX * self.antialiasing)], dtype='complex128').repeat(self.sizeY * self.antialiasing , axis=0)
        self.coordsY = np.array([np.linspace(self.rangeY[1], self.rangeY[0], self.sizeY * self.antialiasing)], dtype='complex128').transpose().repeat(self.sizeX * self.antialiasing, axis=1)
        
        self.coords = eval(eq.replace('x','self.coordsX').replace('y','self.coordsY'))  # array with numerical coords

        #march squares
        for row in range(self.sizeY):
            for col in range(self.sizeX):
                i=row*2
                j=col*2
                square=str(np.sign(self.coords[i:i+2, j:j+2]).astype(int).tolist())
                pixel = self.squareStates.all[square]

                equiationPixel = asciiMode in ['=', '>=', '<='] and square in self.squareStates.boundary
                inequalityPixel = asciiMode in ['<','!=','<='] and square in self.squareStates.fillout
                inequationPixel = asciiMode in ['>','!=','>='] and square in self.squareStates.fillin
                if not pixel in [' ', '']:
                    if equiationPixel or inequalityPixel or inequationPixel:
                        self.framebuffer[row][col] = pixel

if __name__ == '__main__':
    plot = Framebuffer()
    while 1:
        eq = input('Equation: ')
        if len(eq)<1:
            break
        # print(plot.parseEquation(eq))
        plot.setSize()
        plot.setRange(-4,-4,4,4)
        plot.fixAspectRatio()
        plot.drawAxes()
        plot.plot(eq)
        plot.render()
