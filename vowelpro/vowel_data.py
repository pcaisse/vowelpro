from vowel import get_vowel_data_from_file_or_dir, FILE_TYPES
import argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Get formants and/or normalized dimensions for word(s) in file or directory.')
    parser.add_argument('file', metavar='f', help='Path to file or directory. File type(s) must be one of: %s' % FILE_TYPES.keys())
    
    args = parser.parse_args()
    
    formants, dimensions = get_vowel_data_from_file_or_dir(args.file)

    print "formants: %s" % formants
    print "dimensions: %s" % dimensions
