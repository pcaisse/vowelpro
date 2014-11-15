var SpeechRec = (function(window) {

    "use strict";

    var audioRecorder, audioContext;
    var recording = false;

    /**
     * Get WAV file.
     */
    function getWav(callback) {
        audioRecorder && audioRecorder.exportWAV(callback);
    }

    return {

        isRecording: function() {
            return recording;
        },

        download: function(blob) {
            Recorder.forceDownload(blob, "myRecording.wav" );
        },

        /**
         * Start recording.
         */
        start: function() {
            if (!audioRecorder) return;
            audioRecorder.clear();
            audioRecorder.record();
            recording = true;
        },

        /**
         * Stop recording.
         */
        stop: function(callback) {
            audioRecorder && audioRecorder.stop();
            recording = false;
            getWav(callback);
        },

        /**
         * Attempt to access user's microphone to record audio. 
         */
        init: function(successCallback, failureCallback, browserNotSupportedCallback) {

            navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || window.oGetUserMedia || navigator.msGetUserMedia;
            if (navigator.getUserMedia) {
                navigator.getUserMedia(
                    {
                        "audio": {
                            "mandatory": {
                                "googEchoCancellation": "false",
                                "googAutoGainControl": "false",
                                "googNoiseSuppression": "false",
                                "googHighpassFilter": "false"
                            },
                            "optional": []
                        }
                    }, 
                    function(stream) {
                        var AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext || window.oAudioContext || window.msAudioContext;
                        audioContext = new AudioContext();
                        var input = audioContext.createMediaStreamSource(stream);
                        audioRecorder = new Recorder(input, {
                            'workerPath': 'static/js/recorder/recorderWorker.js',
                            'mono': true
                        });
                        successCallback();
                    }, 
                    failureCallback);
            } else {
                // Browser not supported.
                browserNotSupportedCallback();
            }
        }
    }

})(window);
