import unittest
from vowelpro.vowel import FORMANTS, get_signal, get_file_type, get_formants, get_f1_f2_f3, calc_percent_off
import wave
import os

MARGIN_FOR_ERROR = 0.2

TEST_DATA = {
	'ae': {
		'filename': 'files/bat.wav',
		'formants': [724.513989, 1788.088160, 2790.161238]
	},
	'i': {
		'filename': 'files/beat.wav',
		'formants': [285.512606, 2486.483767, 3137.150373]
	},
	'I': {
		'filename': 'files/hit.wav',
		'formants': [708.840931, 2331.232971, 3156.306861]
	},
	'u': {
		'filename': 'files/boot.wav',
		'formants': [379.940419, 1390.467196, 2687.619493]
	},
};


def is_close_enough(test_formants, observed_formants):
	"""
	Whether formants are within a certain percentage of Praat estimation.
	"""
	return all(calc_percent_off(test_formant, observed_formant) <= MARGIN_FOR_ERROR for test_formant, observed_formant in zip(test_formants, observed_formants))


def are_vowel_formants_accurate(vowel_str):
	print 'testing vowel {}'.format(vowel_str)
	vowel = TEST_DATA[vowel_str]
	test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), vowel['filename'])
	test_file_type = get_file_type(test_file)
	test_formants = vowel['formants']
	signal, fs = get_signal(test_file, test_file_type)
	formants = get_formants(signal, fs)
	observed_formants = get_f1_f2_f3(formants, FORMANTS['california'][vowel_str])
	print 'test_formants: {}'.format(test_formants)
	print 'observed_formants: {}'.format(observed_formants)
	return is_close_enough(test_formants, observed_formants)


class FormantTests(unittest.TestCase):

    def test_ae(self):
        self.assertTrue(are_vowel_formants_accurate('ae'))

    def test_i(self):
        self.assertTrue(are_vowel_formants_accurate('i'))

    def test_I(self):
        self.assertTrue(are_vowel_formants_accurate('I'))

    def test_u(self):
        self.assertTrue(are_vowel_formants_accurate('u'))

if __name__ == '__main__':
    unittest.main()