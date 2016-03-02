function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {

            // Create variables (in this scope) to hold the API and image size
            var jcrop_api,
                boundx,
                boundy,

                // Grab some information about the preview pane
                $preview = $('#preview-pane'),
                $pcnt = $('#preview-pane .preview-container'),
                $pimg = $('#preview-pane .preview-container img'),

                xsize = $pcnt.width(),
                ysize = $pcnt.height();

            function updatePreview(c)
            {
                $('#id_x1').val(c.x);
                $('#id_x2').val(c.x2);
                $('#id_y1').val(c.y);
                $('#id_y2').val(c.y2);

              if (parseInt(c.w) > 0)
              {
                var rx = xsize / c.w;
                var ry = ysize / c.h;
                $pimg.css({
                  width: Math.round(rx * boundx) + 'px',
                  height: Math.round(ry * boundy) + 'px',
                  marginLeft: '-' + Math.round(rx * c.x) + 'px',
                  marginTop: '-' + Math.round(ry * c.y) + 'px'
                });
              }
            };

            $('#jcrop-img').attr('src', e.target.result);
            $('.jcrop-preview').attr('src', e.target.result);
            $('#jcrop-img').Jcrop({
                onChange: updatePreview,
                onSelect: updatePreview,
                aspectRatio: xsize / ysize
            },function(){
                // Use the API to get the real image size
                var bounds = this.getBounds();
                boundx = bounds[0];
                boundy = bounds[1];
                // Store the API in the jcrop_api variable
                jcrop_api = this;

              // Move the preview into the jcrop container for css positioning
                $preview.appendTo(jcrop_api.ui.holder);
            });
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$(function() {
    var jcrop_options = $(".jcropped").data();
//     $('#jcrop-img').Jcrop({onselect: storeCoords, onchange: storeCoords});
    $('.jcropped').change(function(e){
        readURL(this);
    });
});

