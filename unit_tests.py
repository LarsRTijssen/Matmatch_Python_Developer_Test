import pandas.testing as pdt
from cleaning import *
#from pytest import expect

# test if standard_unit is accepted by pint

def test_dimensionality():
	'''
	test to see if the dimensions of the material property map are correctly converted to pint units
	'''
	folder = "./unit_tests/"

	data = pd.read_csv(folder + "unit_conversion_test_input.tsv", delimiter=r"\t+", 
																  dtype = str, 
																  engine='python', 
																  comment='#', 
																  header = None).iloc[:,0]

	data_check = pd.read_csv(folder + "unit_conversion_test_expected.tsv", delimiter=r"\t+", 
																		   dtype = str, 
																		   engine='python', 
																		   comment='#', 
																		   header = None).iloc[:,0]
	
	assert data.shape == data_check.shape

	# correction for empty strings
	data_check = data_check.str.replace('\'\'','', regex=True)

	print(data_check)

	for d, dc in zip(data, data_check):

		d = clean_standard_units(d)

		print(d, dc)

		# check if unit d is accepted by pint (otherwise error)
		u1 = pint.Quantity(1, units = d)
		u2 = pint.Quantity(1, units = dc)

		# check if the accepted unit corresponds to the expected unit
		assert u1.dimensionality == u2.dimensionality



def test_cleaning():
	'''
	This test goes through all of the individual steps of cleaning the data and tests each step against an expected output.
	checked output can be found in the unit_tests folder
	'''

	ureg = pint.UnitRegistry()

	folder = "./unit_tests/"

	# read in initial data
	data = pd.read_csv(folder + "cleaning_input.tsv", delimiter=r"\t+", 
													  dtype = str, 
													  engine='python', 
													  comment='#', 
													  header = None)

	# split data into input series and std_units series
	data_input = data.iloc[:,0] # first column
	std_units = data.iloc[:,1]	# second column

	data_check = pd.read_csv(folder + "cleaning_expected.tsv", delimiter=r"\t+", 
															   dtype = str, 
															   engine='python', 
															   comment='#', 
															   header = None).iloc[:,0]

	assert data_input.shape == data_check.shape

	for d,dc,su in zip(data_input, data_check, std_units):

		# clean standard unit in case su is given as uncleaned, not strictly necessary as units are tested in test_dimensionality
		su = clean_standard_units(su)

		d = pd.Series(d)
		dc = pd.Series(dc)
		print('input = {}'.format(d.values))

		# operation 1
		d = pre_cleaning(d)
		print('step1 = {}'.format(d.values))

		# operation 2
		d = extract_groups(d)
		print('step2 = {}'.format(d.values))

		# operation 3
		d = clean_extractions(d, su)
		print('step3 = {}'.format(d.values))

		# operation 4
		d = clean_units(d)
		print('step4 = {}'.format(d.values))

		# operation 5
		d = combine_num_pow(d)
		print('step5 = {}'.format(d.values))

		# operation 6
		d = unit_to_standard_unit(d, su, ureg)
		print('step6 = {}'.format(d.values))

		# operation 7
		d = num_to_decimal_string(d)
		print('step7 = {}'.format(d.values))

		# operation 8
		d = combine_strings(d)
		print('final = {}'.format(d.values))
		print('expct = {}'.format(dc.values))

		pdt.assert_series_equal(d, dc)

		print('-'*100)