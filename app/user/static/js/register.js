$(document).ready(function(){

 $("#id_captcha_1").attr("autocomplete","off");

 var emailRegex,
     step5NeedsAjaxCheck,
     step2NeedsAjaxCheck,
     loadingPosition,
     submitted,
     data,
     mapWarnTimeout;
     
 emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;  
 //
 // validation
 //
 step5NeedsAjaxCheck = true;
 step2NeedsAjaxCheck = false;

 function validateStep5() {

    var email = $.trim($("#step5email").val()),
        allow_email = $("#allow_email").prop("checked"),
        captchaid,
        captchatext,
        captchadata, 
        retVal;

    if (allow_email) {
       if (!emailRegex.test(email)) {
           setErrorMsg("emailNotValid");
           return false;
       }
       if (email.length > 75) {
           setErrorMsg("emailTooLong");
           return false;
       }
    }

    var nocaptcha = $("#ignorecaptcha");
    if (nocaptcha) {
        if (nocaptcha.prop("checked")) {
            return true;
        }
    }

    captchaid = $("#id_captcha_0").val();
    captchatext = $("#id_captcha_1").val();
    captchadata = {
        captchaid : captchaid,
        captchatext : captchatext
    };
    retVal = false;
    
    if (step5NeedsAjaxCheck) {
        $("#refreshCaptcha").hide();
        $.ajax({
            url: "/user/validateCaptcha",
            data: captchadata,
            async: false,
            success: function(response) {
                if (response == "win") {
                   retVal = true;
                   step1NeedsAjaxCheck = false;
                } else {
                    setErrorMsg("captchaFailed");
                    $("#captcha").html($("#loadingGif").html());
                    $.get("/user/getNewCaptcha", function (result){
                        $("#captcha").html(result);
                        $("img.captcha").css({"62":"heightpx","width":"200px"});
                    });
                }
            }
        });
        $("#refreshCaptcha").show();
    } else {
        retVal = true;
    }

    return retVal;
 }

 function validateStep1() {
   return true;
 }

 function validateStep2() {
   return true;
 }

 function validateStep3() {

   if (!$("#contact_info_textarea").val().length) {
      setErrorMsg("contactMeEmpty");
      return false;
   }

   if (!$("#about_me_textarea").val().length) {
      setErrorMsg("aboutMeEmpty");
      return false;
   }

   if ($("#about_me_textarea").val().length > 10000 || $("#contact_info_textarea").val().length > 10000) {
      setErrorMsg("tooMuchInfo");
      return false;
   }

   return true;
 }

 function validateStep4() {
    
  return true;
 }
 //
 // page control
 //

 $('input').change(function() {
    if($(this).val() != "") {
        window.onbeforeunload = function() {
            if (!submitted) {
               return $("#stayOnPageAlert").html();
            }
        };
    }
 });

 function scrollToTop(where) {
    $('html, body').animate({ scrollTop: $(where).offset().top -58 }, 200 );
 }
 
 function setErrorMsg(msgid) {
    var visualErrorId = "#step" + getStep() + "error";
    $(visualErrorId).html($("#" + msgid).html());
    $(visualErrorId).show();
    scrollToTop(visualErrorId);
 }

 function showPleaseWait(){
    $("#pleaseWait").show();
 }
 function showStepTwo() {
    $("#step2").hide();
    $("#step2").attr("style", "");
    $("#step2").fadeIn(400);
    var address = $("#geocodetown").html();
    geocode(address);
 }
 
 function getStep() {
    return $("#step").val();
 }

 function setStep(step) {
    $("#step").val(step);
 }

 $("#step5email").change(function() {
    step1NeedsAjaxCheck = true;
 });

 $("#id_captcha_1").change(function() {
    step1NeedsAjaxCheck = true;
 });

 $("#refreshCaptcha").click(function(e) {
    e.preventDefault();
    step5NeedsAjaxCheck = true;
    $("#captcha").html($("#loadingGif").html());
    $.get("/user/getNewCaptcha", function (result){
        $("#captcha").html(result);
        $("img.captcha").css({"62":"heightpx","width":"200px"});
    });
 });

 $("#allow_email").click(function(e) {
    step5NeedsAjaxCheck = true;
    $(".emailline").toggle();
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

 $("#step5submit").click(function(e) {
    e.preventDefault();
    if (getStep() != "5") {
      return;
    }
    hideWithLoading($(this));
    if (validateStep5()) {
      $("#step5error").hide();
      $("#step5email").val($.trim($("#step5email").val()));
      submitForm("5");
    } else {
      $("#step5error").hide();
      $("#step5error").fadeIn(50);
    }
    showAfterLoading($(this));
 });

 $("#step1submit").click(function(e) {
    e.preventDefault();
    if (getStep() != "1") {
      return;
    }
    hideWithLoading($(this));
    if (validateStep1()) {
       $("#step1").fadeOut(400, function(){
          showStepTwo();
       });
       setStep("2");
    } else {
      $("#step1error").show();
    }
    showAfterLoading($(this));
 });

 function geocodeAddressFocussed(it){
   it.val("");
   geocodeAddressFocussed = function () { return true; };
 };

 $("#geocodeaddress").focus(function (e){
   geocodeAddressFocussed($(this));
 });

 $("#step2yes").click(function(e) {
   e.preventDefault();
   if (getStep() != "2") {
     return;
   }
   showAfterLoading($("#map_canvas"));
   hideWithLoading($(this));
   if (validateStep2()) {
      $("#step2").fadeOut(400, function(){
         $("#step3").fadeIn(400);
         $("#step2yesno").hide();
         $("#step2control").show();
         $("#step2submit").show();
      });
     setStep("3");
   } else {
     $("#step2error").show();
   }
   showAfterLoading($(this));
 });

 $("#step2submit").click(function(e) {
   e.preventDefault();
   if (getStep() != "2") {
     return;
   }
   showAfterLoading($("#map_canvas"));
   hideWithLoading($(this));
   if (validateStep2()) {
      $("#step2").fadeOut(400, function(){
         $("#step3").fadeIn(400);
      });
     setStep("3");
   } else {
     $("#step2error").show();
   }
   showAfterLoading($(this));
 });

 $("#step2no").click(function(e) {
    e.preventDefault();
    $("#step2yesno").fadeOut(400, function() {
       $("#step2control").fadeIn(400);
       $("#step2submit").fadeIn(400);
    });
 });

function geocode(address) {
    hideWithLoading($("#map_canvas"));
    var url = 'http://nominatim.openstreetmap.org/search';
    data = {
        q: address,
        limit: 1,
        addressdetails: 1,
        format: 'json',
    };

    $.getJSON(url, data, function(json, status, request) {
       if(status != "success") {
         $("#step2error").html("Geocode error: " + status);
         $("#step2error").show();
       } else if(!json.length) {
         $("#step2error").html("Geocode error: no results returned");
         $("#step2error").show();
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
        step3NeedsAjaxCheck = true;
        $("#geocodesubmit").click();
    }
 }).change(function() {
    step3NeedsAjaxCheck = true;
 });
 
 $("#geocodesubmit").click(function(e) {
    e.preventDefault();
   if (step2NeedsAjaxCheck) {
    $("#step2error").hide();
    var address = $("#geocodeaddress").val();
    geocode(address);
    step2NeedsAjaxCheck = false;
   }
   else { step2NeedsAjaxCheck = true; }
 });

 function copyDataToHiddenFields() {
    $("#town").val($("#geocodetown").html());
    $("#longitude").val($("#geocodelongitude").html());
    $("#latitude").val($("#geocodelatitude").html());
    $("#about_me").val($("#about_me_textarea").val());
    $("#contact_info").val($("#contact_info_textarea").val());
 }

 function submitForm(step) {
   copyDataToHiddenFields();
   $("#step"+step+"submit").attr('disabled', 'disabled');
   $("#step"+step+"previous").attr('disabled', 'disabled');
   $("#normalform").submit();
   submitted = true;
   $("#step"+step).fadeOut(400, function(){
      showPleaseWait();
   });
 }

 submitted = false;
 $("#step3submit").click(function(e) {
    e.preventDefault();
    if (getStep() != "3") {
      return;
    }
    hideWithLoading($(this));
    if (validateStep3()) {
       if (confirm($("#confirmBoxOne").html())) {
         $("#step3").fadeOut(400, function(){
            $("#step4").fadeIn(400);
         });
         setStep("4");
       }
    } else {
      $("#step3error").show();
    }
    showAfterLoading($(this));
 });



 $("#step4submit").click(function(e) {
    e.preventDefault();
    if (getStep() != "4") {
      return;
    }
    hideWithLoading($(this));
    if (validateStep4()) {
      if (submitted) {
         return false;
      }
      else {
         $("#loginphrase").hide();
         p = prompt($("#phrasePrompt").html(),"");
         $("#loginphrase").show();
         if (p) {
            p = $.trim(p).toUpperCase().split(' ').join('');
            if (p === $("#hidden_loginphrase").html()) {
               $("#step4").fadeOut(400, function(){
                  $("#step5").fadeIn(400);
               });
               setStep("5");
            } else {
               alert($("#phraseError").html());
            }
         }
      }
    } else {
      $("#step4error").show();
    }
    showAfterLoading($(this));
 });

$("#step2previous").click(function(e) {
   e.preventDefault();
   if(getStep() != "2") {
      return;
   }
   showAfterLoading($("#map_canvas"));
   $("#step2").fadeOut(400, function(){
       $("#step1").fadeIn(400);
   });
   setStep("1");
});

$("#step3previous").click(function(e) {
   e.preventDefault();
   if(getStep() != "3") {
      return;
   }
   $("#step3").fadeOut(400, function(){
      showStepTwo();
   });
   setStep("2");
});

$("#step4previous").click(function(e) {
   e.preventDefault();
   if(getStep() != "4") {
      return;
   }
   $("#step4").fadeOut(400, function(){
       $("#step3").fadeIn(400);
   });
   setStep("3");
});

$("#step5previous").click(function(e) {
   e.preventDefault();
   if(getStep() != "5") {
      return;
   }
   $("#step5").fadeOut(400, function(){
       $("#step4").fadeIn(400);
   });
   setStep("4");
});


//
// Reverse geocoding
//
var dblClickHandler = function(e) {

   // show textbox after doubleclick
   if ($("#step2no").is(":visible")) {
      $("#step2no").click();
   }
   $("#geocodetown").html("Retrieving location...");
   $("#step2error").hide();

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

   // submit reverse geocode request 
   var url = 'http://nominatim.openstreetmap.org/reverse';
   var data = {
      lat: latitude,
      lon: longitude,
      format: 'json'
   };
   $.getJSON(url, data, function(json, status, request){
      if (status != "success") {
         $("#step2error").html("Reverse Geocode error: " + status);
         $("#step2error").show();
      } else {
         var town = json['display_name'];
         $("#geocodetown").html(town);
         $("#geocodeaddress").val(town);
         $("#geocodelongitude").html(longitude);
         $("#geocodelatitude").html(latitude);
      }
   });
};

var Navigation = new OpenLayers.Control.Navigation({
    defaultDblClick: dblClickHandler
});

if(!$.global) {
   $.global = {};
   $.global['Navigation'] = Navigation;
} else {
   $.global.map.addControl(Navigation);
}

$("#about_me_textarea").val("");
$("#contact_info_textarea").val("");

function replaceCommas(elm) {
   elm.html(elm.html().replace(",", "."));
}

function twipsyInit(elm) {
   elm.twipsy();
   elm.click(function(e){
      e.preventDefault();
   });
}

function popoverInit(elm) {
   elm.popover();
   elm.click(function(e){
      e.preventDefault();
   });
}

twipsyInit($("#captcha-info"));
twipsyInit($("#select-languages-info"));
twipsyInit($("#local-area-info"));
twipsyInit($("#enter-location-info"));
twipsyInit($("#skills-info"));
popoverInit($('#email-info'));
popoverInit($('#encryption-info'));

replaceCommas($("#geocodelatitude"));
replaceCommas($("#geocodelongitude"));

$("img.captcha").css({"height":"62px","width":"200px"});

setStep("1");

});
