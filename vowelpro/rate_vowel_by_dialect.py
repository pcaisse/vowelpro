from vowel import rate_vowel_by_dialect, VOWELS, DIALECTS, FILE_TYPES
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Rate English vowels (score is out of 100).')
    parser.add_argument('file', metavar='f', help='File path to file of word containing vowel to analyze. File type must be one of: %s' % FILE_TYPES.keys())
    parser.add_argument('vowel', metavar='v', help='Vowel to analyze. Must be one of: %s' % VOWELS.keys())
    parser.add_argument('dialect', metavar='d', help='Dialect to compare against. Must be one of: %s' % DIALECTS.keys())
    parser.add_argument('--extra', action='store_true', help='Extra flag for extra output (includes formants and normalized Bark Difference z-values).' )
    parser.add_argument('--graph', action='store_true', help='Graph flag to show graphs (waveform, vowel segmentation, FFT, spectrogram).' )
    
    args = parser.parse_args()
    
    rating = rate_vowel_by_dialect(args.file, args.vowel, args.dialect, args.graph)
    
    if args.extra:
        print rating
    else:
        print rating['score'] 