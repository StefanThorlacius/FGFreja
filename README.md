# FGFreja
Porting human editable paramter files to function generators internal format

Use switch '-h' to get help texts

>python FGFreja.py -h


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

`>python FGFreja -h`

# Examples
**Example 1, converting analouge values**
Convert a file with, test_2.txt, with the numbers (analouge values in volt) -25.0 -5 0 5 10 5 0 -5 -10 -5 0 5 5 5 5 0 
to a function generator file targeting PeakTech P4165

`>python FG_Besel.py -i test_2.txt -f P4165`

This create the file test_2.bin ready to be loaded into the function generator

**Example 2, converting a logic stream**
Convert a file with, test_3.txt, with the logic values 0001010001010
to a function generator file targeting PeakTech P4165 with values adapted for 3.3V logic

`>python FG_Besel.py -i test_3.txt -f P4165 -j -c CMOS:3.3`






