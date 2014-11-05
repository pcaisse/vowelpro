$(document).ready(function() {

    "use strict";
    
    Word.new();
    
    var recordBtn = document.getElementById('record');
    var scoreElem = document.getElementById('score');
    var wordElem = document.getElementById('word');
    var sexElem = document.getElementById('sex');
    var newWordElem = document.getElementById('new-word');

    showWord();
    
    SpeechRec.init(
        function success() {
            var $recordBtn = $(recordBtn);
            $recordBtn.click(function() {
                if (SpeechRec.isRecording()) {
                    $recordBtn.prop('disabled', true);
                    SpeechRec.stop(function(blob) {
                        var sex = sexElem[sexElem.selectedIndex].value;
                        var vowel = Word.getVowel();
                        rateVowel(blob, sex, vowel, function(score) {
                            $(scoreElem).html(score);
                            $recordBtn.prop('disabled', false);
                            $(recordBtn).html('Record');
                            //SpeechRec.download(blob); 
                        }, function(error) {
                            console.log(error);
                        });
                    });
                } else {
                    SpeechRec.start();
                    $(scoreElem).html('');
                    $(recordBtn).html('Stop')
                }
            });
            $(newWordElem).click(function() {
                Word.new();
                showWord();
            });
        },
        function failure() {
            alert('Error initializing audio recording');
        },
        function browserNotSupported() {
            alert('Your broswer is not supported');
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
        $.ajax({
            url: '/rate',
            type: 'POST',
            success: success,
            error: failure,
            data: formData,
            enctype: 'multipart/form-data',
            cache: false,
            contentType: false,
            processData: false
        });
    }         

});
