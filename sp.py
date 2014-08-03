#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave
from scipy.signal import firwin, lfilter
from xml.dom import minidom
import math
from scipy.ndimage import gaussian_filter1d

DEBUG = True

def print_debug(msg):
    if DEBUG:
        print msg

def get_peaks(signal):

    """
    Get peak indexes and values from signal as list of tuples.
    """

    currVal, prevVal, nextVal = 0, 0, 0
    peaks = []
    for i in range(1, len(signal) - 1):
        currVal = signal[i]
        prevVal = signal[i - 1]
        nextVal = signal[i + 1]
        if currVal > prevVal and currVal > nextVal:
            peaks.append((i, signal[i]))
    return peaks

def load_vowel_data(xml_path, vowel):

    """
    Load vowel formant data from XML file into dict.
    """

    data = {}
    xml = minidom.parse(xml_path)
    formants = xml.getElementsByTagName('formant')
    for f in formants:
        v = f.attributes['vowel'].value
        if vowel == v:
            if vowel not in data.keys():
                data['vowel'] = vowel
            number = f.attributes['number'].value
            data['f' + number] = int(f.childNodes[0].nodeValue)

    return data

def get_vowel_range(start_index, end_index, num_segments, which_segment_to_use):

    """
    Get a list with vowel range.
    """

    range_between_spikes = end_index - start_index
    fraction_of_range = int(range_between_spikes / num_segments)
    vowel_x1 = start_index + fraction_of_range * which_segment_to_use
    vowel_x2 = vowel_x1 + fraction_of_range
    return [vowel_x1, vowel_x2]

def get_humps(signal_x, signal, floor):

    """
    Get intensity humps.
    """
    
    humps = []
    hump = None

    for i in range(0, len(signal)-1):
        y1 = signal[i]
        y2 = signal[i+1]
        start_hump = y1 <= floor and y2 > floor
        end_hump = y1 > floor and y2 < floor
        if start_hump:
            hump = { 'start': i }
        elif end_hump:
            # Make sure we didn't start already in a hump.
            if hump: 
                start = hump['start']
                hump['start_sec'] = signal_x[start]
                hump['end'] = i
                hump['end_sec'] = signal_x[i]
                hump_signal = signal[start:i] 
                area = np.trapz(hump_signal)
                hump['area'] = area
                humps.append(hump)

    return sorted(humps, key=lambda k: k['area'], reverse=True) 

def get_hz_per_x(fft, Fs):

    """
    Get number of Hertz per x coordinate.
    """

    return Fs / float(len(fft))

def get_formants(fft, Fs):

    """
    Get F1 and F2 in signal.
    """

    hz_per_x = get_hz_per_x(fft, Fs)
    peaks = get_peaks(fft)

    print_debug('peaks')
    print_debug(peaks)

    sorted_peaks = sorted(peaks, key=lambda x: x[1], reverse=True)
    print_debug('sorted peaks')
    print_debug(sorted_peaks)

    peak1 = sorted_peaks[0]
    peak2 = sorted_peaks[1]

    f1_index = peak1[0]
    f2_index = peak2[0]
    f1_value = peak1[1]
    f2_value = peak2[1]

    print_debug('index')
    print_debug(f1_index)
    print_debug(f2_index)

    return [
        {
            'index': f1_index,
            'value': f1_index * hz_per_x
        },
        {
            'index': f2_index,
            'value': f2_index * hz_per_x
        }
    ]

def get_fft(signal):

    """
    Get signal in terms of frequency (Hz).
    """

    return 10 * np.log10(abs(np.fft.rfft(signal)))

def get_filtered_fft(fft, N, Fc, Fs):

    """
    Get low pass filtered signal.
    """

    h = firwin(numtaps=N, cutoff=Fc, nyq=Fs/2)
    return lfilter(h, 1.0, fft)

def get_moving_avg(interval, window_size):

    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

def get_vowel_rating(f1, f2, vowel_data):

    """
    Get 1-10 rating for vowel (10 = best, 1 = worst).
    """

    #rate = lambda x: math.log(x) + 10
    rate = lambda x: 10 * math.pow(x, 2)
    percent_off = lambda target, actual: math.fabs(target / float(actual) - 1)
    
    f1_percent_off, f2_percent_off = percent_off(vowel_data['f1'], f1), percent_off(vowel_data['f2'], f2) 
    total_percent_off = f1_percent_off + f2_percent_off
    print_debug('total percent off: %f' % total_percent_off)

    rating = int(round(rate(1 - total_percent_off)))
    return rating if rating > 0 else 1

def rate_vowel(vowel, wav):

    try:
        vowel_data = load_vowel_data('formants.xml', vowel)
        print_debug(vowel_data)
    except KeyError as e:
        print_debug('Vowel not recognized.')
        raise SystemExit

    # Open WAV file
    spf = wave.open(wav, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000 f/s
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    Fs = spf.getframerate()

    bucket_size = 200

    # Get x-values for signal (in terms of seconds)
    signal_len = len(signal)
    total_duration_sec = signal_len / float(frame_rate)
    sec_per_x = total_duration_sec / float(signal_len)
    signal_x = [i * sec_per_x for i in xrange(signal_len)]

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in xrange(0, len(signal))]

    # Get maxes within buckets
    maxes = [int(max(signal_pos[i:i+bucket_size])) for i in xrange(0, len(signal_pos), bucket_size)]
    maxes_x = [signal_x[i] for i in xrange(0, signal_len, bucket_size)]

    std = np.std(maxes)
    mean = np.mean(maxes)
    quarter_std = std * 0.25
    print_debug('Std: %d' % std)
    print_debug('Mean: %d' % mean)
    print_debug('0.25 Std: %d' % quarter_std)

    # Plot maxes
    plt.subplot(511)
    plt.plot(maxes_x, maxes)
    floor = quarter_std
    humps = get_humps(maxes_x, maxes, floor)
    main_hump = humps[0]
    main_vowel_start_sec = main_hump['start_sec']
    main_vowel_end_sec = main_hump['end_sec'] 
    duration = main_vowel_end_sec - main_vowel_start_sec
    print_debug(main_vowel_start_sec)
    print_debug(main_vowel_end_sec)
    print_debug(duration)
    plt.plot([0, total_duration_sec], [floor, floor], 'k-', lw=1, color='red', linestyle='solid')

    # Get vowel range
    signal_main_hump_start = main_hump['start']*bucket_size
    signal_main_hump_end = main_hump['end']*bucket_size
    vowel_range = get_vowel_range(signal_main_hump_start, signal_main_hump_end, 5, 3)

    print_debug(vowel_range)

    # Get vowel index
    vowel_index = vowel_range[0] + ((vowel_range[1] - vowel_range[0]) / 2)

    # Get spectral slice for vowel
    vowel_signal = signal[vowel_range[0]:vowel_range[len(vowel_range)-1]]

    fft = get_fft(vowel_signal)
    #fft_filtered = get_moving_avg(fft, 10)
    fft_filtered = get_filtered_fft(fft, 8, 40, Fs)

    f1, f2 = get_formants(fft_filtered, Fs)

    print_debug('f1: ')
    print_debug(f1['value'])
    print_debug('f2: ' )
    print_debug(f2['value'])

    rating = get_vowel_rating(f1['value'], f2['value'], vowel_data)
    print_debug('rating: ')
    print_debug('%s/10' % rating)

    # Plot waveform
    plt.subplot(512)
    plt.plot(signal_x, signal)

    max_val = max(signal)

    # Plot main hump
    for index in [signal_main_hump_start, signal_main_hump_end]:
        signal_x_val = signal_x[index]
        plt.plot([signal_x_val, signal_x_val], [max_val*-1, max_val], 'k-', lw=1, color='green', linestyle='solid')

    # Plot vowel range
    for index in vowel_range:
        signal_x_val = signal_x[index]
        plt.plot([signal_x_val, signal_x_val], [max_val*-1, max_val], 'k-', lw=2, color='red', linestyle='dashed')

    # Plot FFT
    plt.subplot(513) 
    hz_per_x = int(get_hz_per_x(fft, Fs))
    fft_len = len(fft)
    fft_x = [i * hz_per_x for i in xrange(fft_len)]
    plt.plot(fft_x, fft)

    # Plot filtered FFT
    plt.subplot(514)
    plt.plot(fft_x, fft_filtered)

    # Plot formants
    for formant in [f1, f2]:
        plt.plot(formant['value'], fft[formant['index']], marker='o', color='r')

    # Plot spectrogram
    plt.subplot(515)
    spectrogram = plt.specgram(signal, Fs = Fs, scale_by_freq=True, sides='default')

    plt.show()
    spf.close()

rate_vowel(sys.argv[1], sys.argv[2])
