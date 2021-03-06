Vowel Pro
=========

This software helps learners of English and the hearing impaired practice their English vowels.

The web app uses the [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) which currently has limited support. **Vowel Pro only works in Chrome and Firefox.**

Note that the Python script can also be run as a stand-alone file from the command line.

License: Vowel Pro is published under the [GPLv3](http://www.gnu.org/copyleft/gpl.html).


Installation
------------

Vowel Pro uses Python 2.7. To install its dependencies, you must first have setuptools and easy_install installed. On Linux, run:

```
sudo apt-get install python-setuptools
```

pip must also be installed. If it is not, run:

```
sudo easy_install pip
```

Then use pip to install virtualenv if needed:

```
sudo pip install virtualenv
```

**NOTE**: scipy requires some other dependencies that are not Python packages, like cython, gcc, gfortran. You must make sure they are installed before proceeding. Please see: http://www.scipy.org/install.html.

Now that we have pip and virtualenv and the other scipy dependencies installed, we can use virtualdev to set up the Python environment for Vowel Pro.

Assuming you are at the root of the project directory:

```
virtualenv env
```

Then:

```
env/bin/pip install -r requirements.txt
```

to install the dependencies. Now that all the necessary packages are in place*, to run:

```
env/bin/supervisord -c supervisord.conf
```

To shutdown:

```
env/bin/supervisorctl shutdown
```

*numpy is a dependency of scipy but they don't always play nice together. If you have issues installing them, try reinstalling them using `env/bin/pip install [package]` in this order: numpy, scipy, scikits.talkbox.


FAQ
---

Why vowels?
-----------

There are a couple of reasons. First, [General American English](http://en.wikipedia.org/wiki/General_American) has about a dozen vowel sounds that can be very challanging to master for non-native speakers, yet their accurate realization is crucial to being understood. Consider the following words, all of which are distinguished by the vowel:

* bit
* beet
* bat
* bet
* but
* boot
* bot

Second, vowel acoustics are well understood and vowels can be accurately quantified in terms of formants by computer programs. Third, the acoustic analysis performed on the vowel can be mapped directly to articulation. This means that we can not only tell the user how close they are to the model vowel but also provide them with articulatory cues to help them improve.

How does it work?
-----------------

The user is prompted to record a word containing a certain vowel. The vowel is then isolated within the word and an LPC analysis is performed on it to find the vowel formants, or ressonant frequencies. The user's vowel formants are normalized as are the model formants and they are compared to produce a score.

Which English?
--------------

The model formants are taken from adult American English speakers from Southern California. See: 

Hagiwara, Robert. [Dialect variation and formant frequency: The American English vowels revisited](http://scitation.aip.org/content/asa/journal/jasa/102/1/10.1121/1.419712). 1997.

Why are the words so similar?
-----------------------------

All of the words the user is prompted to say are mono-syllabic and have a CVC (consonant-vowel-consonant) structure. The consonants are all [plosives](http://en.wikipedia.org/wiki/Stop_consonant) -- like [p], [b], [t], [d], [k], [g] -- sounds that are caracterized by the blockage of airflow through the vocal tract and then a burst of air. This spike in intensity in the waveform makes them easier to identify, and in turn makes the segmentation of the vowel easier. The same types of words were used in the research on which this software is based.
