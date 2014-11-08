document.addEventListener('DOMContentLoaded', function() {

    "use strict";
    
    Word.new();
    
    var recordBtn = document.getElementById('record');
    var scoreElem = document.getElementById('score');
    var wordElem = document.getElementById('word');
    var sexElem = document.getElementById('sex');
    var newWordElem = document.getElementById('new-word');
    var errorElem = document.getElementById('error');

    showWord();
    
    SpeechRec.init(
        function success() {
            recordBtn.addEventListener('click', function() {
                if (SpeechRec.isRecording()) {
                    recordBtn.disabled = true;
                    SpeechRec.stop(function(blob) {
                        var sex = sexElem[sexElem.selectedIndex].value;
                        var vowel = Word.getVowel();
                        rateVowel(blob, sex, vowel, function(xhrEvent) {
                            var response = xhrEvent && xhrEvent.target && 
                                    xhrEvent.target.response && JSON.parse(xhrEvent.target.response);
                            if (response.error) {
                                errorElem.innerHTML = response.error;
                            } else {
                                scoreElem.innerHTML = response.score;
                            }
                            recordBtn.disabled = false;
                            recordBtn.innerHTML = 'Record';
                            //SpeechRec.download(blob); 
                        }, function(error) {
                            console.log(error);
                        });
                    });
                } else {
                    SpeechRec.start();
                    scoreElem.innerHTML = '';
                    recordBtn.innerHTML = 'Stop';
                }
            });
            newWordElem.addEventListener('click', function() {
                Word.new();
                showWord();
            });
        },
        function failure() {
            errorElem.innerHTML = 'Error initializing audio recording.';
        },
        function browserNotSupported() {
            errorElem.innerHTML = 'Your broswer is not supported.';
        }
    );

    function showWord() {
        wordElem.innerHTML = Word.getWord();
    }
    
    function rateVowel(blob, sex, vowel, success, failure) {
        var formData = new FormData();
        formData.append('file', blob);
        formData.append('sex', sex);
        formData.append('vowel', vowel);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/rate', true);
        xhr.addEventListener('load', success);
        xhr.addEventListener('error', failure);
        xhr.send(formData);
    }         

});
