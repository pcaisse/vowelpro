#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy
import wave

def show_wave_n_spec(speech):

    # Open WAV file
    spf = wave.open(speech, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = numpy.fromstring(signal, 'Int16')
    f = spf.getframerate()

    max_val = max(signal)
    bucket_size = 500
    spike_factor = 10

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in xrange(0, len(signal))]

    # Get averages within buckets
    means = [int(numpy.mean(signal_pos[i:i+bucket_size])) for i in xrange(0, len(signal_pos), bucket_size)]

    # Get spikes
    spike_indexes = [i*bucket_size for i in xrange(0, len(means)) if i > 0 and means[i-1]*spike_factor < means[i]]

    print spike_indexes

    # Plot graph
    plt.plot(signal)
    # Plot spikes
    for index in spike_indexes[:2]:
        plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=3, color='red', linestyle='dashed')

    plt.show()
    spf.close()

fil = sys.argv[1]

show_wave_n_spec(fil)