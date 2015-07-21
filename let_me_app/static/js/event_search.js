function get_form_radius(){
 form_radius = $('form').find('input[name=radius]').val();
 if (form_radius)
     return parseInt(form_radius);
 return 1000
}


function set_form_geo_point(coordinates){
  data = { "type": "Point", "coordinates": [coordinates.lng, coordinates.lat] };
  $('form').find('input[name=geo_point]').val(JSON.stringify(data));
}


function draw_circle(map, circles, form_geo_value){
    initial_geo_point = $.parseJSON(form_geo_value);
    coords = initial_geo_point['coordinates'];
    circle = L.circle([coords[1], coords[0]], get_form_radius()).addTo(map);
    circles.push(circle);
    map.fitBounds(circle.getBounds());
}

markers = Array();

function draw_markers(map){
    items = $('.event_item');
    items.each(function(x){
        record_id = $(this).data('record_id')
        coords = $(this).data('geo_point');
        marker = L.marker([coords[1], coords[0]], get_form_radius()).addTo(map);
        markers[record_id] = marker;
    });
}


$(function(){
  form_geo_value = $('form').find('input[name=geo_point]').val();

  function map_init_basic (map, options) {
    circles = [];
    if (form_geo_value.length) {
        draw_circle(map, circles, form_geo_value);
        draw_markers(map);
    }

    $('.event_item').closest('article').mouseover(function(){
      for (i in markers){markers[i].setOpacity(0.2);}
      marker = markers[$(this).find('.event_item').data('record_id')];
      marker.setOpacity(1);
    });

    $('form input[name=radius]').change(function(){
      new_value = $(this).val()
      if (new_value.length){
        if (circles.length > 0){
          circle = circles[0];
          circle.setRadius(parseInt(new_value));
          map.fitBounds(circle.getBounds());
        }
      }
    });

    map.on('click', function(e) {
        if (circles.length > 0){
          map.removeLayer(circles.pop());
        };
        circle = L.circle(e.latlng, get_form_radius()).addTo(map);
        set_form_geo_point(e.latlng);
        circles.push(circle);
      }
    );
  };
  window.map_init_basic = map_init_basic;

})
