import numpy as np
import os
from numpy import sqrt, sin, cos, tan, sign, abs


class Framebuffer():
    def __init__(self, sizeX=-1, sizeY=-1):
        #
        self.setSize(sizeX=-1, sizeY=-1)
        self.rangeX = np.array([-10,10])
        self.rangeY = self.rangeX * self.aspectRatio
        #
        self.antialiasing = 2
        self.charMap = {' ': ' ', '<': '<', '>': '>', '_': '─',
                        '^': '˄', 'v': '˅', '|': '│', '+': '┼',
                        '.': '¤', '>=':'≥','<=':'≥','!=':'≠'}

        self.squareStates = {'[[-1, -1], [-1, -1]]':'░',
                        '[[1, -1], [-1, -1]]':'/',
                        '[[-1, 1], [-1, -1]]':'\\',
                        '[[-1, -1], [1, -1]]':'\\',
                        '[[-1, -1], [-1, 1]]':'/',
                        '[[1, 1], [-1, -1]]':'-',
                        '[[-1, -1], [1, 1]]':'-',
                        '[[1, -1], [1, -1]]':'|',
                        '[[-1, 1], [-1, 1]]':'|',
                        '[[1, -1], [-1, 1]]':'\\',
                        '[[-1, 1], [1, -1]]':'/',
                        '[[-1, 1], [1, 1]]':'/',
                        '[[1, -1], [1, 1]]':'\\',
                        '[[1, 1], [-1, 1]]':'\\',
                        '[[1, 1], [1, -1]]':'/',
                        '[[1, 1], [1, 1]]':'▓'}

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

    def fixResize(self):
        self.rangeY = self.rangeX * self.aspectRatio

        
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

    def parseEquation(self, equationString):
        # convert carrets to exponent powers
        equationString = equationString.replace('^', '**')
        # convert <= and >= to signgle cahrs for check
        equationString = equationString.replace('<=',self.charMap['<=']).replace('>=',self.charMap['>=']).replace('!=',self.charMap['!='])
        #reorder equation
        mode = self.equationMode(equationString)
        if mode in equationString:
            left,right = equationString.split(mode)
        else:
            left, right = equationString, '0'
        equationString = left + '-(' + right + ')'+mode+'0'
                    
        return equationString

    def equationMode(self, equationString): # return 'equaton (=, !=)' or 'inequality (>, <, >=, <=)'
        mode = ''
        for char in ['=','>','<', self.charMap['<='], self.charMap['>='], self.charMap['!=']]:
            if char in equationString:
                mode=char
                break
        return mode if mode != '' else '='

    def plot(self, equationString):
        eq = self.parseEquation(equationString)
        mode = self.equationMode(eq)
        if mode in eq:
            eq = eq.split(mode)[0]
        # create coordinate matrices
        self.coordsX = np.array([np.linspace(self.rangeX[0], self.rangeX[1], self.sizeX * self.antialiasing)]).repeat(self.sizeY * self.antialiasing , axis=0)
        self.coordsY = np.array([np.linspace(self.rangeY[1], self.rangeY[0], self.sizeY * self.antialiasing)]).transpose().repeat(self.sizeX * self.antialiasing, axis=1)
        
        self.coords = eval(eq.replace('x','self.coordsX').replace('y','self.coordsY'))  # array with numerical coords

        #march squares
        for row in range(self.sizeY):
            for col in range(self.sizeX):
                i=row*2
                j=col*2
                square=str(np.sign(self.coords[i:i+2, j:j+2]).astype(int).tolist())
                pixel = self.squareStates[square]
                if pixel != ' ':
                    if (mode == '=' and not pixel in ['░','▓']) or (mode == self.charMap['!='] and pixel in ['░','▓']) or (mode == '>' and pixel != '░') or (mode == '<' and pixel != '▓') :
                        self.framebuffer[row][col] = pixel


if __name__ == '__main__':
    plot = Framebuffer()
    while 1:
        eq = input('Equation: ')
        if len(eq)<1:
            break
        # print(plot.parseEquation(eq))
        plot.setSize()
        plot.fixResize()
        plot.drawAxes()
        plot.plot(eq)
        plot.render()
