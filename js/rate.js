$(document).ready(function() {

    var speechRec = new SpeechRec();
    var recordBtn = document.getElementById('record');
    var scoreElem = document.getElementById('score');
    
    speechRec.init(
        function success() {
            $(recordBtn).click(function() {
                if (speechRec.isRecording()) {
                    $(this).prop('disabled', true);
                    speechRec.stop(function(blob) {
                        rateVowel(blob, function(score) {
                            $(scoreElem).html(score);
                            $(this).prop('disabled', false);
                        }, function(error) {
                            console.log(error);
                        });
                    });
                } else {
                    speechRec.start();
                    $(this).html('Stop')
                }
            }); 
        },
        function failure() {
            alert('Error initializing audio recording');
        },
        function browserNotSupported() {
            alert('Your broswer is not supported');
        }
    );
    
    function rateVowel(blob, success, failure) {
        var formData = new FormData();
        formData.append('file', blob);
        $.ajax({
            url: '/rate',  //server script to process data
            type: 'POST',
            // xhr: function() {  // custom xhr
            //     myXhr = $.ajaxSettings.xhr();
            //     if(myXhr.upload){ // if upload property exists
            //         myXhr.upload.addEventListener('progress', progressHandlingFunction, false); // progressbar
            //     }
            //     return myXhr;
            // },
            // Ajax events
            success: success,
            error: failure,
            // Form data
            data: formData,
            enctype: 'multipart/form-data',
            //Options to tell JQuery not to process data or worry about content-type
            cache: false,
            contentType: false,
            processData: false
        });
    }          

});