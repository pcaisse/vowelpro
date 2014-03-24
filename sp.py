#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave

def get_formant(fft, formant_range, hz_per_x):
    for i in range(0, len(formant_range)):
        formant_range[i] = formant_range[i] / hz_per_x
    return (np.argmax(fft[formant_range[0]:formant_range[1]]) + formant_range[0]) * hz_per_x

def get_vowel_range(wav):

    # Open WAV file
    spf = wave.open(wav, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    f = spf.getframerate()

    max_val = max(signal)
    bucket_size = 500 # 1/32 of a second
    spike_factor = 10

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in xrange(0, len(signal))]

    # Get averages within buckets
    means = [int(np.mean(signal_pos[i:i+bucket_size])) for i in xrange(0, len(signal_pos), bucket_size)]

    # Get spikes
    # TODO: Get only two largest spikes, not first two
    spike_indexes = [i*bucket_size for i in xrange(0, len(means)) if i > 0 and means[i-1]*spike_factor < means[i]][:2] 

    # Get vowel range
    range_between_spikes = spike_indexes[1] - spike_indexes[0]
    one_third_of_range = int(range_between_spikes*1/3)
    vowel_range = [spike_indexes[0] + one_third_of_range, spike_indexes[1] - one_third_of_range]

    # Get vowel index
    vowel_index = spike_indexes[0] + int(range_between_spikes*0.5)

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

get_vowel_range(sys.argv[1])