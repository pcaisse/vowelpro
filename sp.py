#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave
import math
from scipy.signal import lfilter, hamming
from scikits.talkbox import lpc



class Signal():

    """
    Signal wrapper.
    """

    def __init__(self, signal, fs, bucket_size=200):
        self.signal = signal
        self.len = len(signal)
        self.fs = fs
        self.bucket_size = bucket_size
        self.total_duration_sec = self.len / float(self.fs)
        self.sec_per_x = self.total_duration_sec / float(self.len)
        self.signal_x = [i * self.sec_per_x for i in xrange(self.len)]


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

        return self.get_vowel_range(main_hump['start'], main_hump['end'], 3, 1)


    def get_main_vowel_signal(self):

        """
        Get main vowel signal.
        """

        main_hump = self.get_humps()[0]
        # Only use middle 1/3 of vowel.
        vowel_range = self.get_main_vowel_range(main_hump)
        vowel_signal = self.signal[vowel_range[0]:vowel_range[len(vowel_range) - 1]]
        return vowel_signal


    def get_hz_per_x(self, fft):

        """
        Get number of Hertz per x coordinate.
        """

        max_hz = self.fs / 2
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
        hz_per_x = int(self.get_hz_per_x(fft))
        fft_len = len(fft)
        fft_x = [i * hz_per_x for i in xrange(fft_len)]
        plt.plot(fft_x, fft)

        # Plot spectrogram
        plt.subplot(414)
        spectrogram = plt.specgram(self.signal, Fs = self.fs, scale_by_freq=True, sides='default')

        plt.show()


def bark_diff(formants):

    """
    Get Bark-converted values (Z) for vowel formants.
    """

    return [26.81 / (1 + 1960 / f) - 0.53 for f in formants]


def get_fft(signal):

    """
    Get signal in terms of frequency (Hz).
    """

    return 20 * np.log10(abs(np.fft.rfft(signal)))


def get_formants(x, fs):

    """
    Estimate formants using LPC.

    See:
    http://www.mathworks.com/help/signal/ug/formant-estimation-with-lpc-coefficients.html
    http://www.phon.ucl.ac.uk/courses/spsci/matlab/lect10.html

    """

    # Get Hamming window.
    N = len(x)
    w = np.hamming(N)

    # Apply window and high pass filter.
    x1 = x * w
    x1 = lfilter([1], [1., 0.63], x1)

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


def rate_vowel(file_path):

    # Read from file.
    spf = wave.open(file_path, 'r')
    fs = spf.getframerate()
    signal = spf.readframes(-1)
    spf.close()

    signal = np.fromstring(signal, 'Int16')
    signal = Signal(signal, fs)
    vowel_signal = signal.get_main_vowel_signal()    

    formants = get_formants(vowel_signal, fs)[1:4]
    z = bark_diff(formants)
    front_back = z[2] - z[1]
    print 'front-back: %f' % front_back
    height = z[2] - z[0]
    print 'height: %f' % height

    signal.plot()
    

rate_vowel(sys.argv[1])

