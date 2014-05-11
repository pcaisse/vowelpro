#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import numpy as np
import wave

def get_vowel_range(start_index, end_index, num_segments, which_segment_to_use):

    """
    Get a list with vowel range.
    """

    range_between_spikes = end_index - start_index
    fraction_of_range = int(range_between_spikes / num_segments)
    vowel_x1 = start_index + fraction_of_range * which_segment_to_use
    vowel_x2 = vowel_x1 + fraction_of_range
    return [vowel_x1, vowel_x2]

def get_humps(signal, floor):

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
                hump['end'] = i
                hump_signal = signal[start:i] 
                area = np.trapz(hump_signal)
                hump['area'] = area
                humps.append(hump)

    return sorted(humps, key=lambda k: k['area'], reverse=True) 

def get_hz_per_x(fft):

    """
    Get number of Hertz per x coordinate.
    """

    max_hz = 8000
    return max_hz / float(len(fft))

def get_formant(fft, formant_range):

    """
    Get formant within a certain range.
    """

    hz_per_x = get_hz_per_x(fft)
    for i in range(0, len(formant_range)):
        formant_range[i] = formant_range[i] / hz_per_x
    return (np.argmax(fft[formant_range[0]:formant_range[1]]) + formant_range[0]) * hz_per_x

def get_fft(signal):

    """
    Get signal in terms of frequency (Hz).
    """

    return 10*np.log10(abs(np.fft.rfft(signal)))

def bucket_index_to_sec(index, bucket_size, frame_rate):

    """
    Converts bucket index (index of array whose values have been mapped to buckets) to seconds.
    """

    return index*bucket_size/float(frame_rate)

def rate_vowel(vowel, wav):

    MODEL_VOWEL_DATA = { # Lower F1 = Higher Vowel; Lower F2 = Backer Vowel
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
        'ae': {
            'f1': [709, 669],
            'f2': [1772, 2349],
            'duration': [278, 332],
        },
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
    }

    try:
        vowel_data = MODEL_VOWEL_DATA[vowel]
    except KeyError as e:
        print 'Vowel not recognized.'
        raise SystemExit

    # Open WAV file
    spf = wave.open(wav, 'r')

    # Get WAV file data
    sample_width = spf.getsampwidth() # 2 (bytes)
    frame_rate = spf.getframerate() # 16000 f/s
    
    # Extract raw audio from WAV file
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    f = spf.getframerate()

    bucket_size = 200

    # Get only positive values
    signal_pos = [signal[x] if signal[x] > 0 else 1 for x in range(0, len(signal))]

    # Get maxes within buckets
    maxes = [int(max(signal_pos[i:i+bucket_size])) for i in range(0, len(signal_pos), bucket_size)]

    std = np.std(maxes)
    mean = np.mean(maxes)
    quarter_std = std * 0.25
    print 'Std: %d' % std
    print 'Mean: %d' % mean
    print '0.25 Std: %d' % quarter_std

    # Plot maxes
    plt.subplot(411)
    plt.plot(maxes)
    floor = quarter_std
    humps = get_humps(maxes, floor)
    print humps
    main_hump = humps[0]
    main_vowel_start = bucket_index_to_sec(main_hump['start'], bucket_size, frame_rate)
    main_vowel_end = bucket_index_to_sec(main_hump['end'], bucket_size, frame_rate)
    duration = main_vowel_end - main_vowel_start
    print main_vowel_start
    print main_vowel_end
    print duration
    plt.plot([0, len(maxes)], [floor, floor], 'k-', lw=1, color='red', linestyle='solid')

    # Get vowel range
    signal_main_hump_start = main_hump['start']*bucket_size
    signal_main_hump_end = main_hump['end']*bucket_size
    vowel_range = get_vowel_range(signal_main_hump_start, signal_main_hump_end, 5, 3)

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

    # Plot waveform
    plt.subplot(412)
    plt.plot(signal)

    # Plot vowel range
    max_val = max(signal)

    for index in [signal_main_hump_start, signal_main_hump_end]:
        plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=1, color='green', linestyle='solid')

    for index in vowel_range:
        plt.plot([index, index], [max_val*-1, max_val], 'k-', lw=2, color='red', linestyle='dashed')

    # Plot FFT
    plt.subplot(413)
    hz_per_x = int(get_hz_per_x(fft))
    fft_len = len(fft)
    fft_x = [i*hz_per_x for i in xrange(fft_len)]
    plt.plot(fft_x, fft)

    # Plot spectrogram
    plt.subplot(414)
    spectrogram = plt.specgram(signal, Fs = f, scale_by_freq=True, sides='default')

    plt.show()
    spf.close()

rate_vowel(sys.argv[1], sys.argv[2])
