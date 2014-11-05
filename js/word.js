var Word = (function(window) {

    "use strict";

    var WORDS = [
        ['i', 'beat', 'peak', 'beak'],      
        ['I', 'bit', 'tick', 'hid'],     
        ['e', 'bait', 'take', 'hate'],     
        ['E', 'bet', 'tech', 'head'],     
        ['ae', 'bat', 'tack', 'had'],
        ['u', 'boot', 'duke', 'hoot'],     
        ['U', 'put', 'took', 'hood'],     
        ['o', 'boat', 'toad', 'goat'],     
        ['a', 'bought', 'talk', 'caught'],     
        ['^', 'but', 'tuck', 'cup'],     
        ['r', 'dirt', 'curb', 'heard']    
    ];
    var vowelIndex, wordIndex;

    return {

        new: function() {
            vowelIndex = Math.floor(WORDS.length * Math.random());
            var vowelData = WORDS[vowelIndex];
            var vowel = vowelData[0];
            wordIndex = Math.floor((vowelData.length - 1) * Math.random()) + 1;
        },

        getVowel: function() {
            return WORDS[vowelIndex][0];
        },

        getWord: function() {
            return WORDS[vowelIndex][wordIndex];
        }
    }

})(window);
