#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave

def get_peaks_and_valleys(signal):

    """
    Get peaks and valleys from signal as lists.
    """

    currVal, prevVal, nextVal = 0, 0, 0
    peaks, valleys = [], []
    for i in range(1, len(signal)-1):
        currVal = signal[i]
        prevVal = signal[i-1]
        nextVal = signal[i+1]
        if currVal > prevVal and currVal > nextVal:
            peaks.append(i)
        elif currVal < prevVal and currVal < nextVal:
            valleys.append(i)
    return peaks, valleys

def get_vowel_range(spike_indexes, num_segments, which_segment_to_use):

    """
    Get a list with vowel range.
    """

    range_between_spikes = spike_indexes[1] - spike_indexes[0]
    fraction_of_range = int(range_between_spikes / num_segments)
    vowel_x1 = spike_indexes[0] + fraction_of_range
    vowel_x2 = vowel_x1 + (fraction_of_range * which_segment_to_use)
    return [vowel_x1, vowel_x2]

def get_spike_indexes(signal):

    """
    Get indexes of spikes in signal.
    """
    
    spike_indexes = []
    peaks, valleys = get_peaks_and_valleys(signal)

    min_slope = 5
    min_tail = 0.75

    print 'Std: %d' % np.std(signal)
    print 'Mean: %d' % np.mean(signal)

    print peaks
    print valleys

    for i in range(0, len(valleys)):
        x1 = valleys[i]
        if i < len(peaks):
            x2 = peaks[i]
            y1 = signal[x1]
            y2 = signal[x2]
            delta_y = y2-y1
            slope_to_peak = delta_y/(x2-x1)
            if i != len(valleys)-1:
                x3 = valleys[i+1]
                y3 = signal[x3]
                slope_to_next_valley = (y3-y2)/(x3-x2)
                tail_long_enough = y2-y3 > min_tail*delta_y
                spikey_enough = delta_y > np.std(signal)
                if slope_to_peak > min_slope and abs(slope_to_next_valley) > min_slope and tail_long_enough and spikey_enough:
                    spike_indexes.append(x2)
                    print '(%d, %d)' % (x2, y2)

    print spike_indexes

    return spike_indexes

def get_formant(fft, formant_range):

    """
    Get formant within a certain range.
    """

    max_hz = 8000
    hz_per_x = max_hz / float(len(fft))
    for i in range(0, len(formant_range)):
        formant_range[i] = formant_range[i] / hz_per_x
    return (np.argmax(fft[formant_range[0]:formant_range[1]]) + formant_range[0]) * hz_per_x

def get_fft(signal):

    """
    Get signal in terms of frequency (Hz).
    """

    return 10*np.log10(abs(np.fft.rfft(signal)))

def rate_vowel(vowel, wav):

    # MODEL_VOWEL_DATA = { # Lower F1 = Higher Vowel; Lower F2 = Backer Vowel
    #     'ii': [
    #         # Men, Women
    #         [342, 437],   # F1
    #         [2322, 2761], # F2
    #         [243, 306]    # Duration
    #     ], 
    #     'i': [
    #         [427, 483],
    #         [2034, 2365],
    #         [192, 237]
    #     ],
    #     'ee': [
    #         [476, 536,
    #         [2089, 2530],
    #         [267, 320]
    #     ],
    #     'e': [
    #         [580, 731],
    #         [1799, 2058],
    #         [189, 254]
    #     ],
    #     'ae': [
    #         [588, 669],
    #         [1952, 2349],
    #         [278, 332]
    #     ],
    #     'a': [
    #         [768, 936],
    #         [1333, 1551],
    #         [267, 323]
    #     ],
    #     'c': [
    #         [652, 781],
    #         [997, 1136],
    #         [283, 353]
    #     ],
    #     'o': [
    #         [497, 555],
    #         [910, 1035],
    #         [265, 326]
    #     ],
    #     'u': [
    #         [469, 519],
    #         [1122, 1225],
    #         [192, 249]
    #     ],
    #     'uu': [
    #         [378, 459],
    #         [997, 1105],
    #         [237, 303]
    #     ],
    #     'v': [
    #         [623, 753],
    #         [1200, 1426],
    #         [188, 226]
    #     ],
    #     'er': [
    #         [474, 523],
    #         [1379, 1588],
    #         [263, 321]
    #     ]
    # }

    # vowel_data = None

    # try:
    #     vowel_data = MODEL_VOWEL_DATA[vowel]
    # except KeyError as e:
    #     print 'Vowel not recognized.'
    #     raise SystemExit

    # Open WAV file
    spf = wave.open(wav, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000 f/s
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    f = spf.getframerate()

    bucket_size = 500 # 1/32 of a second

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in range(0, len(signal))]

    # Get averages within buckets
    means = [int(np.mean(signal_pos[i:i+bucket_size])) for i in range(0, len(signal_pos), bucket_size)]

    # Plot means
    plt.subplot(411)
    plt.plot(means)

    spike_indexes = [i*bucket_size for i in get_spike_indexes(means)]

    # Get vowel range
    vowel_range = get_vowel_range(spike_indexes, 5, 1) if len(spike_indexes) == 2 else [spike_indexes[0], spike_indexes[0] + (frame_rate * 0.2)]

    print vowel_range

    # Get vowel index
    vowel_index = vowel_range[0] + ((vowel_range[1] - vowel_range[0]) / 2)

    # Get spectral slice for vowel
    vowel_signal = signal[vowel_range[0]:vowel_range[len(vowel_range)-1]]

    fft = get_fft(vowel_signal)

    f1 = get_formant(fft, [500, 900])
    f2 = get_formant(fft, [1500, 1900])

    print 'f1: '
    print f1
    print 'f2: ' 
    print f2

    # Plot FFT
    plt.subplot(412)
    plt.plot(fft)

    # Plot waveform
    plt.subplot(413)
    plt.plot(signal)

    # Plot vowel
    max_val = max(signal)
    for index in vowel_range:
        plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=3, color='yellow', linestyle='dashed')
    plt.plot([vowel_index, vowel_index], [max_val*-1, max_val], 'k-', lw=3, color='red', linestyle='solid')

    # # Plot spectrogram
    plt.subplot(414)
    spectrogram = plt.specgram(signal, Fs = f, scale_by_freq=True, sides='default')

    plt.show()
    spf.close()

rate_vowel(sys.argv[1], sys.argv[2])
