$(document).ready(function(){

$("#phrasesubmit").click(function(e){
   $("#div_username").removeClass("error");
   $("#div_password").removeClass("error");
   if ($("#id_loginphrase").val() == "") {
      e.preventDefault();
      $("#div_loginphrase").addClass("error");
   } else {
      $("#div_loginphrase").removeClass("error");
      $("#id_loginphrase").val($.trim($("#id_loginphrase").val()).toUpperCase().split(' ').join(''));
      $("#loginphrase_container").hide();
      $("#pleaseWait").show();
   }
});

$("#new-login-info").
   popover({"placement":"above"}).
   click(function(e){
      e.preventDefault();
   });

});
