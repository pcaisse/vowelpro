import argparse
import sys
import os.path
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import stats
import scipy.signal
from scipy.signal import lfilter, hamming
from scikits.talkbox import lpc
from pydub import AudioSegment


FILE_TYPES = {
    'wav': 'wav',
    'mp3': 'mp3',
    'ogg': 'ogg'
}


VOWELS = {
    'i': 'Close front unrounded',
    'I': 'Near-close front unrounded',
    'e': 'Close-mid front unrounded',
    'E': 'Open-mid front unrounded',
    'ae': 'Near-open front unrounded',
    'a': 'Open back unrounded',
    'o': 'Close-mid back rounded',
    'U': 'Near-close back rounded',
    'u': 'Close back rounded',
    'O': 'Open-mid back rounded',
    '^': 'Open-mid back unrounded',
    'r': 'Rhotic'    
}


FORMANTS = {
    # [F1, F2, F3]
    # NB: Only the data for male informants is used. Normalization seems to 
    #     entirely account for phisiological differences.
    'california': {
        # See: Dialect variation and formant frequency: The American English vowels revisited
        #      Robert Hagiwara, 1997
        # http://www.docin.com/p-101062744.html
        'i': [291, 2338, 2920],      
        'I': [418, 1807, 2589],     
        'e': [403, 2059, 2690],     
        'E': [529, 1670, 2528],     
        'ae': [685, 1601, 2524],
        'a': [710, 1221, 2405],     
        'o': [437, 1188, 2430],     
        'U': [441, 1366, 2446],     
        'u': [323, 1417, 2399],     
        '^': [574, 1415, 2496],     
        'r': [429, 1362, 1679]     
    },
    'general_american': {
        # See: Control Methods Used in a Study of the Vowels
        #      Peterson & Barney, 1952
        # http://www.coe.montana.edu/ee/rosss/courses/ee578_fall_2008/hw05/petersonbarney_jacoustsocam_1952.pdf
        'i': [270, 2290, 3010],
        'I': [390, 1990, 2550],
        'E': [530, 1840, 2480],
        'ae': [660, 1720, 2410],
        '^': [520, 1190, 2390],
        'a': [730, 1090, 2240],
        'O': [570, 840, 2410],
        'U': [440, 1020, 2240],
        'u': [300, 870, 2240],
        'r': [490, 1350, 1690],
    },
    'michigan': {
        # See: Acoustic Characteristic of American English Vowels
        #      Hillenbrand et al, 1995
        # http://talkingneanderthal.com/HillenbrandGettyClarkWheeler.pdf
        'i': [342, 2322, 3000],      
        'I': [427, 2034, 2684],     
        'e': [476, 2089, 2691],     
        'E': [580, 1799, 2605],     
        'ae': [588, 1952, 2601],
        'a': [768, 1333, 2522],     
        'O': [652, 997, 2538],     
        'o': [497, 910, 2459],     
        'U': [469, 1122, 2434],     
        'u': [378, 997, 2343],     
        '^': [623, 1200, 2550],     
        'r': [474, 1379, 1710],
        'DIPHTHONGS': ['e', 'o'] # Falling diphtongs (/e/ realized as [eI] and /o/ realized as [oU])    
    }
}


class Signal():

    """
    Signal wrapper.
    """

    def __init__(self, signal, fs, bucket_size=200, vowel_slices=5, vowel_slice_index=3):
        self.signal = signal
        self.fs = fs
        self.len = len(signal)
        self.bucket_size = bucket_size
        self.total_duration_sec = self.len / float(self.fs)
        self.sec_per_x = self.total_duration_sec / float(self.len)
        self.signal_x = [i * self.sec_per_x for i in xrange(self.len)]
        self.vowel_slices = vowel_slices
        self.vowel_slice_index = vowel_slice_index


    def get_signal_pos(self):

        """
        Get only positive values for signal.
        """

        return [self.signal[x] if self.signal[x] > 0 else 1 for x in xrange(0, self.len)]


    def get_maxes(self):

        """
        Get max values.
        """

        signal_pos = self.get_signal_pos()
        maxes = [int(max(signal_pos[i:i + self.bucket_size])) for i in xrange(0, len(signal_pos), self.bucket_size)]
        maxes_x = [self.signal_x[i] for i in xrange(0, self.len, self.bucket_size)]

        return maxes_x, maxes


    def get_floor(self, maxes):
        std = np.std(maxes)
        floor = std * 0.25
        return floor


    def get_humps(self):

        """
        Get intensity humps.
        """

        maxes_x, maxes = self.get_maxes()
        floor = self.get_floor(maxes)        

        humps = []
        hump = None

        for i in range(0, len(maxes) - 1):
            max_y1 = maxes[i]
            max_y2 = maxes[i + 1]
            start_hump = max_y1 <= floor and max_y2 > floor
            end_hump = max_y1 > floor and max_y2 < floor
            if start_hump:
                hump = { 'start_index': i, 'start': i * self.bucket_size }
            elif end_hump:
                # Make sure we didn't start already in a hump.
                if hump: 
                    start_index = hump['start_index']
                    hump['start_sec'] = maxes_x[start_index]
                    hump['end'] = i * self.bucket_size
                    hump['end_sec'] = maxes_x[i]
                    hump_signal = maxes[start_index:i] 
                    area = np.trapz(hump_signal)
                    hump['area'] = area
                    del hump['start_index']
                    humps.append(hump)

        return sorted(humps, key=lambda k: k['area'], reverse=True)


    def get_vowel_range(self, start_index, end_index, num_segments, which_segment_to_use):

        """
        Get a list of vowel range (from start index to end index).
        """

        range_between_spikes = end_index - start_index
        fraction_of_range = int(range_between_spikes / num_segments)
        vowel_x1 = start_index + fraction_of_range * which_segment_to_use
        vowel_x2 = vowel_x1 + fraction_of_range
        return [vowel_x1, vowel_x2]


    def get_main_vowel_range(self, main_hump):

        """
        Get vowel range for main hump.
        """

        return self.get_vowel_range(main_hump['start'], main_hump['end'], self.vowel_slices, self.vowel_slice_index)


    def get_main_vowel_signal(self):

        """
        Get main vowel signal.
        """

        humps = self.get_humps()
        if len(humps) == 0:
            raise Exception("No vowel signal detected.")
        main_hump = humps[0]
        # Only use middle 1/3 of vowel.
        vowel_range = self.get_main_vowel_range(main_hump)
        vowel_signal = self.signal[vowel_range[0]:vowel_range[len(vowel_range) - 1]]
        return vowel_signal


    def get_hz_per_x(self, fft, max_hz=None):

        """
        Get number of Hertz per x coordinate.
        """

        max_hz = max_hz or self.fs / 2
        return max_hz / float(len(fft))


    def plot(self):

        """
        Show graphs.
        """

        # Plot maxes
        plt.subplot(411)
        maxes_x, maxes = self.get_maxes()
        plt.plot(maxes_x, maxes)
        floor = self.get_floor(maxes)
        plt.plot([0, self.total_duration_sec], [floor, floor], 'k-', lw=1, color='red', linestyle='solid')

        # Plot waveform
        plt.subplot(412)
        plt.plot(self.signal_x, self.signal)
        max_val = max(self.signal)

        # Plot main hump.
        main_hump = self.get_humps()[0]
        signal_main_hump_start = main_hump['start']
        signal_main_hump_end = main_hump['end']
        for index in [signal_main_hump_start, signal_main_hump_end]:
            signal_x_val = self.signal_x[index]
            plt.plot([signal_x_val, signal_x_val], [max_val*-1, max_val], 'k-', lw=1, color='green', linestyle='solid')

        # Plot vowel range.
        vowel_range = self.get_main_vowel_range(main_hump)
        for index in vowel_range:
            signal_x_val = self.signal_x[index]
            plt.plot([signal_x_val, signal_x_val], [max_val*-1, max_val], 'k-', lw=2, color='red', linestyle='dashed')

        # Plot FFT
        plt.subplot(413) 
        fft = get_fft(self.get_main_vowel_signal())
        hz_per_x = int(self.get_hz_per_x(fft, 8000))
        fft_len = len(fft)
        fft_x = [i * hz_per_x for i in xrange(fft_len)]
        plt.plot(fft_x, fft)

        # Plot spectrogram
        ax = plt.subplot(414)
        Pxx, freqs, bins, im = plt.specgram(self.signal, Fs=self.fs, scale_by_freq=True, sides='default')
        ax.set_ylim(0, 5000)

        # Plot formants every 10 ms.
        step = self.fs / 100
        chunked_formants = get_chunked_formants(self.signal, self.fs, step)
        for i, formants in enumerate(chunked_formants):
            for formant in formants:
                plt.plot(self.signal_x[i * step], formant, marker='o', color='r')

        plt.show()


def bark_diff(formants):

    """
    Get Bark-converted values (Z) for vowel formants.
    """

    return [26.81 / (1 + 1960 / float(f)) - 0.53 for f in formants]


def get_fft(signal):

    """
    Get signal in terms of frequency (Hz).
    """

    return 20 * np.log10(abs(np.fft.rfft(signal)))


def get_chunked_formants(signal, fs, step):

    """
    Find formants every x indexes.
    """

    chunked_formants = []
    
    for index in xrange(0, len(signal), step):
        next_index = index + step
        signal_chunk = signal[index:next_index]
        formants = get_formants(signal_chunk, fs)
        signal_chunk_formants = formants[:3]
        chunked_formants.append(signal_chunk_formants)

    return chunked_formants


def get_formants(x, fs):

    """
    Estimate formants using LPC.

    See:
    http://www.mathworks.com/help/signal/ug/formant-estimation-with-lpc-coefficients.html
    http://www.phon.ucl.ac.uk/courses/spsci/matlab/lect10.html

    """

    # b, a = scipy.signal.butter(5, 1.0, 'low', analog=True)
    # x = scipy.signal.filtfilt(b, a, x)

    if not np.any(x):
        # All zeroes
        return []

    x1 = lfilter([1.], [1., 0.63], x)

    # Get Hamming window.
    # N = len(x)
    # w = np.hamming(N)

    # # Apply window.
    # x1 = x * w

    # Get LPC.
    ncoeff = 2 + fs / 1000
    A, e, k = lpc(x1, ncoeff)

    # Get roots.
    rts = np.roots(A)
    rts = [r for r in rts if np.imag(r) > 0]

    # Get angles.
    angz = np.arctan2(np.imag(rts), np.real(rts))

    # Get frequencies.
    frqs = sorted(angz * (fs / (2 * math.pi)))

    return frqs


def get_rms_diff(a, b):

    """
    Measure the average difference of the curves.

    See: http://programmers.stackexchange.com/questions/100303/correlation-between-two-curves
    """

    rmsdiff = 0
    for (x, y) in zip(a, b):
        rmsdiff += (x - y) ** 2  # NOTE: overflow danger if the vectors are long!
    rmsdiff = math.sqrt(rmsdiff / min(len(a), len(b)))    
    return rmsdiff


def get_f1_f2_f3(sample_formants, model_formants):

    """
    Get [F1, F2, F3] of the sample formants.

    Calculate z-values both assuming F0 was found and assuming it was missed. 
    Compare them to the model and return whichever one is more similar to the model.
    """

    model_z = bark_diff(model_formants)

    sample_formants1 = sample_formants[:3] # Assumes F0 was missed.
    sample_formants2 = sample_formants[1:4] # Assumes F0 was found.
    sample_z1 = bark_diff(sample_formants1) 
    sample_z2 = bark_diff(sample_formants2) 
    
    rms_diff1 = get_rms_diff(sample_z1, model_z)
    rms_diff2 = get_rms_diff(sample_z2, model_z)

    if rms_diff1 < rms_diff2:
        return sample_formants1

    return sample_formants2



def get_dimensions(z_values):

    """
    Get front-back and height dimensions for Bark difference metric.
    """

    def front_back(z):
        return z[2] - z[1]

    def height(z):
        return z[2] - z[0]

    return front_back(z_values), height(z_values)


def calc_percent_off(actual, desired):
    return abs(actual - desired) / float(desired)


def calc_percent_correct(actual, desired):

    """
    Calculate the percent correct.
    """

    # Account for values that overshoot the desired value.
    # eg) 4.8/5.0 and 5.2/5.0 are both equally correct (96%)
    percent_off = calc_percent_off(actual, desired)
    if percent_off >= 1.0:
        # Is 100% off or more.
        return 0
    return 1 - percent_off


def get_vowel_score(sample_z, model_z):

    """
    Return vowel score (0-100) as well as some feedback/tips on their pronunciation.
    """

    sample_front_back, sample_height = get_dimensions(sample_z)
    model_front_back, model_height = get_dimensions(model_z)

    # Calculate percent correct for front-back and height dimensions.
    front_back_per = calc_percent_correct(sample_front_back, model_front_back)
    height_per = calc_percent_correct(sample_height, model_height)

    mean_per = np.mean([front_back_per, height_per])

    total_score = int(mean_per * 100)

    return {
        'score': total_score,
        'z_values': {
            'sample_front_back': sample_front_back,
            'model_front_back': model_front_back,
            'sample_height': sample_height,
            'model_height': model_height
        }
    }


def get_file_ext(filename):
    return filename.split('.').pop()


def get_file_type(vowel_file, file_type=None):
    try:
        # `file` may be a File object or a file path (string) 
        if not file_type:
            file_ext = None

            if type(vowel_file) is str:
                # `file` is file path.
                file_ext = get_file_ext(vowel_file)
            else:
                # `file` is File object.
                file_ext = get_file_ext(vowel_file.name)

            file_type = FILE_TYPES[file_ext]

        return file_type
    except:
        raise Exception('Error determining file type. It may need to be passed explicitly. Must be one of: %s' % FILE_TYPES.keys())


def read_file(vowel_file, file_type):
    # Read signal from file.
    # NB: Needs to be mono. Does not work correctly with stereo.
    try:     

        if file_type == FILE_TYPES['wav']:
            # WAV
            audio = AudioSegment.from_wav(vowel_file)
        elif file_type == FILE_TYPES['mp3']:
            # MP3
            audio = AudioSegment.from_mp3(vowel_file)
        else:
            # OGG
            audio = AudioSegment.from_ogg(vowel_file)

        signal = audio._data
        fs = audio.frame_rate

        return signal, fs

    except Exception as e:
        raise Exception('Error reading signal from file: %s' % e)


def get_signal(vowel_file, file_type):

    signal, fs = read_file(vowel_file, file_type)

    # Truncate to nearest 16.
    signal_len = len(signal)
    signal_len = signal_len - (signal_len % 16)
    signal = signal[:signal_len]

    try:
        signal = np.fromstring(signal, 'Int16')
        return signal, fs
    except ValueError as ve:
        raise Exception('Error converting signal to array: %s' % ve)


def rate_vowel(vowel_file, vowel, dialect, file_type, show_graph=False):

    """
    Rate vowel as compared to model.
    """

    file_type = get_file_type(vowel_file, file_type)

    if not file_type in FILE_TYPES:
        raise Exception('Incorrect file type. Must be one of: %s' % FILE_TYPES.keys())

    if not dialect in FORMANTS:
        raise Exception('Dialect not recognized. Must be one of: %s' % FORMANTS.keys())

    if not dialect in FORMANTS:
        raise Exception('Dialect not recognized. Must be one of: %s' % FORMANTS.keys())

    if not vowel in VOWELS:
        raise Exception('Vowel not recognized. Must be one of: %s' % VOWELS.keys())

    dialect = FORMANTS[dialect]

    if not vowel in dialect:
        raise Exception('Vowel not found in selected dialect. Must be one of: %s' % dialect.keys())

    signal, fs = get_signal(vowel_file, file_type)

    diphthongs = 'DIPHTHONGS' in dialect and dialect['DIPHTHONGS']

    # NB: For falling diphtongs we want to find the formants for the first vowel only.
    kwargs = {}
    if diphthongs and len(diphthongs) > 0 and vowel in diphthongs:
        kwargs = dict(vowel_slice_index=1, vowel_slices=7)

    signal = Signal(signal, fs, **kwargs)
    vowel_signal = signal.get_main_vowel_signal()    

    formants = get_formants(vowel_signal, fs)
    model_formants = dialect[vowel]
    sample_formants = get_f1_f2_f3(formants, model_formants)

    sample_z = bark_diff(sample_formants)
    model_z = bark_diff(model_formants)
    
    if show_graph:
        signal.plot()

    results = get_vowel_score(sample_z, model_z)

    results.update({
        'formants': {
            'model': model_formants,
            'sample': sample_formants
        }
    })

    return results

    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Rate English vowels (score is out of 100).')
    parser.add_argument('file', metavar='f', help='File path to file of word containing vowel to analyze. File type must be one of: %s' % FILE_TYPES.keys())
    parser.add_argument('vowel', metavar='v', help='Vowel to analyze. Must be one of: %s' % VOWELS.keys())
    parser.add_argument('dialect', metavar='d', help='Dialect to compare against. Must be one of: %s' % FORMANTS.keys())
    parser.add_argument('--extra', action='store_true', help='Extra flag for extra output (includes formants and normalized Bark Difference z-values).' )
    parser.add_argument('--graph', action='store_true', help='Graph flag to show graphs (waveform, vowel segmentation, FFT, spectrogram).' )
    
    args = parser.parse_args()
    
    rating = rate_vowel(args.file, args.vowel, args.dialect, None, args.graph)
    
    if args.extra:
        print rating
    else:
        print rating['score'] 

