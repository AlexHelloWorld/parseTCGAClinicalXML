# parseTCGAClinicalXML.py

> a small python program for parsing TCGA clinical XML files to CSV format table

## Install
* Just download parseTCGAClinicalXML.py and put it in the directory where you want to run it.

## Run
* run from command line
```
python parseTCGAClinicalXML.py 'output.csv' 'input_xml_file_list.txt' 'patient'or'followup'or'survival'

```
replace 'output.csv' with the name you want for your output csv file
'input_xml_file_list.txt' is a text file containing paths to TCGA clinical xml files
use either one of 'patient', 'followup' or 'survival' as the third input variable to output different clinical data of patients.
sample/ directory contains some samples of input and output

* import as a python module and use functions inside parseTCGAClinicalXML.py
