from vowel import rate_vowel_by_direct_comparison, FILE_TYPES
import argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Rate English vowels (score is out of 100).')
    parser.add_argument('sample_file', metavar='s', help='File path to sample word. File type must be one of: %s' % FILE_TYPES.keys())
    parser.add_argument('model_file', metavar='m', help='File path to model word. File type must be one of: %s' % FILE_TYPES.keys())
    parser.add_argument('--extra', action='store_true', help='Extra flag for extra output (includes formants and normalized Bark Difference z-values).' )
    
    args = parser.parse_args()
    
    rating = rate_vowel_by_direct_comparison(args.sample_file, args.model_file)
    
    if args.extra:
        print rating
    else:
        print rating['score'] 