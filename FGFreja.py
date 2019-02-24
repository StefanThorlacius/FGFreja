#
# This program convert a raw data file into a readable file for function generators
#
# Original written by Stefna Thorlacious
#
# Version 1.0
#
# This program convert a readable text file with data samples into a aribrary wave form file for waveform generators
#
# The program can either take raw volatage levels or a stram of 0 and 1 and convert them to voltage levels 
#
# The program do the following
# 1. Scan and intepretate the arguments
# 2. Read the input file
# 3. Post process the data from the input file in accordance to the arguments
# 4. Save the converted data to a file
#

import sys, getopt, os
import pathlib
from pathlib import Path, PurePath

from math import fabs


class Convert2FG:

    #
    # Supported function generators
    #
    # Name, output min Volt, output max Volt, number of sample points, zero offset
    #
    functiongenerator_type = [
        ['P4165', -10.0, 10.0, 8152],   # Tested by Stefan Thorlacius
        ['P4120', -12.5, 12.5, 8000],   # Not tested
        ['P4121', -12.5, 12.5, 8000],   # Not tested
        ['P4124', -10.0, 10.0, 8000],   # Not tested
        ['P4125', -10.0, 10.0, 8000],   # Not tested
    ]

    #
    # Currently the supported languages
    #
    languagecollection = [
        [0, 'English'],
        [1, 'Svenska'],
    ]
    
    #
    # Translations table
    # 
    languageall = [
        [' takes an infile with data samples and convert them into a file readable by specific function generators',
         ' läser en fil med mätvärden och omvandlar dom till en fil som är läsbar av en funktions generator',
        ],
        ['It can rescale and will clip indata so it is not outside the range of the function generator',
         'Programmet can skala om och kommer att klippa invärderna så att dom inte är utanför användingsområdet för funktions generator',
        ],
        ['The indata can also be an expression of logic values, that is, 00001111 and convert them into analoige values for the function generator',
         'Indata kan också vara en uttryck av logiska värden, såsom, 00001111 och omvandla dom till analoga värden för funktions generatorn',
        ],
        ['Indata file is a readable text file where the anaolouge values are expressed in voltage and seperated with a distinctive charater',
         'Infilen är en läsbar textfil där dom analoga värdena uttrycks i Volt och separerade med ett valfritt tecken',
        ],
        [' -i <inputfile> -o <outputfile> -s <split character> -m <max value> -n <min value> -p <scale value> -f <function generator model> -l <language> -d <debug level> -g -z -c <logic level>',
         ' -i <infil> -o <utfil> -s <splittrings tecken> -m <max värde> -n <min värde> -p <skal värdet> -f <funktionsgenerator model> -l <språk> -d <debug nivå> -g -z -c <logic level>',
        ],
        ['if -o is omitted the output file will be at same place as inputfile with ending .bin',
         'Om -o inte är angivet, då placeras utfilen på samma ställe som infilen men med ändelsen .bin',
        ],
        ['if -f <fg> is present, <fg> will define the target function generator, if omitted, ',
         'Om -f <fg> är angivet, då definerar <fg> vilken funktionsgenerator som är målmaskinen, om -f inte anges så ',
        ],
        [' will be used as default',
         ' används om inget annat anges',
        ],
        ['                  valid function generators are ',
         '                  kända funktionsgeneratorer är ',
        ],
        ['if -j is present, then the infile be treatead as a stream of logic values, like 000111100',
         'Om -j är angivet, då kommer infilen behandlas some en ström av logiska värden, såsom 000111100',
        ],
        ['if -m is present, then any value above this value will be cut to <max value>, <max value> is in volt',
         'Om -m är angivet, då kommer alla värden i infilen att klippas till <max value>, <min value> anges i volt',
        ],
        ['if -n is present, then any value below this value will be cut to <min value>, <min value> is in volt',
         'Om -n är angivet, då kommer alla värden i infilen att klippas till <min value>, <min value> anges i volt',
        ],
        ['if -s is present, then the character <split character> will be used to seperate values in the input file',
         'Om -s är angivet, då används <split character> som separator mellan värden i infilen',
        ],
        ['if -p is present, then input values will be scaled, <scale value> = min, max or a voltage level expressed as a floating point',
         'Om -p är angivet, då skalas all värden i infilen, <skal värdet> = max eller ett decimal tal',
        ],
        ['                  if max, then all values are scaled until the lowest is equal to the function generators minimum value',
         '                  om max, då skalas alla värden så att ingen understiger eller överstiger min och max spänningen för vald funktionsgenerator',
        ],
        ['                  if floating point value, then all values are multiplied with the scale valu but clipped by function generator max and min value',
         '                  om decimal tal då skalas alla värden med skal värdet men klips om dom understiger eller överstiger min och max spänningen för vald funktionsgenerator',
        ],
        ['if -l <val> is present, it will define the language used in the output text, valid values are',
         'Om -l <värde> är angivet, anger vilket språk som skall användas i utskrifter',
        ],
        ['if -d is present, it will set the level of debug messages printed during execution ',
         'Om -d är angivet, anger vilken nivå av debug meddelanden som skrivs ut under körning',
        ],
        ['if -g is present, it it will list all aviable funktion generators and then exit ',
         'Om -g är angivet, så listas all tillgängliga funktionsgenerator och sen avbryts körningen',
        ],
        ['if -c <logic level> is present, then <logic level> will split the values into logic level, for example, ',
         'Om -c <logik nivå> är angivet, då anger <logik nivå> hur indata kommer att omvandlas till logiska volt nivåer,',
        ],
        ['                   if <logic level> = TTL then all values above 2.0 Volt will be transfered into 5 Volt and all others 0.0 Volt',
         '                   om <logic level> = TTL då kommer alla värden högre än 2,0 Volt bli 5,0 Volt och alla andra bli 0,0 Volt',
        ],
        ['                   if <logic level> = ECL then all values above -1.2 Volt will be transfered into 0 volt and all others -2.0 Volt',
         '                   om <logic level> = ECL då kommer alla värden högre än -1,2 Volt bli 0,0 volt och alla andra bli -5,2 Volt',
        ],
        ['                   if <logic level> = CMOS <val> then all values above 2/3 of <val> will be <val> Volt and all others 0.0 Volt',
         '                   om <logic level> = CMOS <val> då kommer alla värden högre än 2/3 av <val> bli <val> Volt och alla andra bli 0,0 Volt',
        ],
        ['if -z is present, then',
         'Om -z ä rangivet, då',
        ],
        ['                  for PeakTech 4120/4121/4124/4125/4165 the function generator should interpolate between samples',
         '                  då kommer PeakTech 4120/4121/4124/4125/4165 att interpolera mellan dom givna värderna',
        ],
        ['Values in the infile can use both . and , as decimal seperator',
         'Invärden i infilen kan använda både . och , som decimal avskiljare',
        ],
        ["The following exmaples takes an input file and adapt it for the function generator P4165",
         "Följande exempel läser en input fil och anpassar den för funktions generatorn P4165",
        ],
        ["Clip indata if they are out of range, data samples are seperated with a ':'  ",
         "Klipp indata om värderna är utanför spänningingsomfånget, värderna är separerade med ett ':'  ",
        ],
        ["Convert indata to CMOS 3.3 Volt, data samples are seperated with a ':'  ",
         "Omvandla indata så att det blir CMOS 3,3 Volt, värderna är separerade med ett ':'  ",
        ],
        ["Convert indata to CMOS 3.3 Volt, indata is a stream of 0 and 1, like 000110011, no seperation between values",
         "Omvandla indata så att det blir CMOS 3,3 Volt, värderna är en ström av 0 och 1, såsom 000110011, ingen seperation mellan värderna",
        ],
        ['Unknown or wrong argument ',
         'Okänd eller felaktig argument ',
        ],
        ['Supported function generators',
         'Följande funktionsgeneratorer stöds',
        ],
        ['Argument -d is not a valid debug level',
         'Argumented till -d är inte en giltig debug nivå',
        ],
        ['Argument -c CMOS is not a valid floating point number expressed in Volt',
         'Argumented till -c CMOS är inte en giltligt decimal tal uttryckt i Volt',
        ],
        ['Argument to -c is unknown',
         'Argumented till -c är okänt',
        ],
        ['minimum voltage',
         'minimum spänning',
        ],
        ['maximum voltage',
         'maximum spänning',
        ],
        ['sample points',
         'mätpunkter',
        ],
        ['Argument to -l is an unknown language',
         'Argumented till -l är ett okänt språk',
        ],
        ['Argument -m is not a valid floating point number expressed in Volt',
         'Argumented till -m är inte ett giltligt tal uttryck i Volt',
        ],
        ['Argument -n is not a valid floating point number expressed in Volt',
         'Argumented till -n är inte ett giltligt tal uttryck i Volt',
        ],
        ['Argument -p is not a valid floating point number expressed in Volt or the string <max>',
         'Argumented till -p är inte ett giltligt tal uttryck i Volt eller strängen <max>',
        ],
        ['Input file is missing as an argument',
         'Infilen fattas som argument',
        ],
        ['Input file does not exist',
         'Infilen finns inte',
        ],
        ['Output file path or file name is reserved',
         'Utfilens sökväg är reserverad',
        ],
        ['Argument to -f is an unknown function generator',
         'Argumented till -f är en okänd funktionsgenerator',
        ],
        ["Function for saving data to '",
         "Funktion för att spara data till '",
        ],
        ["' does not exist",
         "' är inte definerad",
        ],
        ['No data in input file',
         'Infilen är tom',
        ],
        ['Value ',
         'Värde ',
        ],
        [' is not a floating point number on line ',
         ' är inte ett decimal tal på rad ',
        ],
        [' at position ',
         ' position ',
        ],
        ['I/O error',
         'I/O fel',
        ],
        ['Unexpected error:',
         'Oväntad fel:',
        ],
        ['To many samples in input file, ',
         'Fär många datapunkter i infilen, ',
        ],
        [', max is ',
         ', max antal är',
        ],
        ['Argument to -l is not languge that exist',
         'Argumented to -l är inte ett språk som finns',
        ],
        ['Argument to -l is not a valid integer',
         'Argumented till -l är inte ett heltal',
        ],
        ["There is not support for saving data to '",
         "Det finns ingen support för att spara till '",
        ],
    ]

    # path, either relative or absolute, to the input data file
    #
    inputfile = None

    #
    # path, either relative or absolute, to the output file
    #
    outputfile = None

    #
    # Which function generator is target
    #
    functiongenerator = ""

    #
    # Which character should be used to seperate values in a text file
    #
    splitchar = ' '

    #
    # Data samples read from the input file
    # This list is keept to access the orignal data samples in the input file
    # Normally all actions and writing is made from the datasample list
    #
    datasampleraw = []

    #
    # Data samples after the post processing phase based on the datasampleraw
    #
    datasample = []

    #
    # Switch on or off debug messages
    #
    dbglevel = 0

    #
    # Clip any input value above maxclipvalue to maxclipvalue and below minclipvalue to minclipvalue
    #
    maxclipvalue = 0.0
    minclipvalue = 0.0

    #
    # Scale all input values to the maximum input range of the function generator
    #
    scalevalue = 1.0
    scalemax = False

    #
    # Max value of the data samples in datasample
    #
    valuemax = 0.0

    #
    # Min value of the data samples in datasample
    #
    valuemin = 0.0

    #
    # The maximum number of sample points the target function generator can handle
    #
    maxsamplepoint = 0

    #
    # Which language should be used for output messages
    #
    languageselect = 0

    #
    # If the data sample points represent a logic stream, that is 00110011
    #
    convertvalid = False
    convertlimit = 0.0
    convertupper = 0.0
    convertlower = 0.0
    
    #
    # If the infile content should be a stream of logic values, like 0000110011 accordance to Active-high signal
    #
    infilelogicstream = False
    
    #
    # z argument have been added as an argument
    # For the function generators PeakTech 4120/4121/4124/4125/4165, this means the function generator should interpolate or not between samples
    #
    zflag_is_set = False
    
    def setdefault(self):
        #
        # Set default values
        #
        self.inputfile = None
        self.outputfile = None
        #
        self.splitchar = ' '
        self.datasampleraw = []
        self.datasample = []
        self.dbglevel = 0
        #
        self.minclipvalue = sys.float_info.min
        self.maxclipvalue = sys.float_info.max
        #
        self.scalevalue = 1.0
        self.scalemax = False
        #
        self.valuemax = 0.0
        self.valuemin = 0.0
        #
        fg = self.functiongenerator_type[0]
        self.functiongenerator = fg[0]
        self.minclipvalue = fg[1]
        self.maxclipvalue = fg[2]
        self.maxsamplepoint = fg[3]
        #
        self.languageselect = 0
        #
        self.convertvalid = False
        self.convertlimit = 2.20
        self.convertupper = 3.3
        self.convertlower = 0.0
        #
        self.infilelogicstream = False
        #
        self.zflag_is_set = False
        #
        return True


    def normalprint(self, str, addnl = True):
        #
        # Print normal messages
        #
        if addnl:
            print(str)
        else:
            print(str, end = "")


    def debugprint(self, level, str, addnl = True):
        #
        # Print debug message if it is of right level
        #
        if self.dbglevel >= level:
            if addnl:
                print(str)
            else:
                print(str, end = "")


    def outputtext(self, str):
        #
        # Print right translation of the text
        #
        if self.languageselect == 0:
            return str

        for lang in self.languageall:
            if str == lang[0]:
                return lang[self.languageselect]

        #
        sys.stdout.write(os.linesep + os.linesep + "String '" + str + "' has not been translated" + os.linesep + os.linesep)
        return str


    def printHelpText(self, nname):
        #
        # Print help text for the program
        #
        self.normalprint(nname + self.outputtext(' takes an infile with data samples and convert them into a file readable by specific function generators'))
        self.normalprint(self.outputtext('It can rescale and will clip indata so it is not outside the range of the function generator'))
        self.normalprint(self.outputtext('The indata can also be an expression of logic values, that is, 00001111 and convert them into analoige values for the function generator'))
        self.normalprint(self.outputtext('Indata file is a readable text file where the anaolouge values are expressed in voltage and seperated with a distinctive charater'))
        self.normalprint('')
        self.normalprint(nname, False)
        self.normalprint(self.outputtext(' -i <inputfile> -o <outputfile> -s <split character> -m <max value> -n <min value> -p <scale value> -f <function generator model> -l <language> -d <debug level> -g -z -c <logic level>'))
        self.normalprint(self.outputtext('if -o is omitted the output file will be at same place as inputfile with ending .bin'))
        #
        self.normalprint(self.outputtext('if -f <fg> is present, <fg> will define the target function generator, if omitted, '), False)
        self.normalprint(self.functiongenerator, False)
        self.normalprint(self.outputtext(' will be used as default'))
        self.normalprint(self.outputtext('                  valid function generators are '), False)
        for i in range(0, len(self.functiongenerator_type)):
            self.normalprint(self.functiongenerator_type[i][0], False)
            if i < (len(self.functiongenerator_type) - 1):
                self.normalprint(', ', False)
        self.normalprint('')
        #
        self.normalprint(self.outputtext('if -j is present, then the infile be treatead as a stream of logic values, like 000111100'))
        self.normalprint(self.outputtext('if -m is present, then any value above this value will be cut to <max value>, <max value> is in volt'))
        self.normalprint(self.outputtext('if -n is present, then any value below this value will be cut to <min value>, <min value> is in volt'))
        self.normalprint(self.outputtext('if -s is present, then the character <split character> will be used to seperate values in the input file'))
        self.normalprint(self.outputtext('if -p is present, then input values will be scaled, <scale value> = min, max or a voltage level expressed as a floating point'))
        self.normalprint(self.outputtext('                  if max, then all values are scaled until the lowest is equal to the function generators minimum value'))
        self.normalprint(self.outputtext('                  if floating point value, then all values are multiplied with the scale valu but clipped by function generator max and min value',))
        self.normalprint(self.outputtext('if -l <val> is present, it will define the language used in the output text, valid values are'), False)
        self.normalprint(' ', False)
        for i in range(0, len(self.languagecollection)):
            self.normalprint(str(i) + ' (' + self.languagecollection[i][1] + ')', False)
            if i < (len(self.languagecollection) - 1):
                self.normalprint(', ', False)
        self.normalprint('')
        self.normalprint(self.outputtext('if -d is present, it will set the level of debug messages printed during execution '))
        self.normalprint(self.outputtext('if -g is present, it it will list all aviable funktion generators and then exit '))
        self.normalprint(self.outputtext('if -c <logic level> is present, then <logic level> will split the values into logic level, for example, '))
        self.normalprint(self.outputtext('                   if <logic level> = TTL then all values above 2.0 Volt will be transfered into 5 Volt and all others 0.0 Volt'))
        self.normalprint(self.outputtext('                   if <logic level> = ECL then all values above -1.2 Volt will be transfered into 0 volt and all others -2.0 Volt'))
        self.normalprint(self.outputtext('                   if <logic level> = CMOS:<val> then all values above 2/3 of <val> will be <val> Volt and all others 0.0 Volt'))
        self.normalprint(self.outputtext('if -z is present, then'))
        self.normalprint(self.outputtext('                  for PeakTech 4120/4121/4124/4125/4165 the function generator should interpolate between samples'))
        self.normalprint(self.outputtext('Values in the infile can use both . and , as decimal seperator'))
        self.normalprint('')
        self.normalprint('')
        self.normalprint(self.outputtext("The following exmaples takes an input file and adapt it for the function generator P4165"))
        self.normalprint('')
        self.normalprint(nname + " -i <input file> -s ':' -f \"P4165\"                   ", False)
        self.normalprint(self.outputtext("Clip indata if they are out of range, data samples are seperated with a ':'  "))
        self.normalprint(nname + " -i <input file> -s ':' -c \"CMOS 3.3\" -f \"P4165\"     ", False)
        self.normalprint(self.outputtext("Convert indata to CMOS 3.3 Volt, data samples are seperated with a ':'  "))
        self.normalprint(nname + " -i <input file> -s ''  -c \"CMOS:3.3\" -f \"P4165\" -j  ", False)
        self.normalprint(self.outputtext("Convert indata to CMOS 3.3 Volt, indata is a stream of 0 and 1, like 000110011, no seperation between values"))
        #

    def checkargv(self, nname, argv):
        #
        # Check all arguments given to the program
        #
        try:
            opts, args = getopt.getopt(argv,"hgjzi:o:f:s:l:m:n:p:d:c:")
        except getopt.GetoptError:
            self.normalprint(self.outputtext('Unknown or wrong argument '))
            self.normalprint("nname  " + nname)
            self.printHelpText(nname)
            return False

        inf = ''
        outf = ''
        for opt, arg in opts:
            #
            # Set the logic voltage level
            if opt in ("-c"):
                self.convertvalid = True
                tv = arg.split(':')
                #
                if tv[0].upper() == 'TTL':
                    self.convertlimit = 2.0
                    self.convertupper = 5.0
                    self.convertlower = 0.0

                elif tv[0].upper() == 'ECL':
                    self.convertlimit = -1.2
                    self.convertupper = 0.0
                    self.convertlower = -5.2

                elif tv[0].upper() == 'CMOS' and len(tv) > 1:
                    try:
                        self.convertupper = float(tv[1])
                    except:
                        self.normalprint(self.outputtext('Argument -c CMOS is not a valid floating point number expressed in Volt'))
                        return False

                    self.convertlimit = (2.0 / 3.0) * self.convertupper
                    self.convertlower = 0.0
                else:
                    self.normalprint(self.outputtext('Argument ' + tv[0] + ' to -c is unknown'))
                    self.normalprint(self.outputtext('Argument ' + arg + ' to -c is unknown'))
                    self.normalprint(self.outputtext('len(tv) ' + str(len(tv))))
                    return False

            #
            # Debug level messages
            elif opt in ("-d"):
                try:
                    self.dbglevel = int(arg)
                except:
                    self.normalprint(self.outputtext('Argument -d is not a valid debug level'))
                    return False

            #
            # Set the target function generator
            elif opt in ("-f"):
                self.functiongenerator = arg

            #
            # Input file name
            elif opt in ("-g"):
                self.normalprint(self.outputtext('Supported function generators'))
                for fgt in self.functiongenerator_type:
                    self.normalprint(fgt[0] + '   ' + self.outputtext('minimum voltage') + 'minimum voltage {0:.4f}    ' + self.outputtext('maximum voltage') + ' {1:.4f}   ' + self.outputtext('sample points') + ' {2:6d}'.format(fgt[1], fgt[2], fgt[3]))
                return False

            #
            # Help messages
            elif opt == '-h':
                self.printHelpText(nname)
                return False

            #
            # Input file name
            elif opt in ("-i"):
                inf = arg

            #
            # Input file name
            elif opt in ("-j"):
                self.infilelogicstream = True

            #
            # Select language 
            elif opt in ("-l"):
                try:
                    self.languageselect = int(arg)
                    found = False
                    for i in range(0, len(self.languagecollection)):
                        if self.languagecollection[i][0] == self.languageselect:
                            found = True
                    if not found:
                        self.normalprint(self.outputtext('Argument to -l is not languge that exist'))
                        return False
                except:
                    self.normalprint(self.outputtext('Argument to -l is not a valid integer'))
                    return False


            #
            # Use maximum clip value
            elif opt in ("-m"):
                try:
                    self.maxclipvalue = float(arg)
                except:
                    self.normalprint(self.outputtext('Argument -m is not a valid floating point number expressed in Volt'))
                    return False

            #
            # Use minimum clip value
            elif opt in ("-n"):
                try:
                    self.minclipvalue = float(arg)
                except:
                    self.normalprint(self.outputtext('Argument -m is not a valid floating point number expressed in Volt'))
                    return False

            #
            # Output file name
            elif opt in ("-o"):
                outf = arg

            #
            # Scale input values so the match maximum range of function generator
            elif opt in ("-p"):
                if arg.lower() == 'max':
                    self.scalemax = True
                else:
                    try:
                        self.scalevalue = float(arg)
                        self.scalemax = False
                    except:
                        self.normalprint(self.outputtext('Argument -p is not a valid floating point number expressed in Volt or the string <max>'))
                        return False

            #
            # Which character should be used to seperate values in input text file
            elif opt in ("-s"):
                self.splitchar = arg

            # If the z flag is set, 
            # for PeakTech 4120/4121/4124/4125/4165 this mean that the function generator should interpolate or not between samples
            #
            elif opt in ("-z"):
                self.zflag_is_set = True

        #
        # Change values depending on the given arguments
        #
        if len(inf) < 1:
            self.normalprint(self.outputtext('Input file is missing as an argument'))
            return False

        self.inputfile = Path(inf)
        if not self.inputfile.is_file():
            self.normalprint(self.outputtext('Input file does not exist'))
            return False

        if pathlib.PureWindowsPath(self.inputfile).is_reserved():
            self.normalprint(self.outputtext('Input file does not exist'))
            return False

        if pathlib.PurePosixPath(self.inputfile).is_reserved():
            self.normalprint(self.outputtext('Input file does not exist'))
            return False

        if len(outf) < 1:
            self.outputfile = self.inputfile.with_suffix('.bin')

        if pathlib.PureWindowsPath(self.outputfile).is_reserved():
            self.normalprint(self.outputtext('Output file path or file name is reserved'))
            return False

        if pathlib.PurePosixPath(self.outputfile).is_reserved():
            self.normalprint(self.outputtext('Output file path or file name is reserved'))
            return False

        if self.minclipvalue > self.maxclipvalue:
            self.normalprint(self.outputtext('Output file path or file name is reserved'))
            return False

        found = False
        for fgt in self.functiongenerator_type:
            if self.functiongenerator == fgt[0]:
                #
                found = True
                self.maxsamplepoint = fgt[3]
                #
                #
                if self.minclipvalue < fgt[1] or self.minclipvalue > fgt[2]:
                    self.minclipvalue = fgt[1]
                #
                #
                if self.maxclipvalue < fgt[1] or self.maxclipvalue > fgt[2]:
                    self.maxclipvalue = fgt[2]
                #
                #
        if not found:
            self.normalprint(self.outputtext('Argument to -f is an unknown function generator'))
            return False


        self.debugprint(1, 'debug level       ' + str(self.dbglevel))
        self.debugprint(1, 'Input file        ' + str(self.inputfile))
        self.debugprint(1, 'Output file       ' + str(self.outputfile))
        self.debugprint(1, 'Split character   >' + str(self.splitchar) + '<')
        self.debugprint(1, 'functiongenerator ' + self.functiongenerator)
        self.debugprint(1, 'minclipvalue      ' + str(self.minclipvalue))
        self.debugprint(1, 'maxclipvalue      ' + str(self.maxclipvalue))
        self.debugprint(1, 'scalemax          ' + str(self.scalemax))
        self.debugprint(1, 'scalevalue        ' + str(self.scalevalue))
        self.debugprint(1, 'maxsamplepoint    ' + str(self.maxsamplepoint))
        self.debugprint(1, 'infilelogicstream ' + str(self.infilelogicstream))
        self.debugprint(1, 'convertvalid      ' + str(self.convertvalid))
        self.debugprint(1, 'convertlimit      ' + str(self.convertlimit))
        self.debugprint(1, 'convertlower      ' + str(self.convertlower))
        self.debugprint(1, 'convertupper      ' + str(self.convertupper))

        return True


    def readinputfile(self):
        #
        # Read the input file
        #

        values = []
        linecnt = 0
        poscnt = 0
        valuemin = 0.0
        valuemax = 0.0

        self.debugprint(1, 'Reading file ' + str(self.inputfile))
        self.debugprint(1, '')
        
        with open(self.inputfile, "r") as f:
            
            #
            # Read each line
            #
            linecnt = 0
            poscnt = 0
            #
            for dataline in f:
                if len(dataline) > 0:
                    self.debugprint(2, 'Read line ' + dataline)

                    if len(self.splitchar) > 0:
                        datapos = dataline.split(self.splitchar)
                    else:
                        datapos = list(dataline)

                    for pos in datapos:
                        newvalue = 0.0
                        try:
                            pos = pos.replace(",", ".")
                            newvalue = float(pos)
                            self.datasampleraw.append(newvalue)
                        except ValueError:
                            self.normalprint(self.outputtext('Value ') + pos + self.outputtext(' is not a floating point number on line ') + str(linecnt) + self.outputtext(' at position ') + str(poscnt))
                            return False

                        poscnt = poscnt + len(pos)

                linecnt = linecnt + 1

        if len(self.datasampleraw) < 1:
            self.normalprint(self.outputtext('No data in input file'))
            return False

        self.debugprint(1, 'Number values found ' + str(len(self.datasampleraw)))
        self.debugprint(1, '')
        #
        #
        return True


    def postprocessdata(self):
        #
        # Post process the data
        #
        self.valuemax = sys.float_info.min
        self.valuemin = sys.float_info.max
        #
        for i in range(0, len(self.datasampleraw)):
            self.debugprint(2, "{p:8.2f}".format(p = self.datasampleraw[i]), False)
        self.debugprint(2, '')
        #
        self.datasample = []
        for i in range(0, len(self.datasampleraw)):
            self.datasample.append(self.datasampleraw[i])
        #
        #
        if self.convertvalid:
            #
            # Input data samples are a stream of logic levels
            #
            for i in range(0, len(self.datasample)):
                if self.infilelogicstream:
                    if self.datasample[i] > 0.0:
                        self.datasample[i] = self.convertupper
                    else:
                        self.datasample[i] = self.convertlower
                else:
                    if self.datasample[i] >= self.convertlimit:
                        self.datasample[i] = self.convertupper
                    else:
                        self.datasample[i] = self.convertlower
        else:
            #
            # Input value is analouge values
            #
            for i in range(0, len(self.datasample)):
                if self.datasample[i] > self.valuemax:
                    self.valuemax = self.datasample[i]
                
                if self.datasample[i] < self.valuemin:
                    self.valuemin = self.datasample[i]
            #
            # Shall the input value be scaled
            #
            sv = self.scalevalue
            if self.scalemax:
                if self.valuemax != 0.0:
                    sv = self.maxclipvalue / fabs(self.valuemax)

                if self.valuemin != 0.0:
                    if (self.minclipvalue / fabs(self.valuemin)) > sv:
                        sv = self.maxscalevalue / fabs(self.valuemin)
            # Scale
            for i in range(0, len(self.datasample)):
                self.datasample[i] = sv * self.datasample[i]
        #
        # Clip input value if outside limits of the function generator
        #
        for i in range(0, len(self.datasample)):
            if self.datasample[i] > self.maxclipvalue:
                self.datasample[i] = self.maxclipvalue
            #
            if self.datasample[i] < self.minclipvalue:
                self.datasample[i] = self.minclipvalue
        #
        for i in range(0, len(self.datasample)):
            self.debugprint(2, "{p:8.2f}".format(p = self.datasample[i]), False)
        self.debugprint(2, '')
        #
        # Recalculate max and min values from the data samples
        #
        self.valuemax = sys.float_info.min
        self.valuemin = sys.float_info.max
        #
        for i in range(0, len(self.datasample)):
            if self.datasample[i] > self.valuemax:
                self.valuemax = self.datasample[i]
            
            if self.datasample[i] < self.valuemin:
                self.valuemin = self.datasample[i]
        #
        self.debugprint(1, 'valuemin          ' + str(self.valuemin))
        self.debugprint(1, 'valuemax          ' + str(self.valuemax))
        #
        return True


    def writeoutputfile_P4165(self):
        #
        # Write the data to the file for function generator PeakTech P4165
        #
        self.debugprint(1, "Creating a " + self.functiongenerator + " data file '" + self.outputfile.name + "'")
        
        if self.infilelogicstream:
            zflag_is_set = False
        #
        try:
            with open(self.outputfile.name, "wb") as f:
                bc = 0
                #
                # Write file header
                #
                if self.zflag_is_set:
                    #
                    # The function generator will do an interpolation between samples
                    f.write((''.join(chr(i) for i in [255, 255, 255, 255])).encode('charmap'))
                    #
                    self.debugprint(3, 'interpolate       0xFFFFFFFF')
                    #
                else:
                    #
                    # The function generator will noe do an interpolation between samples
                    f.write((''.join(chr(i) for i in [0, 0, 0, 0])).encode('charmap'))
                    #
                    self.debugprint(3, 'interpolate       0x00000000')
                    #
                bc = bc + 4
                #
                # Save the min and max values
                #
                min_vol = int(round((self.valuemin * 1000.0) + 10000))
                max_vol = int(round((self.valuemax * 1000.0) + 10000))
                #
                if min_vol < 0:
                    min_vol = 0
                #
                if min_vol > int(round((self.maxclipvalue * 1000.0) + 10000)):
                    min_vol = int(round((self.maxclipvalue * 1000.0) + 10000))
                #
                if max_vol < 0:
                    max_vol = 0
                #
                if max_vol > int(round((self.maxclipvalue * 1000.0) + 10000)):
                    max_vol = int(round((self.maxclipvalue * 1000.0) + 10000))
                #
                self.debugprint(3, 'min_vol           ' + str(min_vol))
                self.debugprint(3, 'max_vol           ' + str(max_vol))
                #    
                min_vol_b = min_vol.to_bytes(4, byteorder='little')
                max_vol_b = max_vol.to_bytes(4, byteorder='little')
                #
                f.write((''.join(chr(i) for i in max_vol_b)).encode('charmap'))     # Maximum voltage unit mV
                bc = bc + 4
                f.write((''.join(chr(i) for i in min_vol_b)).encode('charmap'))     # Minimum voltage unit mV
                bc = bc + 4
                #
                # Write how many data points the input file have
                #
                samplecnt = len(self.datasample)
                samplecnt_b = samplecnt.to_bytes(4, byteorder='little')
                #
                if samplecnt >= self.maxsamplepoint:
                    self.normalprint(self.outputtext('To many samples in input file, ') + str(len(self.datasample)) + self.outputtext(', max is ') + str(self.maxsamplepoint))
                    samplecnt = self.maxsamplepoint
                #
                self.debugprint(3, 'samplecnt         ' + str(samplecnt))
                #
                f.write((''.join(chr(i) for i in samplecnt_b)).encode('charmap'))   # Edited data point number
                bc = bc + 4
                #
                # Write File name
                #
                sv_b = list(self.outputfile.name[:31].encode('ascii'))
                #
                f.write((''.join(chr(i) for i in sv_b)).encode('ascii'))   # Edited data point number
                bc = bc + len(sv_b)
                #
                # Padding with zeros
                t = 0
                sv_bb = t.to_bytes(((32 + 4 + 4 + 4 + 4) - bc), byteorder='little')
                f.write((''.join(chr(i) for i in sv_bb)).encode('charmap'))   # Edited data point number
                #
                # Write data points to the output file
                #
                for i in range(0, samplecnt):
                    bb = int(round((self.datasample[i] * 1000.0) + 10000))
                    #
                    if bb < 0:
                        bb = 0
                    #
                    if bb > int(round((self.maxclipvalue * 1000.0) + 10000)):
                        bb = int(round((self.maxclipvalue * 1000.0) + 10000))
                    #
                    self.debugprint(3, 'bb                ' + str(bb))
                    #
                    bb_b = bb.to_bytes(2, byteorder='little')
                    f.write((''.join(chr(i) for i in bb_b)).encode('charmap'))   # Edited data point number

        except IOError as e:
           self.normalprint (self.outputtext("I/O error"), False)
           self.normalprint ("({0}): {1}".format(e.errno, e.strerror))
           return False
        except: #handle other exceptions such as attribute errors
           self.normalprint (self.outputtext("Unexpected error:"), sys.exc_info()[0])
           return False
        #
        #
        return True

    def writeoutputfile(self):
        #
        # Write the data to the file
        #
        if self.functiongenerator == 'P4120' or \
           self.functiongenerator == 'P4121' or \
           self.functiongenerator == 'P4124' or \
           self.functiongenerator == 'P4125' or \
           self.functiongenerator == 'P4165':
            self.writeoutputfile_P4165()
            return True

        self.normalprint(self.outputtext("There is not support for saving data to '") + self.functiongenerator + "'")
        #
        #
        return False
    
    
    def mainloop(self, argv):

        #
        # Set up default values
        #
        #
        if not self.setdefault():
            return 1
        #
        # Check arguments and set up internal variables
        #
        if not self.checkargv(argv[0], argv[1:]):
            return 1
        #
        # Read input file
        #
        if not self.readinputfile():
            return 2
        #
        # Post process input data
        #
        if not self.postprocessdata():
            return 2
        #
        # Write the output file
        #
        if not self.writeoutputfile():
            return 2


if __name__ == "__main__":

    cfg = Convert2FG()
    #
    # Set up default values
    #
    cfg.mainloop(sys.argv)
