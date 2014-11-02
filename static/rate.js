$(document).ready(function() {

    $(':file').change(function(){
        var file = this.files[0];
        if (file) {
            name = file.name;
            size = file.size;
            type = file.type;

            if (file.size > 1000000) {
                alert("File is too big");
            } else if (file.type !== 'audio/wav' ) {
                alert("Must be WAV file");
            } else { 
                $(':submit').click(function(){
                    var formData = new FormData();
                    formData.append('file', file);
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
                        success: completeHandler = function(data) {
                            alert(data);
                        },
                        error: errorHandler = function(error) {
                            alert("Error!", error);
                        },
                        // Form data
                        data: formData,
                        enctype: 'multipart/form-data',
                        //Options to tell JQuery not to process data or worry about content-type
                        cache: false,
                        contentType: false,
                        processData: false
                    });
                    return false;
                });
            }
        }
    });

});