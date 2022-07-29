console.log("Question 1 niveau 2")


function initMap() {
  console.log("function initMap!")
  // carte centree sur Paris : 
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: lat_a, lng: long_a },
    zoom: 12,
  });

  console.log(data_to_map)

  markers = []

  for (let coord in data_to_map){
    // itérer sur les anomalies (coordonnées)
    // console.log(data_to_map[coord].split(",")[0])
    my_lat = parseFloat(data_to_map[coord].split(",")[0])
    my_long = parseFloat(data_to_map[coord].split(",")[1])

    marker = new google.maps.Marker({
      position: {lat:my_lat , lng:my_long},
      map: map,
    })

    markers.push(marker)
  }

  new markerClusterer.MarkerClusterer({ markers, map });

}