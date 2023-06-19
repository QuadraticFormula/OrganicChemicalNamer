import ast

class Load_Save:
    def __init__(
            self,
            PosUsed: list,
            PosUsedElement: list,
            BondUsed: list,
            BondArea: list,
            BondStrength: list,
            BondAngles: list,
    ):

        # Setting up all necessary information
        self.PosUsed = PosUsed
        self.PosUsedElement = PosUsedElement
        self.BondUsed = BondUsed
        self.BondArea = BondArea
        self.BondStrength = BondStrength
        self.BondAngles = BondAngles

    def Encode(self):
        # RefactorPos_x and RefactorPos_y are lists containing every x/y value of all the elements
        RefactorPos = []
        RefactorPos_x = []
        RefactorPos_y = []

        RefactorBond = []

        for i in range(len(self.PosUsed)):
            # Multiplying by 2 allows for the room for the bonds in RefactorPos.txt
            NewPos_x = int((self.PosUsed[i][0] - 15) / 40)
            NewPos_y = int((self.PosUsed[i][1] - 20) / 25)
            RefactorPos_x.append(NewPos_x)
            RefactorPos_y.append(NewPos_y)
            RefactorPos.append([NewPos_x, NewPos_y])

        for i in range(len(self.BondUsed)):
            # self.BondUsed[bond][element in bond][x or y]
            NewBond_x1 = int((self.BondUsed[i][0][0] - 15) / 40)
            NewBond_y1 = int((self.BondUsed[i][0][1] - 20) / 25)
            NewBond_x2 = int((self.BondUsed[i][1][0] - 15) / 40)
            NewBond_y2 = int((self.BondUsed[i][1][1] - 20) / 25)
            NewBond_x = 0.5 * (NewBond_x1 + NewBond_x2)
            NewBond_y = 0.5 * (NewBond_y1 + NewBond_y2)

            RefactorBond.append([NewBond_x, NewBond_y])

        MoleculeFile = open("RefactorGrid.txt", "w", encoding='utf-8')
        if len(RefactorPos) > 0:
            for y in range(sorted(RefactorPos_y)[0], sorted(RefactorPos_y)[-1] + 1):
                for x in range(sorted(RefactorPos_x)[0], sorted(RefactorPos_x)[-1] + 1):
                    if [x, y] in RefactorPos:
                        element = RefactorPos.index([x, y])
                        SymbolName = ['C', 'H', 'O', 'N', 'F', 'Cl', 'Br', 'I']
                        Symbol = SymbolName[self.PosUsedElement[element]]
                        MoleculeFile.write(Symbol)
                    elif [x, y] in RefactorBond:
                        BondStrength = RefactorBond.index([x, y])
                        Strength = f'{self.BondStrength[BondStrength]}'
                        MoleculeFile.write(Strength)
                    else:
                        Blank = "∅"
                        MoleculeFile.write(Blank)
                MoleculeFile.write("\n")
        MoleculeFile.write("\n")
        MoleculeFile.write(f'Pos Used:\n{self.PosUsed}\n')
        MoleculeFile.write(f'Elements:\n{self.PosUsedElement}\n')
        MoleculeFile.write(f'Bond Used:\n{self.BondUsed}\n')
        MoleculeFile.write(f'Bond Area:\n{self.BondArea}\n')
        MoleculeFile.write(f'Bond Strength:\n{self.BondStrength}\n')
        MoleculeFile.write(f'Bond Angles:\n{self.BondAngles}\n')
        MoleculeFile.close()

    def Recall(self):
        MoleculeFile = open("RefactorGrid.txt", 'r', encoding='utf-8')
        MoleculeInfo = []
        for pos in MoleculeFile:
            if pos[0] == '[':
                Info = pos
                Info = ast.literal_eval(Info)
                MoleculeInfo.append(Info)

        return MoleculeInfo
