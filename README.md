# Python Developer Test

This program is designed to import, clean and export a given excel file with material data. It mainly uses `pandas` to read, transform and output the data and uses the python package `pint` to convert between units.


## Instructions

- clone this github repo
	- `git clone https://github.com/LarsRTijssen/Matmatch_Python_Developer_Test`
- Build the Docker image
    - `./build.sh`
- Run the Docker image with optional arguments
    - `./run.sh -i <INPUT_FILE> -f <FORMAT>`

`<INPUT_FILE>` is a location to the input file (default: `./data_input/data_input.xlsx`)\
`<FORMAT>` must either be `csv`, `json` or `xlsx` (default: `xlsx`)


## Structure

The structure of the top level main.py is as follows:

- load data
Loads the data from an excel sheet. This can be either from `data_input.xlsx` or a given location (see Instructions).

- clean_data
Cleans the data from `Ceramic_Raw_Data` and the standard unit from `material_property_map`

- export_data
Export the data to `./data_output` in a certain format that can be chosen.

It is important that the structure of the excel sheet stays intact: New variations and columns can be added but standard unit must be declared on the `material_property_map` excel sheet (basically number of variables on `material_property_map` must match the number of variables on `Ceramic_Raw_Data`).


The bulk of the work is done in clean_data. As the name suggests this cleaning pipeline deals with cleaning the data and is divided into several functions. Each function gives its output to the next function as input.

The following table gives a good overview of the functions.


| Steps | Function name | example | description |
| --- | --- | --- | --- |
| Input | --- | '11 - 13 x 10-6/K for 20C' | --- |
| Step1 | pre_cleaning | '11-13e-6/Kfor20C' | Does some regex replacement cleaning of the initial input |
| Step2 | extract_groups | ['11' nan '-' '13' 'e-6' '/K' 'for' '20' 'C'] | Extract the different groups using regex |
| Step3 | clean_extractions | ['11' '' '-' '13' 'e-6' '/K' 'for' '20' 'C'] | Cleaning up of the new dataframe |
| Step4 | clean_units | ['11' '' '-' '13' 'e-6' '1/K' 'for' '20' 'C'] | Does some regex replacement of the units to make it `pint` compatible |
| Step5 | combine_num_pow | [1.1e-05 'e-6' '-' 1.3e-05 'e-6' '1/K' 'for' '20' 'C'] | Combines number and exponent |
| Step6 | unit_to_standard_unit | [1.1e-05 'e-6' '-' 1.3e-05 'e-6' '1/K' 'for' '20' 'C'] | Converts number between units |
| Step7 | num_to_decimal_string | ['0.000011' 'e-6' '-' '0.000013' 'e-6' '1/K' 'for' '20' 'C'] | Format number into decimal string |
| Final | combine_strings | '0.000011,0.000013;20' | Converts symbols and combines the necessary strings |
| --- | --- | --- | --- |
| Side | clean_standard_units |  | Does some regex replacement cleaning of the units from `material_property_map` to make it `pint` compatible |


`clean_standard_units` is just a side function and the output gets used by some of the functions in the cleaning pipeline.


## Unit Testing

a few functions are present in the `unit_tests.py`. This file is run before `main.py` so tests will always be conducted before the program runs.

 - `test_cleaning`
This is the biggest part of the unit tests. It goes through the cleaning pipeline and prints input/output for every indivual function for every value individually. A list of input and expected data is present in the folder `unit_tests` where I added the data from the excel sheet plus a few more random examples. The point is that by adding new values here you can easily test if a new value will pass the cleaning pipeline, and if not where the error is exactly. If the source data gets bigger this will be a great help to test out new values that might not be cleaned correctly.

- `test_dimensionality`
Small test to check if a unit string is converted correctly and accepted by `pint` as a unit and if the accepted unit matches the expected unit. `pint` can be very picky about which unit to accept and which ones it doesn't and sometimes it misinterprets units. This function is intended to catch that early on.


## Speed

I tested the program with the following input variations on my local pc:

5 rows, 6 variables: `~1.5 s`\
1k rows, 6 variables: `~15 s`\
10k rows, 6 variables: `~30 s`


## Expansion

Ideally I would expand this program with more unit tests and more regex rules to convert if I had more time (and more sample data). Especially the unit tests could have been a bit better defined and expanded. But from the examples I added so far to the unit tests everything seems pretty robust.