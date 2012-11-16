$(document).ready(function(){

$("#refreshCaptcha").click(function(e) {
    e.preventDefault();
    $("#captcha").html($("#loadingGif").html());
    $.get("/user/getNewCaptcha", function (result){
        $("#captcha").html(result);
        $("img.captcha").css({"62":"heightpx","width":"200px"});
    });
});

$("#id_captcha_1").attr("autocomplete","off");
$("img.captcha").css({"height":"62px","width":"200px"});

});
