# Imports
import pygame as py
import sys
from pygame import *
from pygame import gfxdraw
from ButtonClass import Button
from LoadSave import Load_Save
from NamerLogic import Namer
import math

py.init()

# Specific Variables

PosUsed = []
PosUsedElement = []
# BondUsed describes connected elements, BondArea describes area the bond symbol is drawn
BondUsed = []
BondArea = []
BondStrength = []
BondAngles = []
ElementType = 0
# Bias is how much the screen has been dragged, IntBias is the Bias of when the first element is placed
Bias_x = 0
Bias_y = 0
IntBias_x = 0
IntBias_y = 0
Dropped = False
Grid_Drag = False
Element_Drag = False

# Dimensions
# The use of X is to differentiate drawn areas and their respective functions
SideBorderX = (0, 0, 800, 450)
SideBarX = [640, 0, 800, 450]

ElementTitleX = [660, 42, 120, 40]

DropButtonX = [640, 0, 44, 22]
DroppedButtonX = [756, 0, 44, 22]

ArrowOpenX = (658, 6), (667, 11), (658, 16)
ArrowCloseX = (782, 6), (773, 11), (782, 16)

DisplayNameX = [130, 20, 380, 65]
DroppedDisplayNameX = [210, 20, 380, 65]

HomeButtonX = [33, 20, 65, 65]

RelInfoX = [0, 410, 642, 40]
DroppedRelInfoX = [0, 410, 800, 40]

ReposX = [575, 40, 25, 25]
DroppedReposX = [655, 40, 25, 25]

ResetX = [530, 40, 25, 25]
DroppedResetX = [610, 40, 25, 25]

CArea = [657, 105, 56, 56]
HArea = [727, 105, 56, 56]
OArea = [657, 170, 56, 56]
NArea = [727, 170, 56, 56]
FArea = [657, 235, 56, 56]
ClArea = [727, 235, 56, 56]
BrArea = [657, 300, 56, 56]
IArea = [727, 300, 56, 56]

# Colours
BACKGROUND = (232, 223, 197)
SIDEBAR = (201, 196, 182)
SELECT = (229, 224, 210)
SELTEXT = (168, 153, 97)
NONSELECT = (213, 198, 157)
NONSELTEXT = (152, 136, 76)
GRIDCOLOUR = (205, 177, 85)
WHITE = (255, 255, 255)
BUTTON = (229, 224, 210)
BLACK = (0, 0, 0)


# Definitions

# General Calculations
def offnum(num, point):
    if num > 0:
        rounded = math.ceil(num / point)
    elif num < 0:
        rounded = math.floor(num / point)
    elif num == 0:
        rounded = 0

    return rounded


def Area(region, point):
    if region[0] < point[0] < (region[0] + region[2]) and region[1] < point[1] < (region[1] + region[3]):
        return True
    else:
        return False

# Events that occur in MOUSEDOWN regardless of the state of Dropped
def MouseDown(Mouse, BondInfo):
    global Grid_Drag, Grid_pos_x, Grid_pos_y
    if len(BondInfo) > 0:
        BondPos = BondInfo[0]
        # BondInfo = [BondPos, strength, already existing?]
        # BondPos = [[First element pos, second element pos], angle]
        if not BondInfo[2]:
            BondAngles.append(BondPos[1])
            BondUsed.append(BondPos[0])
            BondStrength.append(BondInfo[1])
            BondArea.append(BondInfo[3])
        else:
            BondStrength[BondUsed.index(BondPos[0])] = BondInfo[1]

    ElementRedrag(Mouse)

    if not Element_Drag:
        Grid_Drag = True
        Grid_pos_x = - Mouse[0]
        Grid_pos_y = - Mouse[1]

# Drawing screen pieces
def DrawGrid():
    offset_x = int(offnum(Bias_x, 80))
    offset_y = int(offnum(Bias_y, 50))

    # The specific combination of offset and bias allows for the grid to smoothly redraw itself with the mouse drag
    for y in range(- offset_y, 11 - offset_y):
        for x in range(-2 - offset_x, 11 - offset_x):
            Grid_Pos = py.Rect(80 * x + Bias_x, 50 * (y - 1) + Bias_y, 80, 50)
            py.draw.rect(WINDOW, GRIDCOLOUR, Grid_Pos, 1)

    # Keeping the window's outside border in this function for convenience
    py.draw.rect(WINDOW, BLACK, SideBorderX, 2)

    py.draw.rect(WINDOW, SELECT, HomeButtonX, border_radius=6)
    py.draw.rect(WINDOW, BLACK, HomeButtonX, 2, border_radius=6)
    house = py.image.load('LilHouse.png')
    housescale = py.transform.scale(house, (house.get_rect().width / 14, house.get_rect().height / 14))
    WINDOW.blit(housescale, (37, 23))


def SideBar():
    # All non-interactive elements of the sidebar
    py.draw.rect(WINDOW, SIDEBAR, SideBarX)
    py.draw.rect(WINDOW, BLACK, SideBarX, 2)

    py.draw.rect(WINDOW, NONSELECT, ElementTitleX, border_radius=6)
    py.draw.rect(WINDOW, BLACK, ElementTitleX, 2, border_radius=6)

    Font = py.font.SysFont('comicsansms', 25)
    ElementTitle = Font.render('Elements', True, NONSELTEXT)
    WINDOW.blit(ElementTitle, (666, 45))


def DropDown():
    if Dropped:
        py.draw.rect(WINDOW, SELECT, DroppedButtonX)
        py.draw.rect(WINDOW, BLACK, DroppedButtonX, 2)
        py.gfxdraw.aapolygon(WINDOW, ArrowCloseX, BLACK)
        py.gfxdraw.filled_polygon(WINDOW, ArrowCloseX, BLACK)

        py.draw.rect(WINDOW, NONSELECT, DroppedDisplayNameX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, DroppedDisplayNameX, 2, border_radius=6)

        py.draw.rect(WINDOW, NONSELECT, DroppedRelInfoX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, DroppedRelInfoX, 2, border_radius=6)

    if not Dropped:
        SideBar()
        py.draw.rect(WINDOW, SELECT, DropButtonX)
        py.draw.rect(WINDOW, BLACK, DropButtonX, 2)
        py.gfxdraw.aapolygon(WINDOW, ArrowOpenX, BLACK)
        py.gfxdraw.filled_polygon(WINDOW, ArrowOpenX, BLACK)

        Symbols = ['C', 'H', 'O', 'N', 'F', 'Cl', 'Br', 'I']
        Font = py.font.SysFont('comicsansms', 40)

        for y in range(1, 5):
            for x in range(1, 3):
                Square_pos = py.Rect(657 + (x - 1) * 70, 105 + (y - 1) * 65, 56, 56)
                py.draw.rect(WINDOW, BUTTON, Square_pos, border_radius=6)
                py.draw.rect(WINDOW, BLACK, Square_pos, 2, 6)

                # Orients the text of the elements to the boxes
                Element = Font.render(Symbols[2 * y + x - 3], True, SELTEXT)
                Element_pos = Element.get_rect(center=Square_pos.center)
                WINDOW.blit(Element, Element_pos)

        py.draw.rect(WINDOW, NONSELECT, DisplayNameX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, DisplayNameX, 2, border_radius=6)

        py.draw.rect(WINDOW, NONSELECT, RelInfoX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, RelInfoX, 2, border_radius=6)


def DrawFinalName(FinalName):
    Font = py.font.SysFont('comicsansms', 50)
    if not Dropped:
        print("Good Job")

def DrawRepos():
    if len(PosUsed) > 0:
        if not Dropped:
            py.draw.rect(WINDOW, SELECT, ReposX, border_radius=6)
            py.draw.rect(WINDOW, BLACK, ReposX, 2, border_radius=6)
            redo = py.image.load('ReturnButton.png')
            redoscale = py.transform.scale(redo, (redo.get_rect().width / 47, redo.get_rect().height / 47))
            WINDOW.blit(redoscale, (577, 42))
        if Dropped:
            py.draw.rect(WINDOW, SELECT, DroppedReposX, border_radius=6)
            py.draw.rect(WINDOW, BLACK, DroppedReposX, 2, border_radius=6)
            redo = py.image.load('ReturnButton.png')
            redoscale = py.transform.scale(redo, (redo.get_rect().width / 47, redo.get_rect().height / 47))
            WINDOW.blit(redoscale, (656, 42))


def DrawReset():
    if not Dropped:
        py.draw.rect(WINDOW, SELECT, ResetX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, ResetX, 2, border_radius=6)
        reset = py.image.load('refresh-page-option.png')
        resetscale = py.transform.scale(reset, (reset.get_rect().width / 29, reset.get_rect().height / 29))
        WINDOW.blit(resetscale, (534, 44))
    if Dropped:
        py.draw.rect(WINDOW, SELECT, DroppedResetX, border_radius=6)
        py.draw.rect(WINDOW, BLACK, DroppedResetX, 2, border_radius=6)
        reset = py.image.load('refresh-page-option.png')
        resetscale = py.transform.scale(reset, (reset.get_rect().width / 29, reset.get_rect().height / 29))
        WINDOW.blit(resetscale, (614, 44))

# Button Function Definitions
def DropUpdate():
    global Dropped
    Dropped = not Dropped


def Repos():
    global Bias_x, Bias_y
    Bias_x = IntBias_x
    Bias_y = IntBias_y


def Reset():
    global PosUsed, PosUsedElement, BondUsed, BondStrength, BondAngles, BondArea
    PosUsed = []
    PosUsedElement = []
    BondUsed = []
    BondStrength = []
    BondAngles = []
    BondArea = []


def HomeMenu():
    print("Home menu lol")


# Element Dragging

def ElementStartDrag(type):
    global Element_Drag, ElementType
    ElementType = type
    Element_Drag = True


def ElementPick(Mouse):
    if Area(CArea, Mouse):
        ElementStartDrag(0)

    elif Area(HArea, Mouse):
        ElementStartDrag(1)

    elif Area(OArea, Mouse):
        ElementStartDrag(2)

    elif Area(NArea, Mouse):
        ElementStartDrag(3)

    elif Area(FArea, Mouse):
        ElementStartDrag(4)

    elif Area(ClArea, Mouse):
        ElementStartDrag(5)

    elif Area(BrArea, Mouse):
        ElementStartDrag(6)

    elif Area(IArea, Mouse):
        ElementStartDrag(7)


def ElementRedrag(Mouse):
    # Detects of an element is valid to drag, starts drag if valid
    if len(PosUsed) > 0:
        i = 0
        while i < len(PosUsed):
            PosAdjust = []
            PosAdjust.append(PosUsed[i][0] + Bias_x)
            PosAdjust.append(PosUsed[i][1] + Bias_y)
            PosAdjust.append(50)
            PosAdjust.append(30)
            if Area(PosAdjust, Mouse):
                j = 0
                # Detects if an element is bonded to more than 1 other element, doesn't allow dragging if so
                for k in range(len(BondUsed)):
                    if PosUsed[i] in BondUsed[k]:
                        j = j + 1
                if j < 2:
                    BondRemove(PosUsed[i])
                    ElementStartDrag(PosUsedElement[i])
                    PosUsedElement.pop(i)
                    PosUsed.pop(i)

                i = i + len(PosUsed)

            i = i + 1

def ElementDrop():
    DroppedArea = []
    offset_x = int(offnum(Bias_x, 80))
    offset_y = int(offnum(Bias_y, 50))
    for y in range(- offset_y, 11 - offset_y):
        for x in range(- offset_x, 11 - offset_x):
            DropArea = [15 + x * 80 + Bias_x, 10 + y * 50 + Bias_y, 50, 30]
            Element_Pos = py.mouse.get_pos()
            if Area(DropArea, Element_Pos):
                DroppedArea = [DropArea[0] - Bias_x, DropArea[1] - Bias_y + 10, 50, 30]
                return DroppedArea
    return DroppedArea

def ElementDraw():
    Names = ['C', 'H', 'O', 'N', 'F', 'Cl', 'Br', 'I']
    Font = py.font.SysFont('comicsansms', 40)
    for i in range(len(PosUsed)):
        Element = Font.render(Names[PosUsedElement[i]], True, SELTEXT)
        GridRect = py.Rect(PosUsed[i])
        Element_pos = Element.get_rect(center=GridRect.center)
        WINDOW.blit(Element, (Element_pos[0] + Bias_x, Element_pos[1] + Bias_y - 10))

def ElementAdjacent(DroppedArea):
    if len(PosUsed) == 0:
        return True

    for i in range(len(PosUsed)):
        if PosUsed[i][0] - 80 <= DroppedArea[0] <= PosUsed[i][0] + 80 and \
                PosUsed[i][1] - 50 <= DroppedArea[1] <= PosUsed[i][1] + 50:
            return True


# Bond drawing and storing
def ValidAngle(x, y, adjust):
    BondedAngle = ['invalid', 0]
    if (x % 2) != 0:
        BondArea1 = [x * 40 - 25, y * 25 - 30, 50, 30]
        BondArea2 = [x * 40 - 25, y * 25 + 20, 50, 30]
        if BondArea1 in PosUsed and BondArea2 in PosUsed:
            BondedAngle = [[BondArea1, BondArea2], 90]
            return BondedAngle
    elif (y % 2) != 0:
        BondArea1 = [x * 40 - 65, y * 25 - 5, 50, 30]
        BondArea2 = [x * 40 + 15, y * 25 - 5, 50, 30]
        if BondArea1 in PosUsed and BondArea2 in PosUsed:
            BondedAngle = [[BondArea1, BondArea2], 0]
            return BondedAngle

    BondArea1 = [x * 40 - 65, y * 25 - 30, 50, 30]
    BondArea2 = [x * 40 + 15, y * 25 + 20, 50, 30]
    if BondArea1 in PosUsed and BondArea2 in PosUsed:
        BondedAngle = [[BondArea1, BondArea2], 135]

    BondArea3 = [x * 40 - 65, y * 25 + 20, 50, 30]
    BondArea4 = [x * 40 + 15, y * 25 - 30, 50, 30]
    if BondArea3 in PosUsed and BondArea4 in PosUsed:
        BondedAngle = [[BondArea3, BondArea4], 45]

    # Adjust describes which orientation of the element
    if BondArea1 in PosUsed and BondArea2 in PosUsed and BondArea3 in PosUsed and BondArea4 in PosUsed:
        # Cross is if there's a square of 4 elements with a bond in the middle, meaning two possible bond orientations
        if adjust:
            BondedAngle = [[BondArea3, BondArea4], 'cross']
        else:
            BondedAngle = [[BondArea1, BondArea2], 'cross']

    return BondedAngle

def BondSelect(x, y, BondAngle, BondedArea):
    BondPlace = [x * 40 - 10, y * 25 - 10, 20, 20]
    if BondAngle[1] != 'cross':
        if BondPlace not in BondArea:
            # BondAngle = [[First element pos, second element pos], angle]
            # BondedArea = [BondAngle, strength, already existing?, bond location]
            BondedArea = [BondAngle, 1, False, BondPlace]
            return BondedArea
        else:
            indexer = BondUsed.index(BondAngle[0])
            BondStrength[indexer] += 1
            if BondStrength[indexer] == 4:
                BondUsed.pop(indexer)
                BondAngles.pop(indexer)
                BondStrength.pop(indexer)
                BondArea.pop(indexer)
                return BondedArea
            else:
                BondedArea = [BondAngle, BondStrength[indexer], True, BondPlace]
                return BondedArea

    else:
        # Checks if a 'cross' bond has already been created
        if BondPlace not in BondArea:
            BondArea1 = [x * 40 - 65, y * 25 - 30, 50, 30]
            BondArea2 = [x * 40 + 15, y * 25 + 20, 50, 30]
            BondedArea = [[[BondArea1, BondArea2], 135], 1, False, BondPlace]
            return BondedArea
        else:
            if BondAngle[0] not in BondUsed:
                BondAngle = ValidAngle(x, y, False)
            indexer = BondUsed.index(BondAngle[0])

            if BondStrength[indexer] < 3 and BondAngles[indexer] == 45:
                BondStrength[indexer] += 3

            BondStrength[indexer] += 1

            # Updates the state of all the bonds
            if BondStrength[indexer] == 7:
                BondUsed.pop(indexer)
                BondAngles.pop(indexer)
                BondStrength.pop(indexer)
                BondArea.pop(indexer)
                return BondedArea
            elif BondStrength[indexer] > 3:
                BondArea3 = [x * 40 - 65, y * 25 + 20, 50, 30]
                BondArea4 = [x * 40 + 15, y * 25 - 30, 50, 30]
                BondUsed[indexer] = [BondArea3, BondArea4]
                BondAngles[indexer] = 45
                return BondedArea
            else:
                BondArea1 = [x * 40 - 65, y * 25 - 30, 50, 30]
                BondArea2 = [x * 40 + 15, y * 25 + 20, 50, 30]
                BondedArea = [[[BondArea1, BondArea2], 135], BondStrength[indexer], True, BondPlace]
                return BondedArea


def BondSelectGuard():
    BondedArea = []
    BondPos = py.mouse.get_pos()
    offset_x = int(offnum(Bias_x, 40))
    offset_y = int(offnum(Bias_y, 25))
    for y in range(- offset_y, 19 - offset_y):
        for x in range(- offset_x, 23 - offset_x):
            BondPlace = [x * 40 + Bias_x - 10, y * 25 + Bias_y - 10, 20, 20]
            if not Area(BondPlace, BondPos):
                continue
            BondAngle = ValidAngle(x, y, True)
            if BondAngle[0] == 'invalid':
                continue
            BondedArea = BondSelect(x, y, BondAngle, BondedArea)
            return BondedArea
    return BondedArea

def BondDrawX(i, strength, size):
    Level = ['–', '=', '≡']
    Font = py.font.SysFont('arial', size)
    Bond = Font.render(Level[strength - 1], True, SELTEXT)
    Bond = py.transform.rotate(Bond, BondAngles[i])
    GridRect = py.Rect(BondArea[i])
    Bond_pos = Bond.get_rect(center=GridRect.center)
    if BondAngles[i] == 0:
        WINDOW.blit(Bond, (Bond_pos[0] + Bias_x, Bond_pos[1] + Bias_y - 2 * (1 - offnum(strength, 1.5))))
    elif BondAngles[i] == 45:
        WINDOW.blit(Bond, (Bond_pos[0] + Bias_x, Bond_pos[1] + Bias_y - 2))
    elif BondAngles[i] == 90:
        WINDOW.blit(Bond, (Bond_pos[0] + Bias_x - 2 * (1 - offnum(strength, 1.5)), Bond_pos[1] + Bias_y + 2))
    elif BondAngles[i] == 135:
        WINDOW.blit(Bond, (Bond_pos[0] + Bias_x, Bond_pos[1] + Bias_y))

def BondDraw():
    for i in range(len(BondUsed)):
        Strength = BondStrength[i]
        if Strength > 3:
            Strength = Strength - 3
        if Strength == 1:
            BondDrawX(i, 1, 37)
        elif Strength == 2:
            BondDrawX(i, 2, 40)
        elif Strength == 3:
            BondDrawX(i, 3, 40)

def BondRemove(BondoRemovo):
    if len(BondUsed) > 0:
        i = 0
        while i < len(BondUsed):
            if BondoRemovo in BondUsed[i]:
                BondUsed.remove(BondUsed[i])
                BondAngles.pop(i)
                BondStrength.pop(i)
                BondArea.pop(i)

            i = i + 1


# Window Details
FPS = 60
WINWIDTH = 800
WINHEIGHT = 450
fpsClock = py.time.Clock()
WINDOW = py.display.set_mode((WINWIDTH, WINHEIGHT))
py.display.set_caption('Organic Compound Namer')


# Mainline
def Main():
    py.init()
    looping = True
    global Grid_Drag, Element_Drag, Grid_pos_x, Grid_pos_y, Bias_x, Bias_y, IntBias_x, IntBias_y, PosUsed, \
        PosUsedElement, BondUsed, BondArea, BondStrength, BondAngles

    # Loading files
    Load = Load_Save(
        PosUsed=PosUsed,
        PosUsedElement=PosUsedElement,
        BondUsed=BondUsed,
        BondArea=BondArea,
        BondStrength=BondStrength,
        BondAngles=BondAngles
    )

    MoleculeInfo = Load.Recall()
    if len(MoleculeInfo) > 0:
        PosUsed = MoleculeInfo[0]
        PosUsedElement = MoleculeInfo[1]
        BondUsed = MoleculeInfo[2]
        BondArea = MoleculeInfo[3]
        BondStrength = MoleculeInfo[4]
        BondAngles = MoleculeInfo[5]


    # MAINLOOP
    while looping:

        Save = Load_Save(
            PosUsed=PosUsed,
            PosUsedElement=PosUsedElement,
            BondUsed=BondUsed,
            BondArea=BondArea,
            BondStrength=BondStrength,
            BondAngles=BondAngles
        )

        NamerLogic = Namer(
            PosUsed=PosUsed,
            PosUsedElement=PosUsedElement,
            BondUsed=BondUsed,
            BondArea=BondArea,
            BondStrength=BondStrength,
            BondAngles=BondAngles,
            Element_Drag=Element_Drag
        )

        # General GUI Buttons
        DropButton = Button(
            position=(640, 0),
            size=(44, 22),
            on_click_function=DropUpdate
        )

        DroppedButton = Button(
            position=(756, 0),
            size=(44, 22),
            on_click_function=DropUpdate
        )

        HomeButton = Button(
            position=(33, 20),
            size=(65, 65),
            on_click_function=HomeMenu
        )

        ResetButton = Button(
            position=(530, 40),
            size=(25, 25),
            on_click_function=Reset
        )

        DroppedResetButton = Button(
            position=(610, 40),
            size=(25, 25),
            on_click_function=Reset
        )

        ReposButton = Button(
            position=(575, 40),
            size=(25, 25),
            on_click_function=Repos
        )

        DroppedReposButton = Button(
            position=(655, 40),
            size=(25, 25),
            on_click_function=Repos
        )

        Mouse = py.mouse.get_pos()
        MouseMot = py.mouse.get_rel()

        # Render elements of the game
        WINDOW.fill(BACKGROUND)

        DrawGrid()

        ElementDraw()

        BondDraw()

        DropDown()

        HomeButton.update()

        DrawRepos()
        if Dropped:
            DroppedButton.update()
            DroppedReposButton.update()
            if len(PosUsed) > 0:
                DrawReset()
                DroppedResetButton.update()

        if not Dropped:
            DropButton.update()
            ReposButton.update()
            if len(PosUsed) > 0:
                DrawReset()
                ResetButton.update()

        # Click events that can't be described by the Button Class

        for event in py.event.get():
            if event.type == QUIT:
                py.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    BondInfo = BondSelectGuard()
                    if Dropped:
                        if not Area(DroppedDisplayNameX, Mouse) and not Area(DroppedRelInfoX, Mouse) \
                                and not Area(HomeButtonX, Mouse):
                            MouseDown(Mouse, BondInfo)
                            FinalName = NamerLogic.Update()
                            Save.Encode()
                    else:
                        if not Area(SideBarX, Mouse) and not Area(DisplayNameX, Mouse) \
                                and not Area(RelInfoX, Mouse) and not Area(HomeButtonX, Mouse):
                            MouseDown(Mouse, BondInfo)
                            FinalName = NamerLogic.Update()
                            Save.Encode()
                        ElementPick(Mouse)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    Grid_Drag = False
                    DroppedArea = ElementDrop()
                    if Element_Drag and len(DroppedArea) > 0:
                        if ElementAdjacent(DroppedArea) and DroppedArea not in PosUsed:
                            PosUsed.append(DroppedArea)
                            PosUsedElement.append(ElementType)
                            FinalName = NamerLogic.Update()
                            Save.Encode()
                            if len(PosUsed) == 1:
                                IntBias_x = Bias_x
                                IntBias_y = Bias_y

                    Element_Drag = False

            elif event.type == MOUSEMOTION:
                if Grid_Drag:
                    if Bias_x == 0 and Bias_y == 0:
                        Bias_x = Mouse[0] + Grid_pos_x
                        Bias_y = Mouse[1] + Grid_pos_y
                    else:
                        Bias_x = MouseMot[0] + Bias_x
                        Bias_y = MouseMot[1] + Bias_y

        if Element_Drag:
            Symbols = ['C', 'H', 'O', 'N', 'F', 'Cl', 'Br', 'I']
            Font = py.font.SysFont('comicsansms', 40)
            Element = Font.render(Symbols[ElementType], True, SELTEXT)
            WINDOW.blit(Element, (Mouse[0] - 13, Mouse[1] - 21))

        py.display.update()
        fpsClock.tick(FPS)


# Main Loop
Main()
