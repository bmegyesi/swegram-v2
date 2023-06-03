$('#annotate_form').submit(function (e) {
        $('.ui.dimmer').dimmer({closable: false}).dimmer('show');
        e.preventDefault();
        var fd = new FormData($(this)[0]);
        $.ajax({
            url: url_prefix + '/upload_annotate/',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                console.log(data);

                if (data['error_meta'] != undefined){
                  show_error_msg('Ett fel har hittats i metadatan för följande text: <br>&lt;' + data['error_meta'] + '&gt;<br>Kontrollera metadatan och prova igen.');
                  
                }

                document.getElementById("file_to_annotate").value = "";
                document.getElementById("pasted_text").value = "";
                document.getElementById("choose_file_label").innerHTML = 'Välj fil';
                $('#annotate_submit_label').addClass('disabled');
                $('#annotate_submit_label').removeClass('basic');
                update_sidebar();

                $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
                initialize_semantic();
            },
            error: function(_jqXHR, _textStatus, errorThrown) {
                $('.ui.dimmer').dimmer({closable: false}).dimmer('hide');
                displayMsg = ''
                if (errorThrown) {
                  displayMsg = errorThrown
                }
                show_error_msg('An error occured during upload. Please try again.<br>' + displayMsg)
            }
        });

});


$('#analyze_form').submit(function (e) {
        $('.main.ui.dimmer').dimmer({closable: false}).dimmer('show');
        console.log('upload');
        e.preventDefault();
        var fd = new FormData($(this)[0]);
        $.ajax({
            url: url_prefix + '/upload/',
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function(data){
                if (data['error_meta'] != undefined){
                  show_error_msg('Ett fel har hittats i metadatan för följande text: <br>&lt;' + data['error_meta'] + '&gt;<br>Kontrollera metadatan och prova igen.');

                }
                console.log(data);
                document.getElementById("choose_file_label_analyze").innerHTML = 'Välj fil';
                $('#analyze_submit_label').removeClass('disabled');
                $('#analyze_submit_label').addClass('basic');
                update_sidebar();

                $('.main.ui.dimmer').dimmer({closable: false}).dimmer('hide');
                initialize_semantic();
            },
            error: function(_jqXHR, _textStatus, errorThrown) {
                $('.main.ui.dimmer').dimmer({closable: false}).dimmer('hide');
                displayMsg = ''
                if (errorThrown) {
                  displayMsg = errorThrown
                }
                show_error_msg('An error occured during upload. Please try again.<br>' + displayMsg)
            }
        });

});
