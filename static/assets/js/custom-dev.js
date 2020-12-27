$(document).ready(function() {
    $("#backtest-cal").validate({
        rules: {
            name:{
                required: true
            },
            index_vlaue:{
                required: true
            },
            market_value:{
                required: true
            },
            protfolio_file:{
               required: true
            }
        },
        messages: {
            name:{
               required: 'Please add the name!'
            } ,
            index_vlaue:{
               required: 'Please add the index value!'
            } ,
            market_value:{
               required: 'Please add the market value!'
            } ,
            protfolio_file:{
                    required: "Please Select CSV file only"
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
var csrftoken = getCookie('csrftoken');
 $("#backtest-cal").on('submit', function(e){
      e.preventDefault();
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
         fd.append('name', name);
         fd.append('currency', currency);
         fd.append('identifier', identifier);
         fd.append('spin_off', spin_off);
         fd.append('index_vlaue', index_vlaue);
         fd.append('market_value', market_value);
         fd.append('download', download);
         fd.append('confirmbox', confirmbox);
         fd.append('csrfmiddlewaretoken', csrftoken);
         console.log(fd)
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
            $('#backtest-cal').css("opacity",".5");
            $('.loader').css('display','flex');
         },
         success: function(response){
            if(response.error){
              $('.loader').css('display','none');
              $('.msg').html('<div class="alert alert-danger"><strong>Error!</strong>'+response.error+'</div>');
            }else if(response.warning){
               $('.loader').css('display','none');
               $('#confirmbox').val("yes");
               $('.warning').html('<div class="alert alert-warning"><strong>Warning!</strong>'+response.warning+'</div>');

            }else if(response.success){
               $('.loader').css('display','none');
               $('#backtest-cal')[0].reset();
               $(".submit").removeAttr("disabled");
               $('.backtest-cal').css('display','none');
               $('.downlaod').css('display','block');
            }

         }
      });
   });
//===================ajax call for genrate existing portfolio=======//
$("#selectboxid").change(function() {
  var portfolio_data = new FormData();
  var portfolio = $("#selectboxid").val();
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
