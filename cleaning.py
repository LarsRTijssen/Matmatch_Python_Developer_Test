import numpy as np
import pandas as pd
import pint
import re

def clean_standard_units(std_unit):
    '''
    convert a string with unit to string that the pint package can accept
    input is a string
    output is a string
    '''
    rules = [['√([a-zA-Z]+)',r'\1^(1/2)'],  # convert square root sign to exponent (√m to m^(1/2))  
             ['\[-\]','']]                  # convert dimensionless units to empty string

    for i, o in rules:
        std_unit = re.sub(i, o, std_unit)

    return std_unit

def pre_cleaning(s):
    '''
    initial cleaning of the original dataset, to make things easier for later functions
    variable rules can be extended if more cleaning is needed
    input is a pandas series
    output is a pandas series
    '''


    # list of rules to replace in the data
    rules = [[' ',''],                              # remove whitespaces
             ['([1-9]),',r'\1'],                    # remove comma used as thousand separator
             ['0,','0.'],                           # comma used as decimal separator to dot
             ['[Xx]','*'],                          # multiplier x or X to *
             ['\*10[\^]?(-)?([0-9]+)',r'e\1\2'],    # *10-6,*10^-6,*106 to e-6
             ['([0-9]+)E(-)?([0-9]+)',r'\1e\2\3']]  # E-6 to e-6

    # loop over rules
    for i, o in rules:
        s = s.str.replace(i, o, regex = True)

    return s


def extract_groups(s):
    '''
    this function extracts groups from the original data using regex expressions
    The regex expressions probably need to be tweaked if more data becomes available
    input is a pandas series
    output is a pandas dataframe (!)
    '''

    # define regex groups
    regex_num = '([-+]?[0-9]*[.]?[0-9]+)' # decimal number ex. 10, 1.2, -0.31
    regex_pow = '(e[-]?[0-9]+)'           # power number ex. e6 or e-6
    regex_sep = '(-|to(?=[0-9]))'         # separator in case a range is given
    regex_unit = '(.*?(?=for|at|@|$))'    # detect unit (basically the rest unless assocatiated temp is given)
    regex_sep_at = '(for|at|@)'           # separator in case an associated temp is given
    regex_unit_at = '(.+$)'               # detect unit of associated temp (basically the rest)

    # define extract statement 
    extract_statement = ''.join([
        regex_num,
        regex_pow,'?',
        regex_sep,'?',
        regex_num,'?',
        regex_pow,'?',
        regex_unit,'?',
        regex_sep_at,'?',
        regex_num,'?',
        regex_unit_at,'?'
        ])

    # extract the separate groups
    df = s.str.extract(extract_statement)

    # fill empty units with NaNs (regex_unit generates empty strings if no unit is present)
    df[df == ''] = np.NaN

    return df


def clean_extractions(df, standard_unit):
    '''
    Clean up and homogenize the group extraction dataframe
    input is a pandas dataframe
    output is a pandas dataframe
    '''

    # set groups column names
    extract_colnames = ['num1','pow1','sep','num2','pow2','unit',
                        'sep_asc_temp','num_asc_temp','unit_asc_temp']
    df.columns = extract_colnames

    # fill nans with empty string for string operations
    df = df.fillna('')

    # fill empty units with standard unit
    df.loc[:,'unit'][df['unit'] == ''] = standard_unit

    return df


def clean_units(df):
    '''
    This function exists specifically to clean the units separated in the extraction phase
    The goal is to convert the units to a pint-compatible string
    Very similar to the pre_cleaning function
    input is a pandas dataframe
    output is a pandas dataframe
    '''

    rules = [['^/', '1/'],
             ['[^°]C', '°C'],
             ['/([^-]+)[-]([^-]+)', r'/(\1*\2)'],
             ['mK', '(m*K)'],
             ['([Mm])([Pp])am', r'\1\2a m'],
             ['([a-zA-Z]+)([0-9]+)/([0-9]+)', r'\1^(\2/\3)']]

    # loop over rules
    for i, o in rules:
        df.loc[:,'unit'] = df['unit'].str.replace(i, o, regex = True)

    return df


def combine_num_pow(df):
    '''
    Combine the numbers and powers (num1 + pow1 and optional num2 + pow2)
    input is a pandas dataframe
    output is a pandas dataframe
    '''

    # copy power value from pow2 to pow1 if pow1 is empty and pow2 is not
    df.loc[:,'pow1'][df['pow2'] != ''] = df['pow2']

    # join num and pow together as strings
    df.loc[:,'num1'] = df['num1'] + df['pow1']
    df.loc[:,'num2'] = df['num2'] + df['pow2']

    # convert num1 and num2 to float (empty strings converted to nans)
    df.loc[:,'num1'][df['num1'] == ''] = np.NaN
    df.loc[:,'num2'][df['num2'] == ''] = np.NaN
    df.loc[:,['num1','num2']] = df[['num1','num2']].astype(float)

    return df


def convert_value(_num, _unit, _std_unit, unitreg):
    '''
    convert float with unit to standard unit, using pint. 
    Note ureg.Quantity is defined in clean series, due to computation length issues.
    _num is a float
    _unit is a string
    _standard_unit is a string
    output is a float
    '''
    
    return unitreg.Quantity(_num, units = _unit).to(_std_unit).magnitude


def unit_to_standard_unit(df, standard_unit, unitreg):
    '''
    Convert num1 and num2 from unit to standard_unit
    input is a pandas dataframe
    output is a pandas dataframe
    '''
    
    
    # use function convert_value to convert value from one unit to another
    df['num1'] = df.apply(lambda x: convert_value(x['num1'], x['unit'], standard_unit, unitreg), axis = 1)
    df['num2'] = df.apply(lambda x: convert_value(x['num2'], x['unit'], standard_unit, unitreg), axis = 1)

    return df


def convert_float_num_to_decimal_string(num):
    return "{:.8f}".format(num).rstrip('0').rstrip('.')


def num_to_decimal_string(df):
    '''
    Convert num1 and num2 from float to decimal string
    input is a pandas dataframe
    output is a pandas dataframe
    '''
    # apply function to num1 and num2 
    df.loc[:, ['num1','num2']] = df[['num1','num2']].applymap(convert_float_num_to_decimal_string)

    # convert num1 and num2 nans back to empty strings
    df.loc[:,'num1'][df['num1'] == 'nan'] = ''
    df.loc[:,'num2'][df['num2'] == 'nan'] = ''

    return df


def combine_strings(df):
    '''
    Combine all parts of the string together and reform into a pandas series
    input is a pandas dataframe
    output is a pandas series (!)  
    '''
    # convert all separators to commas
    df.loc[:,'sep'][df['sep'] != ''] = ','

    # convert all sep_asc_temp to semicolons
    df.loc[:,'sep_asc_temp'][df['sep_asc_temp'] != ''] = ';'


    # finally put string together by adding the relevant columns
    s =  df['num1'] +\
         df['sep'] +\
         df['num2'] + \
         df['sep_asc_temp'] +\
         df['num_asc_temp']

    return s


def clean_series(data, standard_unit):
    '''
    clean a pandas series with unclean import
    '''

    # define pint unit regsitry (outside of functions because of long computation issues)
    ureg = pint.UnitRegistry()
    
    # clean standard_unit
    std_unit = clean_standard_units(standard_unit)
    
    # clean data
    data = pre_cleaning(data)
    data = extract_groups(data)
    data = clean_extractions(data, std_unit)
    data = clean_units(data)
    data = combine_num_pow(data)
    data = unit_to_standard_unit(data, std_unit, ureg)
    data = num_to_decimal_string(data)
    data = combine_strings(data)
    
    return data