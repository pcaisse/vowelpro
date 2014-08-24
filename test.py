#!/usr/bin/env python
import sys
import numpy as np
import wave
import math
from scipy.signal import lfilter, hamming
from scikits.talkbox import lpc


BUCKET_SIZE = 200


def bark_diff(formants):

    """
    Get Bark-converted values (Z) for vowel formants.
    """

    return [26.81 / (1 + 1960 / f) - 0.53 for f in formants]


def get_humps(signal, fs):

    """
    Get intensity humps.
    """

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in xrange(0, len(signal))]

    # Get x-values for signal (in terms of seconds)
    signal_len = len(signal)
    total_duration_sec = signal_len / float(fs)
    sec_per_x = total_duration_sec / float(signal_len)
    signal_x = [i * sec_per_x for i in xrange(signal_len)]

    # Get maxes within buckets
    maxes = [int(max(signal_pos[i:i+BUCKET_SIZE])) for i in xrange(0, len(signal_pos), BUCKET_SIZE)]
    maxes_x = [signal_x[i] for i in xrange(0, signal_len, BUCKET_SIZE)]

    std = np.std(maxes)
    floor = std * 0.25

    humps = []
    hump = None

    for i in range(0, len(maxes) - 1):
        y1 = maxes[i]
        y2 = maxes[i + 1]
        start_hump = y1 <= floor and y2 > floor
        end_hump = y1 > floor and y2 < floor
        if start_hump:
            hump = { 'start': i }
        elif end_hump:
            # Make sure we didn't start already in a hump.
            if hump: 
                start = hump['start']
                hump['start_sec'] = maxes_x[start]
                hump['end'] = i
                hump['end_sec'] = maxes_x[i]
                hump_signal = maxes[start:i] 
                area = np.trapz(hump_signal)
                hump['area'] = area
                humps.append(hump)

    return sorted(humps, key=lambda k: k['area'], reverse=True)


def get_vowel_range(start_index, end_index, num_segments, which_segment_to_use):

    """
    Get a list with vowel range.
    """

    range_between_spikes = end_index - start_index
    fraction_of_range = int(range_between_spikes / num_segments)
    vowel_x1 = start_index + fraction_of_range * which_segment_to_use
    vowel_x2 = vowel_x1 + fraction_of_range
    return [vowel_x1, vowel_x2]


def get_formants(x, fs):

    """
    Estimate formants using LPC.

    See:
    http://www.mathworks.com/help/signal/ug/formant-estimation-with-lpc-coefficients.html
    http://www.phon.ucl.ac.uk/courses/spsci/matlab/lect10.html

    """

    # Only use middle third of vowel.
    l = len(x)
    third = l / 3
    x = x[third:third + third]

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

    # Get file as numpy array.
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')

    humps = get_humps(signal, fs)
    main_hump = humps[0]
    signal_main_hump_start = main_hump['start'] * BUCKET_SIZE
    signal_main_hump_end = main_hump['end'] * BUCKET_SIZE
    vowel_range = get_vowel_range(signal_main_hump_start, signal_main_hump_end, 5, 3)
    vowel_signal = signal[vowel_range[0]:vowel_range[len(vowel_range) - 1]]

    formants = get_formants(vowel_signal, fs)[1:4]
    z = bark_diff(formants)
    front_back = z[2] - z[1]
    print 'front-back: %f' % front_back
    height = z[2] - z[0]
    print 'height: %f' % height

    spf.close()


rate_vowel(sys.argv[1])

