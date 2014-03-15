#!/usr/bin/env python
import sys
import matplotlib.pyplot as plot
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

    bucket_size = 500
    spike_factor = 10

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in xrange(0, len(signal))]

    # Get averages within buckets
    means = [int(numpy.mean(signal_pos[i:i+bucket_size])) for i in xrange(0, len(signal_pos), bucket_size)]

    print "Means = %.6f, Std = %.6f" % (numpy.mean(means), numpy.std(means))

    explosions = [means[i] for i in xrange(0, len(means)) if i > 0 and means[i-1]*spike_factor < means[i]]

    print means
    print explosions

    plot.plot(means)
    plot.show()
    spf.close()

fil = sys.argv[1]

show_wave_n_spec(fil)