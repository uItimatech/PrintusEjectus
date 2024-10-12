# -------------------------------------------------------------------------------------------------
# This program reads all print files in the "inputs" folder
# and outputs a modified version with a push from the print head
# at the end of the print for automatic removal of the print.

# All outputs are saved in the "outputs" folder. (they can be overwritten !)

# This program currently only works for single part prints.
# Multi-part prints are currently considered as a single part and the
# toolhead might not push all of them off the bed.

# Made by ultimatech
# -------------------------------------------------------------------------------------------------



import os
import re



# -------------------------------------------------------------------------------------------------
# !!! WARNING: Make sure to change the following variables to match your printer's print format !!!
# -------------------------------------------------------------------------------------------------
# (The default values are for Qidi X-Plus 3 printers)


# ----- Input formatting -----
FILEEXTENSION = ".gcode" # File extension of the print files, change if needed

PRINTSTART = "PRINT_START\n" # This is the line that indicates the start of the print
PRINTEND = "; EXECUTABLE_BLOCK_END\n" # This is the line that indicates the end of the print
LAYERCHANGE = ";LAYER_CHANGE\n" # This is the line that indicates a new layer
IGNOREDLAYERS = 2 # Number of layers to ignore at the beginning of the print

# ----- Output formatting -----
PRINTOFFCOMMENT = "; PUSH PRINT OFF BED\n" # This is the comment that indicates the push off bed
FILESUFFIX = "_pushed" # Suffix added to the output file

COOLINGTEMP = 30 # Temperature to wait for before pushing the print off the bed
COOLOFFNOZZLE = f"M109 S{COOLINGTEMP}; Waits for the nozzle to cool down\n" # This is the line that waits for the nozzle to cool down
HOMEXY = "G28 X Y; Homes the X and Y axis\n" # Homes the X and Y axis
GOTOBACK = "G1 X• Y260; Goes to the back of the printer\n" # Moves the print head to the back of printer without going down yet
GOTOBED = "G28 Z; Goes to the bed for print removal\n" # This is the line that moves the print head to the bed
PUSHCOORDINATES = "G1 Y20; Push print off bed\n" # This is the line that pushes the print off the bed

# WARNING: The "•" in some instructions will be replaced with the correct push location, make sure to keep it in the string !





DEBUG = True # Set to True to enable debug mode (prints additional information)

# -------------------------------------------------------------------------------------------------

def read_file(fileID):
    '''
    Open the first print file in the "inputs" folder
    and read all the lines in the file
    '''

    with open('inputs/' + os.listdir('inputs')[fileID], 'r') as file:
        lines = file.readlines()

    return lines



def get_x_coordinates(lines):
    '''
    Get the X coordinates of the printer head
    after the first few layers.
    Ignores all the lines until PRINTSTART
    and stops at PRINTEND
    '''

    x_coordinates = []
    while lines[0] != PRINTSTART:
        lines.pop(0)

    currentLayer = 1
    for line in lines:
        if line == PRINTEND:
            break
            
        if line == LAYERCHANGE:
            currentLayer += 1

        # Modify this condition if you wish to acquire a different line
        if line[0] == "G" and currentLayer > IGNOREDLAYERS:
            x = re.search(r"X\d+\.\d+", line)
            if x:
                x_coordinates.append(float(x.group()[1:]))

    return x_coordinates



def get_width(x_coordinates):
    '''
    Get the width of the object
    based on the min and max X coordinates reached by the printer head
    '''
    return round(max(x_coordinates) - min(x_coordinates),2)



def get_mean(x_coordinates):
    '''
    Get the mean of the given X coordinates
    '''
    return round(sum(x_coordinates) / len(x_coordinates),2)



def create_output(lines, fileID):
    '''
    Create the output file with the same name as the input file
    and write the new lines after the print end
    '''

    with open('outputs/' + os.listdir('inputs')[fileID][:-len(FILEEXTENSION)] + FILESUFFIX + FILEEXTENSION, 'w') as file:

        x_coordinates = get_x_coordinates(lines)
        printWidth = get_width(x_coordinates)
        meanCoordinate = get_mean(x_coordinates)

        # DEBUG ONLY
        if DEBUG:
            print("\tX range: [" + str(min(x_coordinates)) + " - " + str(max(x_coordinates)) + "]")
            print("\tPrint width: ~" + str(printWidth) + "mm")
            print("\tMean X coordinate: ~" + str(meanCoordinate) + "mm")

        # Inserts the go to bed and push coordinates after the end of the print instruction

            
        for line in lines:
            if line == PRINTEND:
                file.write(line)
                file.write(PRINTOFFCOMMENT)
                file.write(COOLOFFNOZZLE)
                file.write(HOMEXY)
                file.write(GOTOBACK.replace("•", str(meanCoordinate)))
                file.write(GOTOBED)
                file.write(PUSHCOORDINATES.replace("•", str(meanCoordinate)))
            file.write(line)
        



# -------------------------------------------------------------------------------------------------



def main():

    # Clears the console - DEBUG ONLY
    if DEBUG:
        os.system('cls' if os.name == 'nt' else 'clear')

    # If the inputs or outputs folders do not exist, create them
    if not os.path.exists('inputs'):
        os.makedirs('inputs')
    if not os.path.exists('outputs'):
        os.makedirs('outputs')


    totalCount = len(os.listdir('inputs'))

    # For each print file in the "inputs" folder
    for i in range(totalCount):
        if os.listdir('inputs')[i][-len(FILEEXTENSION):] != FILEEXTENSION:
            continue
        
        currentCount = i + 1

        print(f"\nProcessing file {currentCount}/{totalCount}: " + os.listdir('inputs')[i])
        create_output(read_file(i), i)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()