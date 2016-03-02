$(window).on('map:init', function (e) {
    var detail = e.originalEvent ? e.originalEvent.detail : e.detail;
    var map = detail.map;
    var modal_div = $(map.getContainer()).closest('.inline-map');
    var coords = modal_div.data('geopoint');
    if (coords) {
        var latitude=coords[0], longitude = coords[1];
        L.marker([latitude, longitude]).addTo(map);
        map.panTo(new L.LatLng(latitude, longitude));
    }

    var coords = modal_div.data('geoline');
    if (coords) {
        var pointList = coords.map(function(x){return new L.LatLng(x[0], x[1]);});
        var firstpolyline = new L.polyline(pointList, {
          color: 'red', weight: 2, opacity: 1, smoothFactor: 1
        }).addTo(map);
    }

//           map.panTo(new L.LatLng({{ latitude }}, {{ longitude }}));

    modal_div.closest('.modal').on('shown.bs.modal', function () {
            map.invalidateSize();
    });
});
