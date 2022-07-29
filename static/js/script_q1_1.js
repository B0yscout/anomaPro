console.log("Question 1 niveau 1")



// function initMap() {

//   console.log("function initMap!")
//   // carte centrÃ©e sur Paris : 
//   map = new google.maps.Map(document.getElementById("map"), {
//     center: { lat: lat_a, lng: long_a },
//     zoom: 12,
//   });

//   console.log(data_to_map)

//   markers = {}
  
//   for (let arr in data_to_map){
//     //loop through ARRONDISSEMENTS
    

//     marker = new google.maps.Marker({
//       position: arrondissements[arr],
//       map: map,
//       label: "Arr"+arr,
//       title: "Arrondissement n° "+ arr,
//       url: arr
//     })

//     // marker.addListener("click", () => {
//     //   infoWindow.close();
//     //   infoWindow.setContent(marker.getTitle());
//     //   infoWindow.open(marker.getMap(), marker);
//     // });


//     for (let year in data_to_map[arr]){
//       // loop through YEARS
      
//       // define color based on YEAR
//       if (year == 2022){
//         var color_fill = "#e75c31" 
//         var color_line = "#e75c31"
//       }
//       else if (year == 2021){
//         var color_fill = "#41c5b8" 
//         var color_line = "#41c5b8"
//       }

//       marker.title = marker.title + "\n" + year +":"+data_to_map[arr][year] + " anomalies"
//       // put a circle which radius is linked to quantity, centered on the ARRONDISSEMENT
//       rond = new google.maps.Circle({
//         center : arrondissements[arr],
//         map: map,
//         title: "Arr. n°" + arr + "/" + year + ":" + data_to_map[arr][year],
//         radius : data_to_map[arr][year]/70,
//         strokeColor: color_line,
//         StrokeOpacity: 0.8,
//         fillColor: color_fill,
//         fillOpacity: 0.5,
//       })

//       google.maps.event.addListener(marker, 'click', function() {
//         window.location.href = this.url;});

//       google.maps.event.addListener(rond,'mouseover',function(){
//         this.getMap().getDiv().setAttribute('title',this.get('title'));});

//       google.maps.event.addListener(rond,'mouseout',function(){
//         this.getMap().getDiv().removeAttribute('title');});
//     }
//   }
// } 




