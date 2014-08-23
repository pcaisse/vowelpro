#!/usr/bin/env python
import sys
import numpy
import wave
import math
from scipy.signal import lfilter, hamming
# from audiolazy import lpc
from scikits.talkbox import lpc

"""
Estimate formants using LPC.

See:
http://www.mathworks.com/help/signal/ug/formant-estimation-with-lpc-coefficients.html
http://www.phon.ucl.ac.uk/courses/spsci/matlab/lect10.html

"""

def get_formants(file_path):

    # Read from file.
    spf = wave.open(file_path, 'r')

    # Get file as numpy array.
    x = spf.readframes(-1)
    x = numpy.fromstring(x, 'Int16')

    # Only use middle third of vowel.
    l = len(x)
    third = l / 3
    x = x[third:third + third]

    # Get Hamming window.
    N = len(x)
    w = numpy.hamming(N)

    # Apply window and high pass filter.
    x1 = x * w
    x1 = lfilter([1], [1., 0.63], x1)

    # Get LPC.
    # A = lpc(x, order=8) # Analysis filter
    Fs = spf.getframerate()
    ncoeff = 2 + Fs / 1000
    A, e, k = lpc(x1, ncoeff)

    # Get roots.
    rts = numpy.roots(A)
    rts = [r for r in rts if numpy.imag(r) >= 0]

    # Get angles.
    angz = numpy.arctan2(numpy.imag(rts), numpy.real(rts))

    # Get frequencies.
    frqs = sorted(angz * (Fs / (2 * math.pi)))

    return frqs

print get_formants(sys.argv[1])