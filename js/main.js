var SpeechRec = (function(window) {

    var audioRecorder;
    var recording = false;

    /**
     * Get WAV file.
     */
    function getWav(callback) {
        audioRecorder && audioRecorder.exportWAV(callback);
    }

    return function() {

        this.isRecording = function() {
            return recording;
        }

        /**
         * Start recording.
         */
        this.start = function() {
            if (!audioRecorder) return;
            audioRecorder.clear();
            audioRecorder.record();
            recording = true;
        }

        /**
         * Stop recording.
         */
        this.stop = function(callback) {
            audioRecorder && audioRecorder.stop();
            recording = false;
            getWav(callback);
        }

        /**
         * Attempt to access user's microphone to record audio. 
         */
        this.init = function(successCallback, failureCallback, browserNotSupportedCallback) {

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
                        var audioContext = new AudioContext();
                        var input = audioContext.createMediaStreamSource(stream);
                        input.connect(audioContext.destination);
                        audioRecorder = new Recorder(input, {'workerPath': 'js/recorder/recorderWorker.js'});
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
