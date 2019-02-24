# FGFreja
Porting human editable paramter files to function generators internal format

Use switch '-h' to get help texts

`$ python FGFreja -h`


This script convertes paramter files readable by humans and convert them into function generators internal file format
The script is written in python and command line driven.

Usually a function generators internal file format is in binary format and not readable by humans, this means that humans are left to edit the desired wave format in the grapahics editors that is normally release with the function generator.

These graphical editors are usually only point and click interfaces which make it tideous to create a complicated waveforms.

This script read a file with human readable values and convert them into the function generators internal file format.

The parameter file specifiy either a series of analouge values or a stream of 0 and 1 which, in combination with paramters converter the stream into a specific logic level.

## Supported function generators
Currently the script support the following function generators

Manufacture     Model
* PeakTech        P4120
* PeakTech        P4121
* PeakTech        P4124
* PeakTech        P4125
* PeakTech        P4165


To see all options add -h as a script parameter

`$ python FGFreja -h`

# Examples
**Example 1, converting analouge values**

Convert a file with, test_2.txt, with the numbers (analouge values in volt) -25.0 -5 0 5 10 5 0 -5 -10 -5 0 5 5 5 5 0 
to a function generator file targeting PeakTech P4165

`$ python FG_Besel.py -i test_2.txt -f P4165`

This create the file test_2.bin ready to be loaded into the function generator

**Example 2, converting a logic stream**

Convert a file with, test_3.txt, with the logic values 0001010001010
to a function generator file targeting PeakTech P4165 with values adapted for 3.3V logic

`$ python FG_Besel.py -i test_3.txt -f P4165 -j -c CMOS:3.3`


$ python FGFreja.py -h
`FGFreja.py takes an infile with data samples and convert them into a file readable by specific function generators
It can rescale and will clip indata so it is not outside the range of the function generator
The indata can also be an expression of logic values, that is, 00001111 and convert them into analoige values for the function generator
Indata file is a readable text file where the anaolouge values are expressed in voltage and seperated with a distinctive charater

FGFreja.py -i <inputfile> -o <outputfile> -s <split character> -m <max value> -n <min value> -p <scale value> -f <function generator model> -l <language> -d <debug level> -g -z -c <logic level>
if -o is omitted the output file will be at same place as inputfile with ending .bin
if -f <fg> is present, <fg> will define the target function generator, if omitted, P4165 will be used as default
                  valid function generators are P4165, P4120, P4121, P4124, P4125
if -j is present, then the infile be treatead as a stream of logic values, like 000111100
if -m is present, then any value above this value will be cut to <max value>, <max value> is in volt
if -n is present, then any value below this value will be cut to <min value>, <min value> is in volt
if -s is present, then the character <split character> will be used to seperate values in the input file
if -p is present, then input values will be scaled, <scale value> = min, max or a voltage level expressed as a floating point
                  if max, then all values are scaled until the lowest is equal to the function generators minimum value
                  if floating point value, then all values are multiplied with the scale valu but clipped by function generator max and min value
if -l <val> is present, it will define the language used in the output text, valid values are 0 (English), 1 (Svenska)
if -d is present, it will set the level of debug messages printed during execution
if -g is present, it it will list all aviable funktion generators and then exit
if -c <logic level> is present, then <logic level> will split the values into logic level, for example,
                   if <logic level> = TTL then all values above 2.0 Volt will be transfered into 5 Volt and all others 0.0 Volt
                   if <logic level> = ECL then all values above -1.2 Volt will be transfered into 0 volt and all others -2.0 Volt
                   if <logic level> = CMOS:<val> then all values above 2/3 of <val> will be <val> Volt and all others 0.0 Volt
if -z is present, then
                  for PeakTech 4120/4121/4124/4125/4165 the function generator should interpolate between samples
Values in the infile can use both . and , as decimal seperator


The following exmaples takes an input file and adapt it for the function generator P4165

FGFreja.py -i <input file> -s ':' -f "P4165"                   Clip indata if they are out of range, data samples are seperated with a ':'
FGFreja.py -i <input file> -s ':' -c "CMOS 3.3" -f "P4165"     Convert indata to CMOS 3.3 Volt, data samples are seperated with a ':'
FGFreja.py -i <input file> -s ''  -c "CMOS:3.3" -f "P4165" -j  Convert indata to CMOS 3.3 Volt, indata is a stream of 0 and 1, like 000110011, no seperation between values
`



