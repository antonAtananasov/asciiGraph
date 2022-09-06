import numpy as np
import os, sys
from numpy import sqrt, sin, cos, tan, sign, abs, sinh, cosh, tanh,log,log10, exp, log2, arcsin, arccos,arctan, degrees, radians, arcsinh, arccosh, arctanh, sinc
import random

#additional math functions
def cot(a):
    return 1/tan(a)
def ctg(a):
    return cot(a)
def cotg(a):
    return cot(a)
def tg(a):
    return tan(a)
def sec(a):
    return 1/cos(a)
def csc(a):
    return 1/sin(a)

#dictionary operations
def reverseDict(d):
    return dict([(val,key) for key,val in list(d.items())])
def selectDictVariant(d,variant):
    return dict([(key,val[variant] if variant < len(val) else '�') for key,val in list(d.items())])

class SquareMap():
    def __init__(self, charmapVariant=0):
        #enumerate all character sets
        self.charmapBoundaryVariants = {
            '[[1, -1], [-1, -1]]':['/','▘','╯'], 
            '[[-1, 1], [-1, -1]]':['\\','▝','╰'],
            '[[-1, -1], [1, -1]]':['\\','▖','╮'],
            '[[-1, -1], [-1, 1]]':['/','▗','╭'],
            '[[1, 1], [-1, -1]]':['-','▀','─'],
            '[[-1, -1], [1, 1]]':['-','▄','─'],
            '[[1, -1], [1, -1]]':['|','▌','│'],
            '[[-1, 1], [-1, 1]]':['|','▐','│'],
            '[[1, -1], [-1, 1]]':['╲','▚','╲'],
            '[[-1, 1], [1, -1]]':['╱','▞','╱'],
            '[[-1, 1], [1, 1]]':['/','▟','┘'],
            '[[1, -1], [1, 1]]':['\\','▙','└'],
            '[[1, 1], [-1, 1]]':['\\','▜','┐'],
            '[[1, 1], [1, -1]]':['/','▛','┌']                
            }
        self.charmapFillinVariants = { 
            '[[1, 1], [1, 1]]':['#','▓','▓'],
            '[[0, 0], [0, 0]]': [' ',' ',' '] 
            }
        self.charmapFilloutVariants = {
            '[[-1, -1], [-1, -1]]':['#','░','░']
            }

        #create group for checking valid marching square 
        self.allVariants={}
        self.allVariants.update(self.charmapBoundaryVariants)
        self.allVariants.update(self.charmapFillinVariants)
        self.allVariants.update(self.charmapFilloutVariants)

        self.setCharmapVariant(charmapVariant)
        self.variantCount = np.max([len(val) for key,val in self.allVariants.items()])

    #select subset
    def setCharmapVariant(self, charmapVariant):
        self.boundary = selectDictVariant(self.charmapBoundaryVariants, charmapVariant)
        self.fillin = selectDictVariant(self.charmapFillinVariants, charmapVariant)
        self.fillout = selectDictVariant(self.charmapFilloutVariants, charmapVariant)

        self.all = {}
        self.all.update(self.boundary)
        self.all.update(self.fillin)
        self.all.update(self.fillout)



class Framebuffer():
    def __init__(self, sizeX=-1, sizeY=-1):
        #window/canvas setup
        self.setSize(sizeX=-1, sizeY=-1)
        self.setRange(-10,-10,10,10)
        self.fixAspectRatio()
        
        #basic character substitution to use keyboard easier
        self.charMap = {' ': ' ', '<': '<', '>': '>', '_': '─',
                        '^': '˄', 'v': '˅', '|': '│', '+': '┼',
                        '.': '·'}
        #for parsing equations
        self.symbols = { '*':'*','^':'**','+':'+','-':'-','/':'/',')':')'}
        #evaluation modes
        self.modes = {'=':'=','>':'>','<':'<','>=':'≥','<=':'≤','!=':'≠',',':','}
        self.symbols.update(self.modes)
        #select graphical symbols
        self.charmapVariant = 0
        self.squareStates = SquareMap()

    def setSize(self, sizeX=-1, sizeY=-1):
        # detect screen size
        if sizeX < 0 or sizeY < 0:
            winX, winY = os.get_terminal_size()
            winY -= 2
            winX -= 1
            if sizeX < 0:
                sizeX = winX
            if sizeY < 0:
                sizeY = winY
        # set size
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.aspectRatio = sizeY/sizeX*32/16

        #prepare framebuffer
        self.framebuffer = np.full((self.sizeY, self.sizeX), ' ')  # array with ascii pixels

    def setRange(self, minX, minY, maxX, maxY):
        self.rangeX = np.array([minX,maxX])
        self.rangeY = np.array([minY,maxY])

    def fixAspectRatio(self, axis=1):
        if axis == 1:
            self.rangeY = self.rangeX * self.aspectRatio
        elif axis == 0:
            self.rangeX = self.rangeY / self.aspectRatio

        
    def drawAxes(self):
        self.plot('y=0','-')
        self.plot('x=0','|')
        pass

    def render(self):
        for row in self.framebuffer:
            for pixel in row:
                print(str(pixel)[0], end='')
            print('')

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
                if char.isdigit() and not nextChar.isdigit() and not nextChar in self.symbols and not nextChar in self.modes:
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
    
    # def point(self, pointString, fill='·'):
    #     pointString = self.parseEquation(pointString).replace('(','[').replace(')',']')
        
    #     coordsX = np.array([np.linspace(self.rangeX[0], self.rangeX[1], self.sizeX)], dtype='complex_').repeat(self.sizeY + 1 , axis=0)
    #     coordsY = np.array([np.linspace(self.rangeY[1], self.rangeY[0], self.sizeY)], dtype='complex_').transpose().repeat(self.sizeX + 1, axis=1)
    #     coords = np.array(zip(coordsX,coordsY))-np.array(eval(pointstring)) # array with numerical coords
        

    def plot(self, equationString, fill=''):
        eq = self.parseEquation(equationString)
        mode = self.equationMode(eq)
        asciiMode = reverseDict(self.modes)[mode]
        if mode in eq:
            eq = eq.split(mode)[0]
        # create coordinate matrices
        coordsX = np.array([np.linspace(self.rangeX[0], self.rangeX[1], self.sizeX + 1)], dtype='complex_').repeat(self.sizeY + 1 , axis=0)
        coordsY = np.array([np.linspace(self.rangeY[1], self.rangeY[0], self.sizeY + 1)], dtype='complex_').transpose().repeat(self.sizeX + 1, axis=1)
        
        coords = eval(eq.replace('x','coordsX').replace('y','coordsY'))  # array with numerical coords

        #update character set
        self.squareStates.setCharmapVariant(self.charmapVariant)
        #march squares
        for row in range(self.sizeY):
            for col in range(self.sizeX):
                submatrix = coords[row:row+2, col:col+2]
                #get sign of dots (elements) in submatrix 
                square=str(np.sign(submatrix).real.astype(int).tolist())
                pixel = ' '
                #check if submatrix is valid
                if square in self.squareStates.all:
                    pixel = self.squareStates.all[square]
                
                #chech type of equality and type of square
                equiationPixel = asciiMode in ['=', '>=', '<='] and square in self.squareStates.boundary
                inequalityPixel = asciiMode in ['<','!=','<='] and square in self.squareStates.fillout
                inequationPixel = asciiMode in ['>','!=','>='] and square in self.squareStates.fillin
                
                #for reserved for checks in the future 
                asymptote = False
                
                if not pixel in [' ', ''] and not asymptote:
                    if equiationPixel or inequalityPixel or inequationPixel:
                        self.framebuffer[row][col] = pixel if fill in ['', ' '] else fill

#=============================================================================================================================================================

w,h=os.get_terminal_size()
resize = True
if len(sys.argv) >= 3:
    w=int(str(sys.argv[1]))
    h=int(str(sys.argv[2]))
if len(sys.argv) == 4:
    resize=int(str(sys.argv[3]))
    print(resize)
    

if __name__ == '__main__':
    plot = Framebuffer()
    while 1:
        eq = input('Equation: ')
        if len(eq)<1:
            break

        plot.setSize() if resize else plot.setSize(w,h)
        plot.setRange(-4,-4,4,4)
        plot.fixAspectRatio()
        plot.drawAxes()
        plot.plot(eq)
        plot.render()
