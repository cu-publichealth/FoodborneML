    var map;
    var sickMin = Number.MAX_VALUE, sickMax = -Number.MAX_VALUE;
    var sickReviewBottomThreshold = 0.5;
    var sickReviewTopThreshold = 1.0;
    var sickRestaurantThreshold = 5;
    var scalingFactor = 3;
    var selectedMarker = null;
    var xhr = null;
    var classification = 'union';
    var allReviewsForSelectedMarker = null;
    var zipSet = new Set();

    var zipFeature = {'feature': null, 'over': false};
    var markers = [];
    var allSickReviews=[];

    var startTime = (new Date(2019, 1, 1)).getTime();
    var endTime = (new Date()).getTime();

    let margin = {top: 10, right: 30, bottom: 30, left: 40},
                width = 450 - margin.left - margin.right,
                height = 100 - margin.top - margin.bottom;
    var dateHistogram = new Histogram('#histogram', margin, height, width, 20, 4);
    var reviewsForHist = [];

    function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          zoom: 11,
          center: new google.maps.LatLng(40.75,-74.00),
            styles: [
              {
                "elementType": "labels",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "administrative",
                "elementType": "geometry",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "administrative.land_parcel",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "administrative.neighborhood",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "poi",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "road",
                "elementType": "labels.icon",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              },
              {
                "featureType": "transit",
                "stylers": [
                  {
                    "visibility": "off"
                  }
                ]
              }
            ]
        });
        loadGeoJson();

        map.data.setStyle(styleFeature);
        map.data.addListener('mouseover', mouseInToRegion);
        map.data.addListener('mouseout', mouseOutOfRegion);

    }

    function deselectMarker(){
      document.getElementById('rest-info-box').style.display = 'none';
        if(selectedMarker != null){
            makeNeutralIcon(selectedMarker);
            selectedMarker = null;
        }
    }

    function openBusinessWindow(){
    let params = {
        business_id: selectedMarker.rest_info.id,
        start_time: startTime,
        end_time: endTime,
        review_bottom_threshold: sickReviewBottomThreshold,
        review_top_threshold: sickReviewTopThreshold
    };
    OpenWindowWithPost("/foodbornemap/restaurant_info", params);
    }

    function OpenWindowWithPost(url, params)
    {
        var form = document.createElement("form");
        form.setAttribute("method", "post");
        form.setAttribute("action", url);
        form.setAttribute("target", '_blank');

        for (var i in params) {
            if (params.hasOwnProperty(i)) {
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = i;
                input.value = params[i];
                form.appendChild(input);
                console.log(input)
            }
        }

        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }

    function changeMap(){
        reviewsForHist = [];
        classification = document.querySelector('input[name="classification"]:checked').value;
        if(xhr)
            xhr.abort();

        console.log(getFormattedDate(new Date(startTime)), getFormattedDate(new Date(endTime)), classification);
        for(var i = 0; i<markers.length; i++){
            if(markers[i] !== selectedMarker)
                markers[i].setMap(null);
        }
        markers = [];
        if(selectedMarker != null){
            markers.push(selectedMarker);
        }
        zipSet = new Set();
        // map.data.forEach(function(feature){
        //     feature.setProperty('sick_score', 0);
        //     feature.setProperty('review_dates', [])
        // })
        loadRestaurants();
    }

    $(function (){
        $("#sick-review-slider").slider({
            range: true,
            min: 0.1,
            max: 1.0,
            step: 0.1,
            values: [sickReviewBottomThreshold, sickReviewTopThreshold],
            slide: function(event, ui){
                 $("#sick-slider-text").text( ui.values[0] + " - " + ui.values[1]);
            },
            change: function(event, ui){
                sickReviewBottomThreshold = ui.values[0];
                sickReviewTopThreshold = ui.values[1];
                changeMap();
            }
        })

        let sliderStartTime = new Date(2019, 1, 1).getTime();

        $("#date-slider").slider({
            range: true,
            min: sliderStartTime / 1000,
            max: endTime / 1000,
            step: 604800,
            values: [startTime / 1000, endTime / 1000],
            slide: function( event, ui ) {
                 $( "#date-slider-text" ).text( getFormattedDate(new Date(ui.values[ 0 ] *1000)) + " - " + getFormattedDate(new Date(ui.values[ 1 ] *1000)));
             },
            change: function(event, ui){
                $( "#date-slider-text" ).text( getFormattedDate(new Date(ui.values[0] *1000)) + " - " + getFormattedDate(new Date(ui.values[1] *1000)));
                startTime = ui.values[0] * 1000;
                endTime = ui.values[1] * 1000;
                changeMap();
            }
        })

         $("#sick-rest-slider").slider({
            min: 1,
            max: 10,
            step: 1,
            value: sickRestaurantThreshold,
            slide: function( event, ui ) {
                 $( "#rest-slider-text" ).text(ui.value);
             },
            change: function(event, ui){
                sickRestaurantThreshold = ui.value;
                changeMap();
            }
        })

        $("#sick-slider-text").text(sickReviewBottomThreshold + " - " + sickReviewTopThreshold);
        $("#date-slider-text").text(getFormattedDate(new Date(startTime)) + " - " + getFormattedDate(new Date(endTime)));
        $("#rest-slider-text").text(sickRestaurantThreshold);

        $("#date-select").on("change", function() {
            var today = new Date();
            let option = this.value;
            var date = new Date();
            $("#date-slider").slider("disable");
            if (option == 'week'){
                date.setDate(today.getDate() - 7);
            }
            else if(option == 'month'){
                date.setMonth(today.getMonth() - 1);
            }
            else if(option == '6month'){
                date.setMonth(today.getMonth() - 6);
            }
            else if(option == 'year'){
                date.setFullYear(today.getFullYear() - 1);
            }
            else{
                $("#date-slider").slider("enable");
                date = new Date(startTime);
            }
            $("#date-slider").slider("values", [date.getTime()/1000, today.getTime()/1000]);
        })

        $("#sort-by-select").on("change", function() {
            let option = this.value;

            if(option == 'date'){
                reviewDisplay.displaySickReviews('reviews', selectedMarker.reviews, 'created');
            }
            else if(option == 'hsan'){
                reviewDisplay.displaySickReviews('reviews', selectedMarker.reviews, 'classification_hsan');
            }
            else{
                reviewDisplay.displaySickReviews('reviews', selectedMarker.reviews, 'classification');
            }
        });

        $('#radio-buttons :input').change(function() {
            changeMap();
        });
    })

    function getFormattedDate(date) {
      var year = date.getFullYear();

      var month = (1 + date.getMonth()).toString();
      month = month.length > 1 ? month : '0' + month;

      var day = date.getDate().toString();
      day = day.length > 1 ? day : '0' + day;

      return month + '/' + day + '/' + year;
    }

    function loadDataFromServer() {
         xhr = $.getJSON("/foodbornemap/get_reviews", function(businesses){
             console.log("started");
             allSickReviews = businesses;
             console.log("ended");
             loadRestaurants();
         }).fail(function (jqxhr, status, error) {
            console.log('error', status, error);
         }
        );
    }

    function loadRestaurants() {
        sickMin = Number.MAX_VALUE;
        sickMax = -Number.MAX_VALUE;
        allSickReviews.forEach(function (business) {
            if (!('lat-long' in business) || (business['lat-long'] == null)) {
                return;
            }
            let latlng = new google.maps.LatLng(business['lat-long'][0],
                business['lat-long'][1]);
            // let feature = map.data.getFeatureById(zip);
            //  if(feature === undefined){
            // // console.log("undefined");
            //  }
            //  else{
            //      feature.getProperty('test');
            //      feature.setProperty('test', 0);
            //  }
            let reviews = [];
            let restReviewDates = [];

            let aboveThreshold = 0;
            for (var i = 0; i < business['reviews'].length; i++) {
                let reviewScore = 0;
                if (classification == 'union') {
                    if ('classification_hsan' in business['reviews'][i]) {
                        reviewScore = Math.max(business['reviews'][i]['classification']['total_score'], business['reviews'][i]['classification_hsan']['total_score']);
                    } else {
                        reviewScore = business['reviews'][i]['classification']['total_score']
                    }
                } else {
                    if (classification === 'classification_hsan' && !('classification_hsan' in business['reviews'][i])) {
                        return;
                    } else {
                        reviewScore = business['reviews'][i][classification]['total_score'];
                    }
                }
                var reviewTime = Date.parse(business['reviews'][i]['created']);

                if (reviewScore < sickReviewBottomThreshold ||
                    reviewScore > sickReviewTopThreshold ||
                    reviewTime < startTime ||
                    reviewTime > endTime) {

                    continue;
                } else {
                    reviews.push(business['reviews'][i]);
                    let reviewDate = new Date(reviewTime)
                    reviewsForHist.push(reviewDate);
                    restReviewDates.push(reviewDate);
                    aboveThreshold += 1;
                }
            }

            if (selectedMarker != null && selectedMarker.rest_info.id == business['_id']) {
                selectedMarker.normal_icon.scale = aboveThreshold / scalingFactor;
                selectedMarker.reviews = reviews;
                selectedMarker.rest_info.total_review_count = business['review_count'];
                selectedMarker.rest_info.rating = business['rating'];
                selectedMarker.sick_score = aboveThreshold;
                updateClickBox(selectedMarker);
                return;
            }

            let feature = map.data.getFeatureById(business['location']['postal_code']);
            if (feature) {
                let zip_sick_count = 0;
                let zipReviewDates = feature.getProperty('review_dates');

                if (zipSet.has(business['location']['postal_code'])) {
                    zip_sick_count = feature.getProperty('sick_score');
                } else {
                    zipSet.add(business['location']['postal_code']);
                    zipReviewDates = [];

                }
                if (zip_sick_count > sickMax) {
                    sickMax = zip_sick_count;
                }
                if (zip_sick_count < sickMin) {
                    sickMin = zip_sick_count;
                }
                feature.setProperty('sick_score', zip_sick_count + aboveThreshold);
                if (zipReviewDates) {
                    feature.setProperty('review_dates', zipReviewDates.concat(restReviewDates));
                } else {
                    feature.setProperty('review_dates', restReviewDates);
                }

            }

            if (aboveThreshold < sickRestaurantThreshold) {
                return;
            }

            var regular_icon = {
                path: google.maps.SymbolPath.CIRCLE,
                scale: aboveThreshold / scalingFactor,
                fillColor: 'blue',
                fillOpacity: 0.3,
                strokeWeight: 1,
                strokeColor: 'grey'
            };

            var marker = new google.maps.Marker({
                map: map,
                normal_icon: regular_icon,
                icon: regular_icon,
                position: latlng,
                sick_score: aboveThreshold,
                reviews: reviews,
                rest_info: {
                    name: business['name'],
                    id: business['_id'],
                    address: business['address'],
                    total_review_count: business['review_count'],
                    url: business['url'],
                    business_url: business['business_url'],
                    rating: business['rating'],
                    phone: business['phone']
                },
                zIndex: 999
            });

            google.maps.event.addListener(marker, 'mouseover', function () {
                updateMouseoverBox('Restaurant Name:', this.rest_info.name, this.sick_score);

                var icon = this.icon;
                icon.scale = this.normal_icon.scale + 3;
                this.setIcon(icon);
            });

            google.maps.event.addListener(marker, 'click', function () {
                updateClickBox(this);
                if (selectedMarker != null) {
                    makeNeutralIcon(selectedMarker);
                }
                selectedMarker = this;
                this.setIcon('https://www.google.com/mapfiles/marker_green.png');
            });

            google.maps.event.addListener(marker, 'mouseout', function () {
                if (zipFeature['over']) {
                    var feature = zipFeature['feature'];
                    var sickScoreString = feature.getProperty('sick_score');
                    updateMouseoverBox('Zip Code:', feature.getProperty('postalcode'), sickScoreString);
                }

                if (selectedMarker !== this) {
                    makeNeutralIcon(this);
                }
            });
            markers.push(marker);
        });
        dateHistogram.changeHistogram(reviewsForHist, new Date(startTime), new Date(endTime));
    }

    function makeNeutralIcon(marker){
        marker.setIcon(marker.normal_icon);
    }
    function loadGeoJson() {
        map.data.loadGeoJson('/foodbornemap/static/nyc_zip_code.geojson', {idPropertyName :'postalcode'});
        google.maps.event.addListenerOnce(map.data, 'addfeature', function() {
        //        loadSickData();
            loadDataFromServer();
    });
    }

    function scaleUp(){
      for(var i =0; i < markers.length; i++){
          var icon = markers[i].normal_icon;
          icon.scale += 2;
          markers[i].normal_icon = icon;
          if(markers[i] !== selectedMarker)
              markers[i].setIcon(icon);
      }
    }

    function updateClickBox(marker){
        var restInfo = marker.rest_info;
        var sickScore = marker.sick_score;
        var box = document.getElementById('rest-info-box');
        box.style.display = 'block';
        document.getElementById('rest-title').href = restInfo.url;
        document.getElementById('rest-title').textContent = restInfo.name;
        document.getElementById('address').textContent = restInfo.address;
        document.getElementById('rest-rating').src = yelpImages.getLargeImgFromRating(restInfo.rating);
        document.getElementById('total-reviews').textContent = restInfo.total_review_count + ' Reviews';
        document.getElementById('rest-website').href = restInfo.business_url;
        document.getElementById('rest-website').textContent = restInfo.business_url;
        document.getElementById('sick-score').textContent = sickScore + ' Sick Reviews (within slider bounds)';
        document.getElementById('phone-number').textContent = formatPhoneNumber(restInfo.phone);

        reviewDisplay.displaySickReviews('reviews', marker.reviews, 'date_created');
    }

    function styleFeature(feature) {
    var normalizedFillOpacity = (feature.getProperty('sick_score') - sickMin) /
        (sickMax-sickMin);
    // normalizedFillOpacity = 1 - normalizedFillOpacity;

    var outlineWeight = 0.5, zIndex = 1;
        if (feature.getProperty('state') === 'hover') {
            outlineWeight = zIndex = 2;
        }

    return {
        strokeWeight: outlineWeight,
        strokeColor: '#fff',
        fillColor: 'red',
        fillOpacity: normalizedFillOpacity,
        zIndex: zIndex
    }

    }

    function updateMouseoverBox(restOrZip, name, sickScore) {
        document.getElementById('mouseover-type').textContent = restOrZip;
        document.getElementById('mouseover-name').textContent = name;
        document.getElementById('sick_score').textContent = sickScore;
    }

    function mouseInToRegion(event) {
        event.feature.setProperty('state', 'hover');
        zipFeature['feature'] = event.feature;
        zipFeature['over'] = true;

        var sickScoreString = event.feature.getProperty('sick_score');
        updateMouseoverBox('Zip Code:', event.feature.getProperty('postalcode'), sickScoreString);
        if(event.feature.getProperty('review_dates')) {
            dateHistogram.changeHistogram(event.feature.getProperty('review_dates'),
                new Date(startTime), new Date(endTime));
        }
    }

    function mouseOutOfRegion(event) {
        event.feature.setProperty('state', 'normal');
        zipFeature['over'] = false;
        dateHistogram.changeHistogram(reviewsForHist,
                new Date(startTime), new Date(endTime));
    }

    function formatPhoneNumber(phone){
      if (!phone){
          return '';
      }
      let cleaned = ('' + phone).replace(/\D/g, '')
      let match = cleaned.match(/^(1|)?(\d{3})(\d{3})(\d{4})$/)
      if (match) {
        var intlCode = (match[1] ? '+1 ' : '')
        return [intlCode, '(', match[2], ') ', match[3], '-', match[4]].join('')
      }
      return null
    }

