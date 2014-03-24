#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave

def get_formants(fft, range_f1, range_f2, hz_per_marker):
    range_f1[0] = range_f1[0]/hz_per_marker
    range_f1[1] = range_f1[1]/hz_per_marker
    range_f2[0] = range_f2[0]/hz_per_marker
    range_f2[1] = range_f2[1]/hz_per_marker
    print range_f1
    print range_f2
    f1 = (np.argmax(fft[range_f1[0]:range_f1[1]]) + range_f1[0]) * hz_per_marker
    f2 = (np.argmax(fft[range_f2[0]:range_f2[1]]) + range_f2[0]) * hz_per_marker
    print fft[range_f2[0]:range_f2[1]]
    print (np.argmax(fft[range_f2[0]:range_f2[1]]) + range_f2[0])
    return [f1, f2]

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

    vowel_signal = signal[vowel_range[0]:vowel_range[len(vowel_range)-1]]

    fft = 10*np.log10(abs(np.fft.rfft(vowel_signal)))

    #fft_smooth = smooth(fft)

    #print peaks(fft, 1000)

    print len(fft)

    hz_per_marker = 8000 / float(len(fft))

    formants = get_formants(fft, [500, 900], [1500, 1900], hz_per_marker)

    print 'f1: '
    print formants[0]
    print 'f2: ' 
    print formants[1]

    plt.clf()
    plt.subplot(211)
    plt.plot(fft)
    # plt.subplot(212)
    # # plt.plot(fft_smooth)
    plt.show()

    #print fft[vowel_index]

    # Plot waveform
    #plt.subplot(211)
    #plt.plot(signal)

    # Plot vowel
    # for index in vowel_range:
    #     plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=3, color='yellow', linestyle='dashed')
    # plt.plot([vowel_index, vowel_index], [max_val*-1, max_val], 'k-', lw=3, color='red', linestyle='solid')

    # Plot FFT
    # plt.subplot(211)
    # plt.plot(fft)

    # # Plot spectrogram
    # plt.subplot(212)
    # spectrogram = plt.specgram(signal, Fs = f, scale_by_freq=True, sides='default')

    # plt.show()
    spf.close()

get_vowel_range(sys.argv[1])