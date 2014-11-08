var Word = (function(window) {

    "use strict";

    var WORDS = [
        ['i', 'i', 'beat', 'peak', 'beak'],      
        ['I', '026A', 'bit', 'tick', 'kid'],     
        ['e', 'e', 'bait', 'take', 'cake'],     
        ['E', '025B', 'bet', 'peck', 'pet'],     
        ['ae', '00E6', 'bat', 'tack', 'pad'],
        ['u', 'u', 'boot', 'dupe', 'toot'],     
        ['U', '028A', 'put', 'took', 'could'],     
        ['o', 'o', 'boat', 'toad', 'goat'],     
        ['a', '0254', 'bought', 'talk', 'caught'],     
        ['^', '028C', 'but', 'tuck', 'cup'],     
        ['r', '025D', 'dirt', 'curb', 'bird']    
    ];
    var vowelIndex, wordIndex;

    return {

        new: function() {
            var newIndex; 
            while (!newIndex || newIndex === vowelIndex) {
                newIndex = Math.floor(WORDS.length * Math.random());
            }
            vowelIndex = newIndex;
            var vowelData = WORDS[vowelIndex];
            var vowel = vowelData[0];
            wordIndex = Math.floor((vowelData.length - 2) * Math.random()) + 2;
        },

        getVowel: function() {
            return WORDS[vowelIndex][0];
        },

        getVowelIpa: function() {
            var vowel = this.getVowel();
            var vowelIpa = WORDS[vowelIndex][1];
            if (vowel === vowelIpa) {
                return vowel;
            }
            return '&#x' + vowelIpa + ';';
        },

        getWord: function() {
            return WORDS[vowelIndex][wordIndex];
        }
    }

})(window);
