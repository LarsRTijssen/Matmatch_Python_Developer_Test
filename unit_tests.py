import pandas.testing as pdt
from cleaning import *
#from pytest import expect

# test if standard_unit is accepted by pint

def test_dimensionality():
	'''
	test to see if the dimensions of the material property map are correctly converted to pint units
	'''


	ureg = pint.UnitRegistry()

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
		u1 = pint.Quantity(1, units = d)
		u2 = pint.Quantity(1, units = dc)

		assert u1.dimensionality == u2.dimensionality



def test_cleaning():
	'''
	This test goes through all of the individual steps of cleaning the data and tests each step against an expected output.
	checked output can be found in the unit_tests folder
	'''

	ureg = pint.UnitRegistry()

	folder = "./unit_tests/"

	std_unit = '1/°C'

	# read in initial data
	data = pd.read_csv(folder + "cleaning_input.tsv", delimiter=r"\t+", 
													  dtype = str, 
													  engine='python', 
													  comment='#', 
													  header = None).iloc[:,0]

	data_check = pd.read_csv(folder + "cleaning_expected.tsv", delimiter=r"\t+", 
															   dtype = str, 
															   engine='python', 
															   comment='#', 
															   header = None).iloc[:,0]

	assert data.shape == data_check.shape

	for d,dc in zip(data, data_check):
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
		d = clean_extractions(d, std_unit)
		print('step3 = {}'.format(d.values))

		# operation 4
		d = clean_units(d)
		print('step4 = {}'.format(d.values))

		# operation 5
		d = combine_num_pow(d)
		print('step5 = {}'.format(d.values))

		# operation 6
		d = to_standard_unit(d, std_unit, ureg)
		print('step6 = {}'.format(d.values))

		# operation 7
		d = to_decimal_string(d)
		print('step7 = {}'.format(d.values))

		# operation 8
		d = combine_strings(d)
		print('final = {}'.format(d.values))
		print('expct = {}'.format(dc.values))

		pdt.assert_series_equal(d, dc)

		print('-'*100)
	
	


#