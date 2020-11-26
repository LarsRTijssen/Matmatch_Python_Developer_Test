import argparse
from cleaning import *

def load_data(input_file):
    '''
    Load data
    '''
    
    # define paths
    path = input_file
    
    # read in the ceramic raw data as dataframe
    data_sheet = pd.read_excel(input_file, 
                             'Ceramic_Raw_Data', 
                             header=0, 
                             dtype = str)
    
    # read in the material property map as dataframe and transpose
    unit_sheet = pd.read_excel(input_file, 
                             'material_property_map', 
                             index_col=0, 
                             dtype = str).T

    print('Data succesfully imported')
    
    return data_sheet, unit_sheet


def clean_data(data_sheet, unit_sheet):
    '''
    Clean data using the clean_series function
    '''
    
    # take variable names from prop_map and use it to replace the respective columns in raw_data
    variables_names = unit_sheet.columns
    data_sheet.columns = data_sheet.columns[:4].union(variables_names, sort = False)
    
    # loop over the variables
    for variables_name in variables_names:
        
        # store the individual series of values and unit into variables
        data = data_sheet[variables_name]
        unit = unit_sheet[variables_name].to_list()[0]
    
        # use clean_series function to clean the data and overwrite the original column in data_sheet
        data_sheet[variables_name] = clean_series(data, unit)
        
    print('Data succesfully cleaned')
        
    return data_sheet


def export_data(data_sheet, fileformat):
    '''
    Export data
    '''
    
    output_path = './data_output/data_output.' + fileformat
    
    
    if fileformat == 'xlsx':
        data_sheet.to_excel(output_path, index = False)
    elif fileformat == 'csv':
        data_sheet.to_csv(output_path, index = False)
    elif fileformat == 'json':
        data_sheet.to_json(output_path)
        
    print('Output file created in {}'.format(output_path))


def main():

	parser = argparse.ArgumentParser(description='Clean excel sheet material data')
	parser.add_argument('input_file')
	parser.add_argument('fileformat')

	args = parser.parse_args()

	# set standard formats if argument is missing
	if args.input_file == '':
		args.input_file = "./data_input/data_input.xlsx"

	if args.fileformat == '':
		args.fileformat = "xlsx"

	data, units = load_data(args.input_file)

	data = clean_data(data, units)

	export_data(data, args.fileformat)


if __name__ == "__main__":
	main()