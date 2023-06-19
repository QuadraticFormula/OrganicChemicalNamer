# OrganicChemicalNamer
An interactive piece of software that just names organic compounds using click and drag elements.

------------------------------------------------------------------------------------------------------

The code for this right now is somewhat inconsistent and a bit shit for the Base_Namer_GUI 
but I just ran out of time for this assignment and couldn't be bothered to fix a bunch of
the minor issues since they don't break the program and the names are still basically
correct for the most part :/

For now, the program can only name organic compounds without any broken chains, meaning no esters
where there's 2 seperate chain segments. It can name different bond strengths within the carbon chain,
and the different alkyl groups, and of the functional groups that do exist, it is able to name: 

* Carboxylic Acids
* Acid Halides
* Amides
* Nitriles
* Aldehydes
* Ketones
* Alcohols
* Amines
* Regular Halides

The naming priority, i.e. which end of the carbon chain that it is counted from and whether a 
functional group is a suffix or prefix, is done in the order above from highest priority to 
lowest.

------------------------------------------------------------------------------------------------------

Element dragging is done by holding down the mouse over the element select and dragging it into the 
grid, and placing bonds + updating bond strengths is done by clicking the spaces in between elements.

The grid itself is draggable and infinite. The two buttons that appear after placing down an element
is to reset the position of the screen if you drag too far away from the compound and can't find it 
(This happened too much during testing :/) and a general reset of the elements on the screen.

The home menu does nothing, and the actual final verson of this software is on my laptop where I uploaded
the final piece of code directly to the submission and never backed it up, and rn I don't have access to it,
so once I have the chance I'll update the piece of code that actually draws the name of the compound on the
screen - for now it is just printed in the console.
