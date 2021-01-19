$(document).ready(function() {
    $("#backtest-cal").validate({
        rules: {
            protfolio_file:{
               required: true
            }
        },
        messages: {
            protfolio_file:{
                    required: "Please select input CSV file only"
            } ,
        }
    });
});


//===ajax call========//

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 
//=== ajax cal for  backtest calculatio=====//
var csrftoken = getCookie('csrftoken');
 $("#backtest-cal").on('submit', function(e){
  if ($('#sav_data').is(":checked")){
    var name_value = document.forms["backtest-cal"]["name"].value;
    if (name_value == "") {
       $('.name-error').html('Please add porfolio name! ')
       return false;
  }
         }
  var formStatus = $('#backtest-cal').validate().form();
      if(true == formStatus){
      e.preventDefault();
         $("#myModal").modal('hide');
         var fd = new FormData();
         var files = document.getElementById('protfolio_file').files.length;
         for (var index = 0; index < files; index++) {
            fd.append("protfolio_file", document.getElementById('protfolio_file').files[index]);
         }
         var files1 = document.getElementById('tax_rate').files.length;
         for (var index = 0; index < files1; index++) {
            fd.append("tax_rate", document.getElementById('tax_rate').files[index]);
         }
         var name = $("#name").val();
         var currency = $("#currency").val();
         var identifier = $("#identifier").val();
         var spin_off = $("#spin_off").val();
         var index_vlaue = $("#index_vlaue").val();
         var market_value = $("#market_value").val();
         var download = $("#download").val();
         var confirmbox = $("#confirmbox").val();
         var save_portfolio = $('#sav_data').val();
         if ($('#sav_data').is(":checked")){
          var save_data ='yes';
          fd.append('save_data', save_data);
         }
         console.log(sav_data)
         fd.append('name', name);
         fd.append('currency', currency);
         fd.append('identifier', identifier);
         fd.append('spin_off', spin_off);
         fd.append('index_vlaue', index_vlaue);
         fd.append('market_value', market_value);
         fd.append('download', download);
         fd.append('confirmbox', confirmbox);
         fd.append('csrfmiddlewaretoken', csrftoken);
         $.ajax({
               type: 'POST',
               url: 'calculation/portfolio/',
               data: fd,
               dataType: 'json',
               contentType: false,
               cache: false,
               processData:false,
         beforeSend: function(){
            $('.submit').attr("disabled","disabled");
            $('.loader').css('display','flex');
         },
         success: function(response){
            if(response.error){
              $('.loader').css('display','none');
              $('.msg').html('<div class="alert alert-danger"><strong>Error!</strong>'+response.error+'</div>');
              }else if (response.error_msg){
                $('.loader').css('display','none');
                $('.msg').html('<div class="alert alert-danger"><strong>Error!</strong>'+response.error_msg+'</div>');


            }else if(response.warning){
               $('.loader').css('display','none');
               $("#myModal").modal('show');
               $('#confirmbox').val("yes");
               $('.warning').html('<div class="alert alert-warning"><strong>Warning!</strong>'+response.warning+'</div>');

            }else if(response.success){
              $("#myModal").modal('hide');
               $('.loader').css('display','none');
               $('#backtest-cal')[0].reset();
               $(".submit").removeAttr("disabled");
               $('.backtest-cal').css('display','none');
               $('.downlaod').css('display','block');
               $('.alert-success').html('<strong>Success! </strong>'+response.success);
               $("#index").attr("href", response.index_file);
               $("#constitute").attr("href", response.constituents_file);
            }

         }
      });
       }
   });
//===================ajax call for genrate existing portfolio=======//
$("#portfolio_id").change(function() {
  var portfolio_data = new FormData();
  var portfolio = $("#portfolio_id").val();
  portfolio_data.append('id', portfolio);
  portfolio_data.append('csrfmiddlewaretoken', csrftoken);
 $.ajax({
       type: 'POST',
       url: 'calculation/get_portfolio/',
       data: portfolio_data,
       dataType: 'json',
       contentType: false,
       cache: false,
       processData:false,
         success: function(response){
          $('#stat_date').val(response.start_date);
          $('#end_date').val(response.end_date);
          console.log(response)

         }
      });
   });

//===================ajax call for rerun portfolio=======//
 $("#rerun").on('submit', function(e){
  e.preventDefault();
  if( document.rerun.portfolio_id.value == "" )
   {
     $('.rerun-msg').html('<div class="alert alert-danger" role="alert">Please select one portfolio from dropdown list.</div>')
     return false;
   }
  var rerun_data = new FormData();
  var portfolio_id = $("#portfolio_id").val();
  var stat_date = $("#stat_date").val();
  var end_date = $("#end_date").val();
  rerun_data.append('portfolio_id', portfolio_id);
  rerun_data.append('stat_date', stat_date);
  rerun_data.append('end_date', end_date);
  rerun_data.append('csrfmiddlewaretoken', csrftoken);
 $.ajax({
       type: 'POST',
       url: 'calculation/rerun_portfolio/',
       data: rerun_data,
       dataType: 'json',
       contentType: false,
       cache: false,
       processData:false,
       beforeSend: function(){
            $('.submit2').attr("disabled","disabled");
            $('.loader').css('display','flex');
         },
         success: function(response){
               $('.loader').css('display','none');
               $('.down1').css('display','block');
               $('.down2').css('display','block');
               $('.rerun-msg').html('<div class="alert alert-success"><strong>Success!</strong>'+response.success+'</div>');
               $("#rerun_index").attr("href", response.index_file);
               $("#rerun_constitute").attr("href", response.constituents_file);
          console.log(response)

         }
      });
   });

//=====================Ad Tax Rate===================//

 $("#addtax").on('submit', function(e){
  e.preventDefault();
  var tax_data = new FormData();
  var country = $("#country").val();
  var tax = $("#tax").val();
  tax_data.append('country', country);
  tax_data.append('tax', tax);
  console.log(tax_data)
 $.ajax({
       type: 'POST',
       url: 'calculation/add_tax/',
       data: tax_data,
       dataType: 'json',
       contentType: false,
       cache: false,
       processData:false,
       beforeSend: function(){
            $('.submitax').attr("disabled","disabled");
            $('.loader').css('display','flex');
         },
         success: function(response){
          console.log(response)

         }
      });
   });

//======================Update Tax Rate=================//
$(document).ready(function() {
for(var counter = 1; counter < 200; counter++) {
  console.log('Inside the loop:' );
  $('.mychoice'+counter).click(function() {
  e.preventDefault();
  var tax_data = new FormData();
  var country = $("#country").val();
  var tax = $("#tax").val();
  tax_data.append('country', country);
  tax_data.append('tax', tax);
  console.log(tax_data)
 $.ajax({
       type: 'POST',
       url: 'calculation/update_tax/',
       data: tax_data,
       dataType: 'json',
       contentType: false,
       cache: false,
       processData:false,
       beforeSend: function(){
            $('.submitax').attr("disabled","disabled");
            $('.loader').css('display','flex');
         },
         success: function(response){
          console.log(response)

         }
      });
}
}
});