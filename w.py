#!/usr/bin/env python
import sys
import math
import wave
import numpy

'''
Notes:
The WAV files from my phone have 16,000 samples per second and 16 bits per sample
'''

def wp(speech):
    spf = wave.open(speech,'r')

    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000

    sound_info = spf.readframes(-1)
    sound_info = numpy.fromstring(sound_info, 'Int16')

    # iterate over sound_info
    chunk_size = 1000 # 1/16 second
    mean = None
    # prev_mean = None
    # start_secs = None
    # end_secs = None

    print "Variance = %.6f, Std = %.6f" % (numpy.var(sound_info), numpy.std(sound_info))

    chunkified_sound_info = []

    for i in xrange(0, len(sound_info), chunk_size):
        chunk = sound_info[i:i+chunk_size]
        s = 0
        for c in chunk:
            s = s + abs(c)
        mean = s / chunk_size
        chunkified_sound_info.append(mean)
        # if mean and prev_mean and mean > prev_mean * 10:
        #     start_secs = i / frame_rate
        #     print "i = %s, mean = %s, prev_mean = %s, start_secs = %.6f" % (i, mean, prev_mean, start_secs)
        # prev_mean = mean

    print chunkified_sound_info

    numpy.set_printoptions(threshold='nan')
    #print sound_info
    f = spf.getframerate()
    spf.close()

fil = sys.argv[1]

wp(fil)