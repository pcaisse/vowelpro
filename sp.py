#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave

def get_peaks_and_valleys(signal):
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
    range_between_spikes = spike_indexes[1] - spike_indexes[0]
    fraction_of_range = int(range_between_spikes / num_segments)
    vowel_x1 = spike_indexes[0] + fraction_of_range
    vowel_x2 = vowel_x1 + (fraction_of_range * which_segment_to_use)
    return [vowel_x1, vowel_x2]

def get_spike_indexes(signal):
    
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

def get_formant(fft, formant_range, hz_per_x):
    for i in range(0, len(formant_range)):
        formant_range[i] = formant_range[i] / hz_per_x
    return (np.argmax(fft[formant_range[0]:formant_range[1]]) + formant_range[0]) * hz_per_x

def rate_vowel(wav):

    # Open WAV file
    spf = wave.open(wav, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000 f/s
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    f = spf.getframerate()

    max_val = max(signal)
    bucket_size = 500 # 1/32 of a second

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in range(0, len(signal))]

    # Get averages within buckets
    means = [int(np.mean(signal_pos[i:i+bucket_size])) for i in range(0, len(signal_pos), bucket_size)]

    spike_indexes = [i*bucket_size for i in get_spike_indexes(means)]

    # Get vowel range
    vowel_range = get_vowel_range(spike_indexes, 5, 1) if len(spike_indexes) == 2 else [spike_indexes[0], spike_indexes[0] + (frame_rate * 0.2)]

    print vowel_range

    # Get vowel index
    vowel_index = vowel_range[0] + ((vowel_range[1] - vowel_range[0]) / 2)

    # Get spectral slice for vowel
    vowel_signal = signal[vowel_range[0]:vowel_range[len(vowel_range)-1]]

    fft = 10*np.log10(abs(np.fft.rfft(vowel_signal)))

    hz_per_x = 8000 / float(len(fft))

    f1 = get_formant(fft, [500, 900], hz_per_x)
    f2 = get_formant(fft, [1500, 1900], hz_per_x)

    print 'f1: '
    print f1
    print 'f2: ' 
    print f2

    # Plot FFT
    plt.subplot(311)
    plt.plot(fft)

    # Plot waveform
    plt.subplot(312)
    plt.plot(signal)

    # Plot vowel
    for index in vowel_range:
        plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=3, color='yellow', linestyle='dashed')
    plt.plot([vowel_index, vowel_index], [max_val*-1, max_val], 'k-', lw=3, color='red', linestyle='solid')

    # # Plot spectrogram
    plt.subplot(313)
    spectrogram = plt.specgram(signal, Fs = f, scale_by_freq=True, sides='default')

    plt.show()
    spf.close()

rate_vowel(sys.argv[1])