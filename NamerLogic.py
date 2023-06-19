import pygame as py

py.init()


class Namer:
    def __init__(
            self,
            PosUsed: list,
            PosUsedElement: list,
            BondUsed: list,
            BondArea: list,
            BondStrength: list,
            BondAngles: list,
            Element_Drag: bool
    ):

        # Setting up all necessary information
        self.PosUsed = PosUsed
        self.PosUsedElement = PosUsedElement
        self.BondUsed = BondUsed
        self.BondArea = BondArea
        self.BondStrength = BondStrength
        self.BondAngles = BondAngles
        self.Element_Drag = Element_Drag

    # ---ROUTING---
    # Calculate the length of carbon chains
    def StartingPos(self, CarbonBond, element, Counted, Uncounted):
        for bond in CarbonBond:
            if element in bond:
                if bond[0] in Counted and bond[1] in Uncounted:
                    starting = bond[0]
                    return starting
                elif bond[1] in Counted and bond[0] in Uncounted:
                    starting = bond[1]
                    return starting
                else:
                    continue

    def CarbonChains(self):
        ChainLengths = []
        ChainPos = []

        # bridges refers to the number of points where a carbon chain splits into 2 or more
        BridgeChainLengths = []
        BridgeChainPos = []

        # Describes the lengths of all non-bridge chains that are bonded to a bridge
        AssocLengths = []

        Counted = []
        Uncounted = []

        # Transferring element and bond information into carbon specific arrays
        CarbonUsed = []
        CarbonFrequency = []
        TotalFrequency = []
        CarbonBond = []
        index = 0

        ChainInfo = [ChainLengths, ChainPos, CarbonUsed, CarbonFrequency, BridgeChainLengths, BridgeChainPos,
                     CarbonBond]

        for element in self.PosUsedElement:
            if element == 0:
                CarbonUsed.append(self.PosUsed[index])
                CarbonFrequency.append(0)
            TotalFrequency.append(0)
            index += 1

        for bond in self.BondUsed:
            element_1 = bond[0]
            element_2 = bond[1]
            if element_1 in CarbonUsed and element_2 in CarbonUsed:
                CarbonBond.append(bond)

        for bond in CarbonBond:
            for element in CarbonUsed:
                if element in bond:
                    CarbonFrequency[CarbonUsed.index(element)] += 1

        for bond in self.BondUsed:
            for element in self.PosUsed:
                if element in bond:
                    TotalFrequency[self.PosUsed.index(element)] += 1

        if (0 in CarbonFrequency and len(CarbonUsed) > 1) or len(self.PosUsed) == 0 or 0 in TotalFrequency:
            ChainInfo = 'invalid'
            return ChainInfo

        for frequency in CarbonFrequency:
            if frequency > 4:
                ChainInfo = 'invalid'
                return ChainInfo

        # Single carbon has length = 0 since the length is updated to increase by 1 regardless
        if len(CarbonUsed) == 1:
            ChainLengths.append(0)
            ChainPos.append(CarbonUsed[0])
            ChainInfo = [ChainLengths, ChainPos, CarbonUsed, CarbonFrequency, BridgeChainLengths, BridgeChainPos,
                         CarbonBond]
            return ChainInfo

        # Counts all chains that start Frequency = 1 and end in either Frequency = 1 or > 2
        for element in CarbonUsed:
            if element in Counted:
                continue

            elif CarbonFrequency[CarbonUsed.index(element)] == 1:
                length = 0
                looping = True
                ChainPosTemp = []
                while looping:
                    for bond in CarbonBond:
                        if element not in bond or not looping:
                            continue

                        Counted.append(element)
                        length += 1
                        ChainPosTemp.append(element)
                        # bond[bond.index(element) - 1 either changes 1 to 0, or 0 to -1, which changes the
                        # element to the other in the bond
                        checked = bond[bond.index(element) - 1]
                        index = CarbonUsed.index(checked)
                        element = CarbonUsed[index]

                        if CarbonFrequency[index] == 2:
                            continue
                        # Counted prevents the other end of a carbon chain from being Counted
                        ChainLengths.append(length)
                        ChainPos.append(ChainPosTemp)
                        ChainPosTemp.append(element)
                        if element not in Counted:
                            Counted.append(element)
                        looping = False

        # Counts all chains connecting carbons which both contain frequency > 2
        if len(Counted) < len(CarbonUsed):
            for element in CarbonUsed:
                if element not in Counted:
                    Uncounted.append(element)

            # The use of UncountedLoop allows to check every value in Uncounted while the length of the list changes
            UncountedLoop = []
            UncountedLoop += Uncounted
            for element in UncountedLoop:
                length = 0
                starting = self.StartingPos(CarbonBond, element, Counted, UncountedLoop)
                looping = True
                if element in Counted:
                    continue
                while looping:
                    BridgeChainPosTemp = [starting]
                    for bond in CarbonBond:
                        if (element not in bond) or (starting in bond) or not looping:
                            continue
                        length += 1
                        BridgeChainPosTemp.append(element)
                        Counted.append(element)
                        Uncounted.remove(element)
                        starting = element
                        element = bond[bond.index(element) - 1]

                        if CarbonFrequency[CarbonUsed.index(element)] < 3:
                            continue
                        looping = False
                        BridgeChainPosTemp.append(element)
                        BridgeChainLengths.append(length)
                        BridgeChainPos.append(BridgeChainPosTemp)
        return ChainInfo

    def LongestPath(self):
        PathLength = 0
        AssocLengths = []
        ChainInfo = self.CarbonChains()
        if ChainInfo == 'invalid':
            return 'invalid'

        # suffix: -Used refers to individual carbon position, -Pos refers to a list of carbons in a chain
        ChainLengths = ChainInfo[0]
        ChainPos = ChainInfo[1]
        CarbonUsed = ChainInfo[2]
        CarbonFrequency = ChainInfo[3]
        BridgeChainLengths = ChainInfo[4]
        BridgeChainPos = ChainInfo[5]
        CarbonBond = ChainInfo[6]
        BridgeUsed = []
        # Creates a list of all bridge's positions (Carbonfrequency > 3) and splits them into inner and outer (In the
        # middle of the chain vs on the edge of the chain)
        for chain in ChainPos:
            if chain[1] in BridgeUsed:
                continue
            stub = []
            for length in range(len(ChainLengths)):
                if ChainPos[length][1] == chain[1]:
                    stub.append(ChainLengths[length])
            BridgeUsed.append(chain[1])
            AssocLengths.append(stub)

        Bridges = 0
        BridgeUsed = []
        for frequency in range(len(CarbonFrequency)):
            if CarbonFrequency[frequency] >= 3:
                Bridges += 1
                BridgeUsed.append(CarbonUsed[frequency])

        for bond in CarbonBond:
            if bond[0] in BridgeUsed and bond[1] in BridgeUsed:
                BridgeChainPos.append(bond)
                BridgeChainLengths.append(0)

        # Identifies all bridges in the middle and ends of chains and appends them to a list
        # InnerBridgeUsed and OuterBridgeUsed describes the position of element

        OuterBridgeUsed = []
        InnerBridgeUsed = []
        checked = []
        for chain in BridgeChainPos:
            checked += chain
        for item in BridgeUsed:
            chains = 0
            for BridgeUsed in checked:
                if BridgeUsed == item:
                    chains += 1
            if chains == 1:
                OuterBridgeUsed.append(item)
            else:
                InnerBridgeUsed.append(item)

        if len(OuterBridgeUsed) > 2:
            return 'invalid'

        PathPosList = []
        PathChainList = []
        # PathLength = [length, path, ChainPos, CarbonBond, PathChainList, CarbonUsed]
        if Bridges == 0:
            PathLength = [ChainLengths[0] + 1, ChainPos[0], ChainPos, CarbonBond, ChainPos, CarbonUsed]
            return PathLength

        elif Bridges == 1:
            Longest_1 = sorted(ChainLengths, reverse=True)[0]
            Longest_2 = sorted(ChainLengths, reverse=True)[1]
            PathLength = Longest_1 + Longest_2 + 1
            PathPosList += ChainPos[ChainLengths.index(Longest_1)]
            PathChainList.append(ChainPos[ChainLengths.index(Longest_1)])
            if Longest_1 == Longest_2:
                for length in range(len(ChainLengths)):
                    if (ChainLengths[length] == Longest_1) and (ChainPos[length] != PathPosList):
                        added = []
                        added += ChainPos[length]
                        added.pop(-1)
                        PathPosList += reversed(added)
                        PathChainList.append(ChainPos[length])
                        PathLength = [PathLength, PathPosList, ChainPos, CarbonBond, PathChainList, CarbonUsed]
                        return PathLength
            else:
                added = []
                added += ChainPos[ChainLengths.index(Longest_2)]
                added.pop(-1)
                PathPosList += reversed(added)
                PathChainList.append(ChainPos[ChainLengths.index(Longest_2)])
                PathLength = [PathLength, PathPosList, ChainPos, CarbonBond, PathChainList, CarbonUsed]
                return PathLength

        elif Bridges >= 2:
            # Longest valid chain = sum of all bridged paths + the longest attached alkyl groups on the ends
            Index = []
            PathChainList = []
            for chain in ChainPos:
                if OuterBridgeUsed[0] in chain:
                    Index.append(ChainPos.index(chain))
            PathLength += ChainLengths[sorted(Index)[-1]]
            PathPosList += ChainPos[sorted(Index)[-1]]
            PathChainList.append(ChainPos[sorted(Index)[-1]])

            # Middle of the chain
            for chain in BridgeChainLengths:
                PathLength += chain
            PathLength += len(BridgeChainPos) + 1
            counter = 0
            looping = True
            while looping:
                for chain in BridgeChainPos:
                    if PathPosList[-1] not in chain or not looping:
                        continue
                    if chain[0] == PathPosList[-1]:
                        counter += 1
                        added = []
                        added += chain
                        PathChainList.append(chain)
                        added.pop(0)
                        PathPosList += added
                        if len(InnerBridgeUsed) == 0:
                            looping = False

                    elif chain[-1] == PathPosList[-1]:
                        counter += 1
                        added = []
                        added += chain
                        added.reverse()
                        PathChainList.append(chain)
                        added.pop(0)
                        PathPosList += added
                        if len(InnerBridgeUsed) == 0:
                            looping = False

                    if (chain[0] in OuterBridgeUsed or chain[-1] in OuterBridgeUsed) and counter > 1:
                        looping = False

            # End of the chain
            Index = []
            for chain in ChainPos:
                if OuterBridgeUsed[1] in chain:
                    Index.append(ChainPos.index(chain))
            PathLength += ChainLengths[sorted(Index)[-1]]
            added = []
            added += ChainPos[sorted(Index)[-1]]
            added.reverse()
            PathChainList.append(ChainPos[sorted(Index)[-1]])
            added.pop(0)
            PathPosList += added

            PathLength = [PathLength, PathPosList, ChainPos, CarbonBond, PathChainList, CarbonUsed]
            return PathLength

    # ---NAMING---
    # ---General calculations---
    def ChainUpdate(self, path, CarbonBond):
        # Changes the order of items in CarbonBond to be aligned with the longest path
        ChainBond = []
        for item in range(len(path)):
            if len(ChainBond) == len(path) - 1:
                continue

            for bond in CarbonBond:
                if path[item] in bond and path[item + 1] in bond:
                    ChainBond.append(bond)

        # Updates the order of carbon-specific bonds with the change of order from CarbonBond to ChainBond
        ChainStrength = []
        for bond in ChainBond:
            ChainStrength.append(self.BondStrength[self.BondUsed.index(bond)])

        return ChainStrength

    def StrengthUpdate(self, ChainStrength):
        # Stores the indexes of all BondStrength > 1
        PosEn = []
        PosYn = []
        for Index in range(len(ChainStrength)):
            if ChainStrength[Index] == 2:
                PosEn.append(Index + 1)
            elif ChainStrength[Index] == 3:
                PosYn.append(Index + 1)
        PosEn.sort()
        PosYn.sort()
        return [PosEn, PosYn]

    def HalogenUpdate(self, path):
        # Defines location and value of all halogens
        HalogenListTemp = []
        HalogenIndexTemp = []
        for element in range(len(self.PosUsedElement)):
            if self.PosUsedElement[element] < 4:
                continue
            HalogenListTemp.append(self.PosUsedElement[element])
            for bond in self.BondUsed:

                if self.PosUsed[element] not in bond:
                    continue
                checked = bond[bond.index(self.PosUsed[element]) - 1]

                if checked not in path:
                    return 'invalid'

                HalogenIndexTemp.append(path.index(checked))
                break
        return [HalogenIndexTemp, HalogenListTemp]

    def HalogenReupdate(self, HalogenListTemp, HalogenIndexTemp):
        HalogenIndex = [[], [], [], []]
        Bromo = []
        Chloro = []
        Fluoro = []
        Iodo = []
        for Halogen in range(len(HalogenListTemp)):
            if HalogenListTemp[Halogen] == 4:
                Fluoro.append(HalogenIndexTemp[Halogen] + 1)
            elif HalogenListTemp[Halogen] == 5:
                Chloro.append(HalogenIndexTemp[Halogen] + 1)
            elif HalogenListTemp[Halogen] == 6:
                Bromo.append(HalogenIndexTemp[Halogen] + 1)
            elif HalogenListTemp[Halogen] == 7:
                Iodo.append(HalogenIndexTemp[Halogen] + 1)
        Chloro.sort()
        Fluoro.sort()
        Bromo.sort()
        Iodo.sort()

        # Halogens have been reorganised in alphabetical order
        HalogenIndex[0] = Bromo
        HalogenIndex[1] = Chloro
        HalogenIndex[2] = Fluoro
        HalogenIndex[3] = Iodo
        return HalogenIndex

    def AlkylUpdate(self, path, PathChainList, ChainPos):
        AlkylIndex = []
        AlkylLength = []
        if ChainPos == 0 or len(PathChainList) == len(ChainPos):
            return [AlkylIndex, AlkylLength]

        for chain in ChainPos:
            if chain in PathChainList:
                continue
            AlkylIndex.append(path.index(chain[-1]) + 1)
            AlkylLength.append(len(chain) - 1)

        return [AlkylIndex, AlkylLength]

    def AlkylReUpdate(self, AlkylIndex, AlkylLength):
        TempAlkylLength = []
        for length in AlkylLength:
            if length in TempAlkylLength:
                continue
            TempAlkylLength.append(length)
        TempAlkylLength.sort()

        TempAlkylIndex = []
        for length in TempAlkylLength:
            temp = []
            for index in range(len(AlkylIndex)):
                if AlkylLength[index] != length:
                    continue
                temp.append(AlkylIndex[index])
            temp.sort()
            TempAlkylIndex.append(temp)

        AlkylIndex = TempAlkylIndex
        AlkylLength = TempAlkylLength
        return [AlkylIndex, AlkylLength]

    def NitrogenGuard(self, path):
        NitrogenUsed = []
        index = 0
        for element in self.PosUsedElement:
            if element == 3:
                NitrogenUsed.append(self.PosUsed[index])
            index += 1

        NitrogenIndex = []
        NitrogenStrength = []
        for nitrogen in NitrogenUsed:
            for bond in self.BondUsed:
                if nitrogen not in bond:
                    continue
                # Checks if the nitrogen is bonded to an element besides carbon or hydrogen
                elif self.PosUsedElement[self.PosUsed.index(bond[bond.index(nitrogen) - 1])] != 0 and \
                        self.PosUsedElement[self.PosUsed.index(bond[bond.index(nitrogen) - 1])] != 1:
                    return 'invalid'
                # Checks if any bonds containing nitrogen have a strength not equal to 1 or 3
                elif self.BondStrength[self.BondUsed.index(bond)] != 1 and \
                        self.BondStrength[self.BondUsed.index(bond)] != 3:
                    return 'invalid'
                # Checks if bond between a nitrogen and hydrogen has a strength of 1
                elif self.PosUsedElement[self.PosUsed.index(bond[bond.index(nitrogen) - 1])] == 1 and \
                        self.BondStrength[self.BondUsed.index(bond)] != 1:
                    return 'invalid'
                # Checks if a carbon bonded to a nitrogen is in the path
                elif self.PosUsedElement[self.PosUsed.index(bond[bond.index(nitrogen) - 1])] == 0 and \
                        bond[bond.index(nitrogen) - 1] not in path:
                    return 'invalid'
                # Checks if the carbon is at the ends of the path, only Nitrogen-Carbon bonds pass through
                elif path[0] != bond[bond.index(nitrogen) - 1] and path[-1] != bond[bond.index(nitrogen) - 1]:
                    continue

                # Checking for NH2
                if self.BondStrength[self.BondUsed.index(bond)] == 1:
                    count = 0
                    for value in self.BondUsed:

                        # Checks if the nitrogen has multiple bonds (NH2)
                        if nitrogen not in value or self.BondUsed.index(bond) == self.BondUsed.index(value):
                            continue

                        # If a nitrogen has multiple bonds, it cannot be a nitrile
                        elif self.BondStrength[self.BondUsed.index(value)] == 3:
                            return 'invalid'

                        elif self.BondStrength[self.BondUsed.index(bond)] == 3:
                            return 'invalid'

                        elif self.PosUsedElement[self.PosUsed.index(value[value.index(nitrogen) - 1])] == 1:
                            count += 1

                    if count != 2:
                        return 'invalid'
                    NitrogenIndex.append(path.index(bond[bond.index(nitrogen) - 1]) + 1)
                    NitrogenStrength.append(1)

                # Checking for C(3)N
                elif self.BondStrength[self.BondUsed.index(bond)] == 3:
                    NitrogenIndex.append(path.index(bond[bond.index(nitrogen) - 1]) + 1)
                    NitrogenStrength.append(3)
        return [NitrogenIndex, NitrogenStrength, NitrogenUsed]

    def OxygenGuard(self, path):
        OxygenUsed = []
        index = 0
        for element in self.PosUsedElement:
            if element == 2:
                OxygenUsed.append(self.PosUsed[index])
            index += 1

        OxygenBonds = []
        OxygenStrength = []
        for oxygen in OxygenUsed:
            tempbond = []
            tempstrength = []
            for bond in self.BondUsed:
                if oxygen not in bond:
                    continue
                if self.BondStrength[self.BondUsed.index(bond)] > 2:
                    return 'invalid'
                elif self.PosUsedElement[self.PosUsed.index(bond[bond.index(oxygen) - 1])] != 0 and \
                        self.PosUsedElement[self.PosUsed.index(bond[bond.index(oxygen) - 1])] != 1:
                    return 'invalid'
                elif self.PosUsedElement[self.PosUsed.index(bond[bond.index(oxygen) - 1])] == 1 and \
                        self.BondStrength[self.BondUsed.index(bond)] > 1:
                    return 'invalid'
                added = []
                for item in bond:
                    added.append(item)
                tempstrength.append(self.BondStrength[self.BondUsed.index(added)])
                tempbond.append(added)
            if len(tempbond) > 3:
                return 'invalid'

            # Always putting the oxygen in the bond at index = 1, carbon/hydrogen at index = 0
            # When an Oxygen is bonded to a carbon and hydrogen, carbon comes first
            for bond in tempbond:
                for element in bond:
                    if self.PosUsedElement[self.PosUsed.index(element)] == 2:
                        continue
                    elif bond.index(element) == 0 or bond.index(element) == 1:
                        tempbond[tempbond.index(bond)].reverse()

            if tempbond[0][0] not in path:
                tempbond.reverse()

            # tempbond = [[carbon position, oxygen position], [hydrogen/carbon position, oxygen position]]
            OxygenBonds.append(tempbond)
            OxygenStrength.append(tempstrength)

        for bonds in OxygenBonds:
            if len(bonds) == 1 and 2 not in OxygenStrength[OxygenBonds.index(bonds)]:
                return 'invalid'
            elif len(bonds) == 2 and 2 in OxygenStrength[OxygenBonds.index(bonds)]:
                return 'invalid'

        return [OxygenBonds, OxygenStrength]

    def OxygenNitrogenNonBreak(self, path, HalogenIndexTemp, HalogenListTemp):
        NitrogenInfo = self.NitrogenGuard(path)
        if NitrogenInfo == 'invalid':
            return 'invalid'
        NitrogenIndex = NitrogenInfo[0]
        NitrogenStrength = NitrogenInfo[1]
        NitrogenUsed = NitrogenInfo[2]

        OxygenInfo = self.OxygenGuard(path)
        if OxygenInfo == 'invalid':
            return 'invalid'
        OxygenBonds = OxygenInfo[0]
        OxygenStrength = OxygenInfo[1]

        index = 0
        HydrogenUsed = []
        for element in self.PosUsedElement:
            if element == 1:
                HydrogenUsed.append(self.PosUsed[index])
            index += 1

        HydrogenBonds = []
        for bond in self.BondUsed:
            for hydrogen in HydrogenUsed:
                if hydrogen in bond:
                    HydrogenBonds += bond

        OxyBondTypeTemp = []
        OxyBondIndexTemp = []
        halogens = []
        for carbon in path:
            for item in OxygenBonds:
                for bond in item:
                    if carbon not in bond:
                        continue
                    if carbon != path[0] and carbon != path[-1] and OxygenStrength[OxygenBonds.index(item)][0] == 2:
                        OxyBondTypeTemp.append('ketone')
                        OxyBondIndexTemp.append(path.index(carbon) + 1)

                    elif path.index(carbon) in HalogenIndexTemp and OxygenStrength[OxygenBonds.index(item)][0] == 2:
                        OxyBondTypeTemp.append('acid halide')
                        halogens.append(HalogenListTemp[HalogenIndexTemp.index(path.index(carbon))])
                        OxyBondIndexTemp.append(path.index(carbon) + 1)

                    elif carbon in HydrogenBonds and OxygenStrength[OxygenBonds.index(item)][0] == 2:
                        OxyBondTypeTemp.append('aldehyde')
                        OxyBondIndexTemp.append(path.index(carbon) + 1)

                    if len(NitrogenStrength) > 0 and path.index(carbon) in NitrogenStrength and \
                            len(NitrogenStrength) >= path.index(carbon) + 1:
                        if NitrogenStrength[path.index(carbon)] == 1 and \
                                OxygenStrength[OxygenBonds.index(item)][0] == 2:
                            OxyBondTypeTemp.append('amide')
                            OxyBondIndexTemp.append(path.index(carbon) + 1)

                    count = 0
                    for value in OxygenBonds:
                        if bond[0] != value[0][0] or OxygenBonds.index(item) == OxygenBonds.index(value):
                            continue

                        if len(item) == 2 and len(value) == 1:
                            count += 1
                            OxyBondTypeTemp.append('carboxylic acid')
                            OxyBondIndexTemp.append(path.index(carbon) + 1)
                            break

                    if count == 0:
                        if OxygenStrength[OxygenBonds.index(item)] == [1, 1]:
                            OxyBondTypeTemp.append('alcohol')
                            OxyBondIndexTemp.append(path.index(carbon) + 1)

        temp = 0
        for Type in OxyBondTypeTemp:
            if Type == 'ketone':
                continue
            temp += 1

        if temp > 2:
            return 'invalid'

        for carbon in path:
            for nitrogen in NitrogenUsed:
                if [carbon, nitrogen] in self.BondUsed:
                    Index = path.index(carbon) + 1
                elif [nitrogen, carbon] in self.BondUsed:
                    Index = path.index(carbon) + 1
                else:
                    continue

                if Index in OxyBondIndexTemp and NitrogenStrength[NitrogenIndex.index(Index)] == 3:
                    return 'invalid'
                elif Index not in OxyBondIndexTemp and NitrogenStrength[NitrogenIndex.index(Index)] == 1:
                    OxyBondTypeTemp.append('amine')
                    OxyBondIndexTemp.append(path.index(carbon) + 1)
                elif Index not in OxyBondIndexTemp and NitrogenStrength[NitrogenIndex.index(Index)] == 3:
                    OxyBondTypeTemp.append('nitrile')
                    OxyBondIndexTemp.append(path.index(carbon) + 1)

        return [OxyBondTypeTemp, OxyBondIndexTemp, halogens]

    def ReverseOrder(self, PosEn, PosYn, ChainStrength, HalogenIndexTemp, length, AlkylIndex, AlkylLength,
                     OxyBondTypeTemp, OxyBondIndexTemp, halogens):
        # Reversing the direction of counting depending on priority
        PosAll = PosEn + PosYn
        PosAll.sort()
        reverse = False
        if len(OxyBondTypeTemp) > 0:
            if 'carboxylic acid' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('carboxylic acid')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('carboxylic acid')]:
                    reverse = True
            elif 'acid halide' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('acid halide')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('acid halide')]:
                    reverse = True
            elif 'amide' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('amide')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('amide')]:
                    reverse = True
            elif 'nitrile' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('nitrile')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('nitrile')]:
                    reverse = True
            elif 'aldehyde' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('aldehyde')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('aldehyde')]:
                    reverse = True
            elif 'ketone' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('ketone')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('ketone')]:
                    reverse = True
            elif 'alcohol' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('alcohol')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('alcohol')]:
                    reverse = True
            elif 'amine' in OxyBondTypeTemp:
                if OxyBondIndexTemp[OxyBondTypeTemp.index('amine')] > length - \
                        OxyBondIndexTemp[OxyBondTypeTemp.index('amine')]:
                    reverse = True

        # Alkenes/Aklynes > Alkyl Groups > Halides
        if 2 in ChainStrength or 3 in ChainStrength:
            if len(PosEn) > 0 and len(PosYn) > 0:
                # Alkenes and Alkynes take no extra priority, unless they are equidistant away from the ends, in which
                # Alkenes take numbering priority
                if PosAll[0] > length - PosAll[-1]:
                    reverse = True

                elif PosEn[-1] == length - PosYn[0]:
                    if PosEn[0] > PosYn[-1]:
                        reverse = True
            elif len(PosEn) > 0:
                if PosEn[0] > length - PosEn[-1]:
                    reverse = True
            elif len(PosYn) > 0:
                if PosYn[0] > length - PosYn[-1]:
                    reverse = True

        elif len(AlkylLength) > 0:
            if sorted(AlkylIndex)[0] > length - sorted(AlkylIndex)[-1]:
                reverse = True

        if 'acid halide' not in OxyBondTypeTemp and len(HalogenIndexTemp) > 0:
            if sorted(HalogenIndexTemp)[0] > length - sorted(HalogenIndexTemp)[-1]:
                reverse = True

        if reverse:
            for index in range(len(PosEn)):
                PosEn[index] = length - PosEn[index]
            for index in range(len(PosYn)):
                PosYn[index] = length - PosYn[index]
            for index in range(len(AlkylIndex)):
                AlkylIndex[index] = length - AlkylIndex[index] + 1
            for index in range(len(HalogenIndexTemp)):
                HalogenIndexTemp[index] = length - HalogenIndexTemp[index] - 1
            for index in range(len(OxyBondIndexTemp)):
                OxyBondIndexTemp[index] = length - OxyBondIndexTemp[index]
        PosEn.sort()
        PosYn.sort()
        halogens.reverse()
        OxyBondIndex = sorted(OxyBondIndexTemp)
        OxyBondType = []
        for index in OxyBondIndex:
            OxyBondType.append(OxyBondTypeTemp[OxyBondIndexTemp.index(index)])

        return [PosEn, PosYn, HalogenIndexTemp, AlkylIndex, OxyBondType, OxyBondIndex, halogens]

    # --- Prefix/Suffix deriving ---
    def HalogenNaming(self, HalogenIndex, PS, OxyBondTypeTemp, OxyBondIndexTemp):
        for lengths in range(4):
            if len(HalogenIndex[lengths]) == 0:
                continue

            halogen = PS[lengths + 21]

            positions = []
            count = 0
            for item in range(len(HalogenIndex[lengths])):
                if 'acid halide' in OxyBondTypeTemp:
                    if HalogenIndex[lengths][item - count] - 1 in OxyBondIndexTemp:
                        HalogenIndex[lengths].pop(item - count)
                        count += 1
                        continue

                if item - count == 0:
                    positions += f'{HalogenIndex[lengths][item - count]}'
                elif item - count < len(HalogenIndex[lengths]):
                    positions += f',{HalogenIndex[lengths][item - count]}'

            positions = ''.join(positions)

            subPrefix = []
            if len(HalogenIndex[lengths]) > 1:
                subPrefix += [f'{PS[len(HalogenIndex[lengths]) + 24]}']
            subPrefix = ''.join(subPrefix)

            prefix = f'{positions}-{subPrefix}{halogen}o-'
            if len(positions) == 0:
                prefix = ''

        return prefix

    def AlkylNaming(self, AlkylLength, PS, AlkylIndex):
        prefix = []
        for lengths in range(len(AlkylLength)):
            Alkyl = PS[AlkylLength[lengths] - 1]
            positions = ''

            for item in range(len(AlkylIndex[lengths])):
                if item == 0:
                    positions += f'{AlkylIndex[lengths][item]}'
                else:
                    positions += f',{AlkylIndex[lengths][item]}'

            subPrefix = ''
            if len(AlkylIndex[lengths]) > 1:
                subPrefix = f'{PS[len(AlkylIndex[lengths]) + 24]}'

            prefix.append(f'{positions}-{subPrefix}{Alkyl}yl-')
        return prefix

    def StrengthNaming(self, PosEne, PosYne, PS, ps):
        suffixEne = []
        if len(PosEne) > 0:
            positions = ''

            for item in range(len(PosEne)):
                if item == 0:
                    positions += f'{PosEne[item]}'
                else:
                    positions += f',{PosEne[item]}'

            subPrefix = ''
            if len(PosEne) > 1:
                subPrefix = f'{PS[len(PosEne) + 24]}'

            if len(ps[0]) == 0 and len(ps[1]) == 0:
                suffixEne.append(f'-{positions}-{subPrefix}ene')
            else:
                suffixEne.append(f'-{positions}-{subPrefix}en')
        suffixEne = ''.join(suffixEne)

        suffixYne = []
        if len(PosYne) > 0:
            positions = ''

            for item in range(len(PosYne)):
                if item == 0:
                    positions += f'{PosYne[item]}'
                else:
                    positions += f',{PosYne[item]}'

            subPrefix = ''
            if len(PosYne) > 1:
                subPrefix = f'{PS[len(PosYne) + 24]}'

            if len(ps[0]) == 0 and len(ps[1]) == 0:
                suffixYne.append(f'-{positions}-{subPrefix}yne')
            else:
                suffixYne.append(f'-{positions}-{subPrefix}yn')
        suffixYne = ''.join(suffixYne)
        return [suffixEne, suffixYne]

    def OxygenNitrogenNaming(self, OxyBondTypeTemp, OxyBondIndexTemp, halogens, PS, length):
        groups = self.OxygenNitrogenSort(OxyBondTypeTemp, OxyBondIndexTemp)
        carboxyacid = groups[0]
        acidhalide = groups[1]
        amide = groups[2]
        nitrile = groups[3]
        aldehyde = groups[4]
        ketone = groups[5]
        alcohol = groups[6]
        amine = groups[7]
        prefixGroup = []
        suffixGroup = []
        if len(carboxyacid) > 0:
            nameinfo = self.CarboxylicAcidNaming(carboxyacid, ketone, alcohol, PS, acidhalide, halogens, amide, nitrile,
                                                 amine, aldehyde, length)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(acidhalide) > 0:
            nameinfo = self.AcidHalideNaming(ketone, alcohol, PS, acidhalide, halogens, amide, nitrile, amine,
                                             aldehyde, length)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(amide) > 0:
            nameinfo = self.AmideNaming(ketone, alcohol, PS, amide, nitrile, amine, aldehyde, length)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(nitrile) > 0:
            nameinfo = self.NitrileNaming(ketone, alcohol, PS, nitrile, amine, aldehyde, length)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(aldehyde) > 0:
            nameinfo = self.AldehydeNaming(ketone, alcohol, PS, amine, aldehyde, length)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(ketone) > 0:
            nameinfo = self.KetoneNaming(ketone, PS, alcohol, amine)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(alcohol) > 0:
            nameinfo = self.AlcoholNaming(alcohol, PS, amine)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]

        elif len(amine) > 0:
            nameinfo = self.AmineNaming(amine)
            prefixGroup = nameinfo[0]
            suffixGroup = nameinfo[1]
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def OxygenNitrogenSort(self, OxyBondTypeTemp, OxyBondIndexTemp):
        carboxyacid = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'carboxylic acid':
                carboxyacid.append(OxyBondIndexTemp[count])
            count += 1

        acidhalide = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'acid halide':
                acidhalide.append(OxyBondIndexTemp[count])
            count += 1

        amide = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'amide':
                amide.append(OxyBondIndexTemp[count])
            count += 1

        nitrile = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'nitrile':
                nitrile.append(OxyBondIndexTemp[count])
            count += 1

        aldehyde = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'aldehyde':
                aldehyde.append(OxyBondIndexTemp[count])
            count += 1

        ketone = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'ketone':
                ketone.append(OxyBondIndexTemp[count])
            count += 1

        alcohol = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'alcohol':
                alcohol.append(OxyBondIndexTemp[count])
            count += 1

        amine = []
        count = 0
        for item in OxyBondTypeTemp:
            if item == 'amine':
                amine.append(OxyBondIndexTemp[count])
            count += 1
        return [carboxyacid, acidhalide, amide, nitrile, aldehyde, ketone, alcohol, amine]

    # ---Naming Oxygen/Nitrogen functional group prefixes/suffixes---
    def KetoneAlcoholNaming(self, ketone, alcohol, PS):
        tempprefix = []
        if len(ketone) > 0:
            tempketone = ''
            for index in ketone:
                if ketone[ketone.index(index)] != ketone[-1]:
                    tempketone += f'{index + 1},'
                else:
                    tempketone += f'{index + 1}-'

            subPrefix = ''
            if len(ketone) > 1:
                subPrefix = f'{PS[len(ketone) + 24]}'

            tempprefix.append(f'{tempketone}{subPrefix}oxo-')

        if len(alcohol) > 0:
            tempalcohol = ''
            for index in alcohol:
                if alcohol[alcohol.index(index)] != alcohol[-1]:
                    tempalcohol += f'{index + 1},'
                else:
                    tempalcohol += f'{index + 1}-'

            subPrefix = ''
            if len(alcohol) > 1:
                subPrefix = f'{PS[len(alcohol) + 24]}'

            tempprefix.append(f'{tempalcohol}{subPrefix}hyrdoxy-')

        return tempprefix

    def CarboxylicAcidNaming(self, carboxyacid, ketone, alcohol, PS, acidhalide, halogens, amide, nitrile, amine,
                             aldehyde, length):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(carboxyacid) == 2:
            subPrefix = 'di'
        suffixGroup.append(f'{subPrefix}oic acid')

        tempprefix = self.KetoneAlcoholNaming(ketone, alcohol, PS)
        prefixGroup += tempprefix
        if len(acidhalide) == 1:

            # Values of added to account for alphabetical order
            if halogens[0] == 4:
                added = 2
            elif halogens[0] == 5:
                added = 1
            elif halogens[0] == 6:
                added = 0
            elif halogens[0] == 7:
                added = 3
            prefixGroup.append(f'{PS[added + 21]}ocarbonyl-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(amide) == 1:
            prefixGroup.append(f'{length}-amido-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(nitrile) == 1:
            prefixGroup.append(f'{length}-cyano-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(aldehyde) == 1:
            prefixGroup.append(f'{length}-oxo-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(amine) == 1:
            prefixGroup.append(f'{length}-amino-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def AcidHalideNaming(self, ketone, alcohol, PS, acidhalide, halogens, amide, nitrile, amine,
                         aldehyde, length):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(acidhalide) == 2:
            return 'invalid'
        if halogens[0] == 4:
            added = 2
        elif halogens[0] == 5:
            added = 1
        elif halogens[0] == 6:
            added = 0
        elif halogens[0] == 7:
            added = 3
        suffixGroup.append(f'{subPrefix}oyl {PS[added + 21]}ide')

        tempprefix = self.KetoneAlcoholNaming(ketone, alcohol, PS)
        prefixGroup += tempprefix

        if len(amide) == 1:
            prefixGroup.append(f'{length}-amido-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(nitrile) == 1:
            prefixGroup.append(f'{length}-cyano-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(aldehyde) == 1:
            prefixGroup.append(f'{length}-oxo-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(amine) == 1:
            prefixGroup.append(f'{length}-amino-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def AmideNaming(self, ketone, alcohol, PS, amide, nitrile, amine, aldehyde, length):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(amide) == 2:
            subPrefix = 'di'
        suffixGroup.append(f'{subPrefix}amide')

        tempprefix = self.KetoneAlcoholNaming(ketone, alcohol, PS)
        prefixGroup += tempprefix

        if len(nitrile) == 1:
            prefixGroup.append(f'{length}-cyano-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(aldehyde) == 1:
            prefixGroup.append(f'{length}-oxo-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(amine) == 1:
            prefixGroup.append(f'{length}-amino-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def NitrileNaming(self, ketone, alcohol, PS, nitrile, amine, aldehyde, length):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(nitrile) == 2:
            subPrefix = 'di'
        suffixGroup.append(f'{subPrefix}nitrile')

        tempprefix = self.KetoneAlcoholNaming(ketone, alcohol, PS)
        prefixGroup += tempprefix

        if len(aldehyde) == 1:
            prefixGroup.append(f'{length}-oxo-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]

        elif len(amine) == 1:
            prefixGroup.append(f'{length}-amino-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def AldehydeNaming(self, ketone, alcohol, PS, amine, aldehyde, length):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(aldehyde) == 2:
            subPrefix = 'di'
        suffixGroup.append(f'{subPrefix}al')

        tempprefix = self.KetoneAlcoholNaming(ketone, alcohol, PS)
        prefixGroup += tempprefix

        if len(amine) == 1:
            prefixGroup.append(f'{length}-amino-')
            prefixGroup.reverse()
            return [prefixGroup, suffixGroup]
        return [prefixGroup, suffixGroup]

    def KetoneNaming(self, ketone, PS, alcohol, amine):
        prefixGroup = []
        suffixGroup = []
        tempketone = ''
        if len(ketone) > 1:
            for index in ketone:
                if ketone[ketone.index(index)] == ketone[0]:
                    tempketone += f'-{index},'
                elif ketone[ketone.index(index)] != ketone[-1]:
                    tempketone += f'{index},'
                else:
                    tempketone += f'{index}-'
        else:
            tempketone += f'-{alcohol[0]}-'

        subPrefix = f'{PS[len(ketone) + 24]}'

        if tempketone == '-0-':
            tempketone = ''

        suffixGroup.append(f'{tempketone}{subPrefix}one')

        if len(alcohol) > 0:
            tempalcohol = ''
            for index in alcohol:
                if alcohol[alcohol.index(index)] != alcohol[-1]:
                    tempalcohol += f'{index},'
                else:
                    tempalcohol += f'{index}-'
            subPrefix = ''

            if len(alcohol) > 1:
                subPrefix = f'{PS[len(alcohol) + 24]}'

            prefixGroup.append(f'{tempalcohol}{subPrefix}hyrdoxy-')

        if len(amine) == 1:
            prefixGroup.append(f'{amine[0]}-amino-')
            prefixGroup.reverse()
        return [prefixGroup, suffixGroup]

    def AlcoholNaming(self, alcohol, PS, amine):
        prefixGroup = []
        suffixGroup = []
        tempalcohol = ''
        if len(alcohol) > 1:
            for index in alcohol:
                if alcohol[alcohol.index(index)] == alcohol[0]:
                    tempalcohol += f'-{index},'
                elif alcohol[alcohol.index(index)] != alcohol[-1]:
                    tempalcohol += f'{index},'
                else:
                    tempalcohol += f'{index}-'
        else:
            tempalcohol += f'-{alcohol[0]}-'

        subPrefix = f'{PS[len(alcohol) + 24]}'

        if tempalcohol == '-0-':
            tempalcohol = ''

        suffixGroup.append(f'{tempalcohol}{subPrefix}ol')

        if len(amine) == 1:
            prefixGroup.append(f'{amine[0]}-amino-')
            prefixGroup.reverse()

        return [prefixGroup, suffixGroup]

    def AmineNaming(self, amine):
        prefixGroup = []
        suffixGroup = []
        subPrefix = ''
        if len(amine) == 2:
            subPrefix = 'di'
        suffixGroup.append(f'{subPrefix}amine')
        return [prefixGroup, suffixGroup]

    # --- String Concatenation ---
    def NonBreakCompound(self):
        # LongestPath = [length, path, bridge number, CarbonBond]
        LongestPath = self.LongestPath()
        if LongestPath == 'invalid':
            print('invalid')
            return

        length = LongestPath[0]
        path = LongestPath[1]
        ChainPos = LongestPath[2]
        CarbonBond = LongestPath[3]
        PathChainList = LongestPath[4]
        CarbonUsed = LongestPath[5]

        if len(CarbonBond) < len(CarbonUsed) - 1:
            print('invalid')
            return

        ChainStrength = self.ChainUpdate(path, CarbonBond)

        StrengthInfo = self.StrengthUpdate(ChainStrength)
        PosEne = StrengthInfo[0]
        PosYne = StrengthInfo[1]

        HalogenInfo = self.HalogenUpdate(path)
        if HalogenInfo == 'invalid':
            print('invalid')
            return
        HalogenIndexTemp = HalogenInfo[0]
        HalogenListTemp = HalogenInfo[1]

        OxygenInfo = self.OxygenNitrogenNonBreak(path, HalogenIndexTemp, HalogenListTemp)
        if OxygenInfo == 'invalid':
            print('invalid')
            return
        OxyBondTypeTemp = OxygenInfo[0]
        OxyBondIndexTemp = OxygenInfo[1]
        halogens = OxygenInfo[2]

        AlkylInfo = self.AlkylUpdate(path, PathChainList, ChainPos)
        AlkylIndex = AlkylInfo[0]
        AlkylLength = AlkylInfo[1]

        ReverseChainInfo = self.ReverseOrder(PosEne, PosYne, ChainStrength, HalogenIndexTemp, length,
                                             AlkylIndex, AlkylLength, OxyBondTypeTemp, OxyBondIndexTemp, halogens)
        PosEne = ReverseChainInfo[0]
        PosYne = ReverseChainInfo[1]
        HalogenIndexTemp = ReverseChainInfo[2]
        AlkylIndex = ReverseChainInfo[3]
        OxyBondTypeTemp = ReverseChainInfo[4]
        OxyBondIndexTemp = ReverseChainInfo[5]
        halogens = ReverseChainInfo[6]

        HalogenIndex = self.HalogenReupdate(HalogenListTemp, HalogenIndexTemp)

        AlkylInfo = self.AlkylReUpdate(AlkylIndex, AlkylLength)
        AlkylIndex = AlkylInfo[0]
        AlkylLength = AlkylInfo[1]

        name = []

        PS = []
        with open("PSTable.txt", "r") as PSTable:
            for lengths, line in enumerate(PSTable):
                temp = f'{line}'
                for char in temp:
                    if char == '\n':
                        temp = temp.replace('\n', '')
                PS.append(temp)

        # ---Oxygen/Nitrogen Functional Groups---
        ps = self.OxygenNitrogenNaming(OxyBondTypeTemp, OxyBondIndexTemp, halogens, PS, length)
        prefixON = ps[0]
        suffixON = ps[1]
        prefixON = ''.join(prefixON)


        # ---Halogens---
        prefix = self.HalogenNaming(HalogenIndex, PS, OxyBondTypeTemp, OxyBondIndexTemp)
        prefix = ''.join(prefix)
        name.append(prefix)
        name.append(prefixON)

        # ---Alkyl Groups---

        prefix = self.AlkylNaming(AlkylLength, PS, AlkylIndex)
        prefix = ''.join(prefix)
        name.append(prefix)

        # ---Main carbon chain---
        name.append(PS[length - 1])

        # ---Suffixes---
        suffixes = self.StrengthNaming(PosEne, PosYne, PS, ps)
        suffixEne = suffixes[0]
        suffixYne = suffixes[1]

        name.append(suffixEne)
        name.append(suffixYne)

        if 2 not in ChainStrength and 3 not in ChainStrength:
            if len(suffixON) == 0 and len(prefixON) == 0:
                name.append('ane')
            else:
                name.append('an')

        suffixON = ''.join(suffixON)
        name.append(suffixON)
        FinalName = ''.join(name)
        print(FinalName)
        return FinalName

    def Update(self):
        FinalName = self.NonBreakCompound()
        return FinalName
