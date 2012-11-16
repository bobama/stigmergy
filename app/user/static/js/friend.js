$(document).ready(function() {

   var dropcommentcontent=$("#dropcomment_textarea").html();

   $("#drop-button").click(function(e) {
      e.preventDefault();
      $('html, body').scrollTop(0);
      $("#map_canvas").css("visibility","hidden");
      $("#background").fadeIn();
      $("#modal").fadeIn();
   });

   $("#background, #dropcancel, .close").click(function(e) {
      e.preventDefault();
      $("#modal").fadeOut();
      $("#background").fadeOut(function(){
         resetModal();
      });
      $("#map_canvas").css("visibility","visible");
   });
   
   function resetModal(){
      $(".dropdis").removeClass("dropdis disabled").addClass("dropbutton");
      $(".dropbutton").show();
      $("#dropcomment").hide();
      $("#dropcomment_textarea").val($("#dropcomment_textarea").val() || dropcommentcontent);
   }
   
   $(".dropbutton").click(function(e) {
      e.preventDefault();
      $(this).addClass("dropdis disabled").removeClass("dropbutton");
      $("#dropped_reason").val($(this).attr("id").split("-")[1]);
      $(".dropbutton").slideUp(function(){
         $("#dropcomment").show(function(){
            $("#dropsubmit").fadeIn();
         });
      });
   });

   $("#dropcomment_textarea").focus(function(){
      if ($("#dropcomment_textarea").val() == dropcommentcontent){
         $("#dropcomment_textarea").val("")
      }
   });
   
   $("#dropsubmit").click(function(e) {
      e.preventDefault();
      if ($("#dropcomment_textarea").val() != dropcommentcontent){
         $("#dropped_comment").val($("#dropcomment_textarea").val());
      }
      $("#loginphrase").val($.trim($("#id_password").val()).toUpperCase().split(' ').join(''));
      $("#drop_form").submit();
   });

   $("#title").css({"display": "inline","margin-right":"20px"}).after($(".backlink").html());

   $("#encrypted-info").
      popover({"placement":"below"}).
      click(function(e){
         e.preventDefault();
      });
   $("#drop-info").
      popover({"placement":"above"}).
      click(function(e){
         e.preventDefault();
      });

});


