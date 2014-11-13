Vowel Pro
=========

This software helps learners of English and the hearing impaired practice their English vowels.

The web app uses the [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) which currently has limited support. Vowel Pro only works in Chrome and Firefox. Note that the Python script can also be run as a stand-alone file.

Vowel Pro is published under the [GPLv3](http://www.gnu.org/copyleft/gpl.html).

Why vowels?
-----------

There are a couple of reasons. First, [General American English](http://en.wikipedia.org/wiki/General_American) has about a dozen vowel sounds that can be very challanging to master for non-native speakers, yet their accurate realization is crucial to being understood. Second, vowel acoustics are well understood and vowels can be accurately quantified in terms of formants by computer programs. Third, the acoustic analysis performed on the vowel can be mapped directly to articulation. This means that we can not only tell the user how close they are to the model vowel but also provide them with articulatory cues to help them improve.

How does it work?
-----------------

The user is prompted to record a word containing a certain vowel. The vowel is then isolated within the word and an LPC analysis is performed on it to find the vowel formants, or ressonant frequencies. The user's vowel formants are normalized as are the model formants and they are compared to produce a score.

Which English?
--------------

The model formants are taken from adult American English speakers from Southern California. See: 

Hagiwara, Robert. [Dialect variation and formant frequency: The American English vowels revisited](http://scitation.aip.org/content/asa/journal/jasa/102/1/10.1121/1.419712). 1997.

Why are the words so similar?
-----------------------------

All of the words the user is prompted to say are mono-syllabic and have a CVC (consonant-vowel-consonant) structure. The consonants are all [plosives](http://en.wikipedia.org/wiki/Stop_consonant) -- like [p], [b], [t], [d], [k], [g] -- which are caracterized by a burst of air which makes them easier to identify, also making it easier to identify the vowel.  
