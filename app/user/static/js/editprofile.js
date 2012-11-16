$(document).ready(function(){

 var submitted = false,
     locNeedsAjaxCheck = false,
     mapWarnTimeout;
     
 function copyDataToHiddenFields() {
    $("#town").val($("#geocodetown").html());
    $("#longitude").val($("#geocodelongitude").html());
    $("#latitude").val($("#geocodelatitude").html());
 }

 function validateForm() {
   var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/,
      email = $.trim($("#id_email").val()),
      allow_email = $("#allow_email").prop("checked");

   if (allow_email) {
      if (!emailRegex.test(email)) {
           setErrorMsg("email", "emailNotValid");
           $("#div_email").addClass("error");
           return false;
      } else if (email.length > 75) {
           setErrorMsg("email", "emailTooLong");
           $("#div_email").addClass("error");
           return false;
      } 
   }
   
   $("#emailerror").hide();
   $("#div_email").removeClass("error");
   
   if (!$("#contact_info_textarea").val().length) {
      setErrorMsg("contact", "contactMeEmpty");
      return false;
   } else if ($("#contact_info_textarea").val().length > 10000) {
      setErrorMsg("contact", "tooMuchInfo");
      return false;
   } else {
      $("#contacterror").hide();
   }

   if (!$("#about_me_textarea").val().length) {
      setErrorMsg("about", "aboutMeEmpty");
      return false;
   } else if ($("#about_me_textarea").val().length > 10000) {
      setErrorMsg("about", "tooMuchInfo");
      return false;
   } else {
      $("#abouterror").hide();
   }

   $("#id_password").val($.trim($("#id_password").val()).toUpperCase().split(' ').join(''));
   if (!$("#id_password").val().length) {
      setErrorMsg("password", "passwordMissing");
      $("#div_password").addClass("error");
      return false;
   } else {
      $("#passworderror").hide();
      $("#div_password").removeClass("error");
   }

   return true;
 }

 $('input, textarea').change(function() {
     window.onbeforeunload = function() {
         if (!submitted) {
            return $("#stayOnPageAlert").html();
         }
     };
 });

 function scrollTo(tab, place) {
    $('#'+tab).click();
    $('html, body').animate({ scrollTop: $("#"+place).offset().top-65 }, 200 );
 }
 
 function setErrorMsg(which, msgid) {
    var tab = which + "_head"
    var place = which + "error"
    var visualErrorId = "#" + place;
    $(visualErrorId).html($("#" + msgid).html());
    $(visualErrorId).show();
    scrollTo(tab, place);
 }

 $("#allow_email").click(function(e) {
    step1NeedsAjaxCheck = true;
    $(".emailline").toggle();
 });
 
 $("#formsubmit").click(function(e) {
   e.preventDefault();
   if (validateForm()) {
      $("#formsubmit").attr('disabled', 'disabled');
      $("#cancellink").addClass('disabled');
      copyDataToHiddenFields();
      submitted = true;
      $("#editform").submit();
   } else {
     return;
   }
 });

 $("#cancellink").click(function(e) {
   submitted = true;
 });

 function hideWithLoading($toHide){
   loadingPosition = $toHide.offset();
   $toHide.css("visibility", "hidden"); // don't want the layout to change - don't use display:none
   $("#loadingGif").css({ "left": loadingPosition.left + "px", "top": loadingPosition.top + "px" }).show();
 }

 function showAfterLoading($toShow){
   $("#loadingGif").hide();
   $toShow.css("visibility", "visible");
 }

 function geocode(address) {
    hideWithLoading($("#map_canvas"));
    $('.tabs a').bind('show', function (e) {
      showAfterLoading($("#map_canvas"));
    });
    var url = 'http://nominatim.openstreeetmap.org/search';
    data = {
       q: address,
       limit: 1,
       addressdetails: 1,
       format: 'json',
    };

    $.getJSON(url, data, function(json, status, request) {
       if(status != "success") {
         $("#locerror").html("Geocode error: " + status);
         $("#locerror").show();
       } else if(!json.length) {
         $("#locerror").html("Geocode error: no results returned");
         $("#locerror").show();
       } else {
         var loc = json[0];
         var longitude = loc['lon'];
         var latitude = loc['lat'];
         var town = loc['display_name'];

         $.global.markers.removeMarker($.global.marker);
         $.global.marker.destroy()

         var lonlat = new OpenLayers.LonLat(
            parseFloat(longitude), parseFloat(latitude));
         var proj = new OpenLayers.Projection("EPSG:4326");
         lonlat.transform(proj, $.global.map.getProjectionObject());
         var marker = new OpenLayers.Marker(
            lonlat, $.global.gold_icon.clone());

         var b = loc['boundingbox'];
         var bounds = new OpenLayers.Bounds(b[0], b[1], b[2], b[3]);
         bounds.transform(proj, $.global.map.getProjectionObject());

         $.global.markers.addMarker(marker);
         $.global.marker = marker;
         $.global.map.setCenter(lonlat);
         $.global.map.zoomTo(10);

         $("#geocodetown").html(town);
         $("#geocodelongitude").html(longitude);
         $("#geocodelatitude").html(latitude);
       }
       $('.tabs a').unbind('show');
       showAfterLoading($("#map_canvas"));
    });
 }

 $("#map_canvas").mousedown(function(e){
    window.clearTimeout(mapWarnTimeout);
    // display little text.
    $("#pointerMoveWarning").css("visibility", "visible");
 }).mouseup(function(){
    window.clearTimeout(mapWarnTimeout);
    mapWarnTimeout = window.setTimeout( hideMapWarn, 2000 );
 }).mouseleave(function(){
    window.clearTimeout(mapWarnTimeout);
    mapWarnTimeout = window.setTimeout( hideMapWarn, 2000 );
 });
 
 function hideMapWarn() {
    $("#pointerMoveWarning").css("visibility", "hidden");
 }
 
 $("#geocodeaddress").keypress(function(e) {
    if(e.keyCode == 13) {
        locNeedsAjaxCheck = true;
        $("#geocodesubmit").click();
    }
 }).change(function() {
    locNeedsAjaxCheck = true;
 });

 $("#geocodesubmit").click(function(e) {
    e.preventDefault();
   if (locNeedsAjaxCheck) {
    $("#locerror").hide();
    var address = $("#geocodeaddress").val();
    geocode(address);
    locNeedsAjaxCheck = false;
   } else { 
    locNeedsAjaxCheck = true; 
   }
 });

 //
 // Reverse geocoding
 //
 var dblClickHandler = function(e) {

   window.onbeforeunload = function() {
      if (!submitted) {
         return $("#stayOnPageAlert").html();
      }
   };
   $("#geocodetown").html("Retrieving location...");
   $("#locerror").hide();

   // get lonlat from double click
   var lonlat = $.global.map.getLonLatFromViewPortPx(e.xy);
   var proj = new OpenLayers.Projection("EPSG:4326");
   var origlon = lonlat.lon;
   var origlat = lonlat.lat;
   lonlat.transform($.global.map.getProjectionObject(), proj);
   var longitude = lonlat.lon;
   var latitude = lonlat.lat;

   // move pointer and map
   $.global.markers.removeMarker($.global.marker);
   $.global.marker.destroy();
   var origlonlat = new OpenLayers.LonLat(origlon, origlat);
   var marker = new OpenLayers.Marker(origlonlat, $.global.gold_icon.clone());
   $.global.markers.addMarker(marker);
   $.global.marker = marker;

   submit_reverse_geocode_request(latitude, longitude);
 };

 var Navigation = new OpenLayers.Control.Navigation({
    defaultDblClick: dblClickHandler
 });

 function submit_reverse_geocode_request(latitude, longitude) {
   var url = 'http://nominatim.openstreetmap.org/reverse';
   var data = {
      lat: latitude,
      lon: longitude,
      format: 'json'
   };
   $.getJSON(url, data, function(json, status, request){
      if (status != "success") {
         $("#locerror").html("Geocode error: " + status);
         $("#locerror").show();
      } else {
         var place = "";
         var address = json['address'];
         if (address) {
            place += address['country'] ? address['country'] : "";
            place = (address['city'] ? address['city'] + ", " : "") + place;
            if (address['city_district']) {
               place = "" + address['city_district'] + ", " + place;
            } else if (address['suburb']){
               place = "" + address['suburb'] + ", " + place;
            }
            place = (address['road'] ? address['road'] + ", " : "") + place;
            if (place === "") {
               for (var key in address) {
                  place += address[key];
               }
            }
         }
         
         if (place === "") {
            place += json["display_name"] ? json["display_name"] : "";
         }
         if (place === "") {
            place += json["error"] ? json["error"] : "";
         }
         
         $("#geocodetown").fadeOut(function (){
            $("#geocodetown").html(place);
            $("#geocodetown").fadeIn();
         });
         $("#geocodelongitude").html(longitude);
         $("#geocodelatitude").html(latitude);
      }
   });
 }


 function twipsyInit(elm) {
   elm.twipsy();
   elm.click(function(e){
      e.preventDefault();
   });
 }

 function replaceCommas(elm) {
   elm.html(elm.html().replace(",", "."));
 }

if(!$.global) {
   $.global = {};
   $.global['Navigation'] = Navigation;
} else {
   $.global.map.addControl(Navigation);
}

$("#loc_head").click(function (){
   showLocationTab();
});
var showLocationTab = function(){
   $("#editloc_tab").attr("style", "");
   showLocationTab = function(){ return; };
};

twipsyInit($("#local-area-info"));
twipsyInit($("#enter-location-info"));
twipsyInit($("#skills-info"));
twipsyInit($("#select-languages-info"));

replaceCommas($("#geocodelatitude"));
replaceCommas($("#geocodelongitude"));

$('.tabs').tabs();
 
submit_reverse_geocode_request(
   parseFloat($("#geocodelatitude").html().replace(",", ".")),
   parseFloat($("#geocodelongitude").html().replace(",", "."))
);

});
