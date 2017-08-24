$('#NewRegistrationVinCodeButton').on('click', function() {
  var step_1_elem = $('.step_1')
  var step_1_progress = $('.step_1 .progress-bar')
  step_1_progress.one('transitionend', function() {
    var step_2_elem = $('.step_2')
    var step_2_progress = $('.step_2 .progress-bar')
    step_2_elem.addClass('active');
    step_2_progress.one('transitionend', function() {
      var step_2_elem = $('.step_2');
      step_2_elem.removeClass('disabled');
      $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
      $('.step_1_body').addClass('hidden')
      $('.step_2_body').removeClass('hidden')
    });
  });
  step_1_elem.removeClass('active')
  step_1_elem.addClass('complete')
})

$('.send-documents-button').on('click', function() {
  $.ajax({
    url: '/cars/registration',
    type: 'POST',
    data: new FormData($('#newRegistrationForm')[0]),
    cache: false,
    contentType: false,
    processData: false,
    success: function(response) {
      var step_2_elem = $('.step_2')
      var step_2_progress = $('.step_2 .progress-bar')
      step_2_progress.one('transitionend', function() {
        var step_3_elem = $('.step_3')
        var step_3_progress = $('.step_3 .progress-bar')
        step_3_elem.addClass('active');
        step_3_progress.one('transitionend', function() {
          var step_3_elem = $('.step_3');
          step_3_elem.removeClass('disabled');
          $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
          $('.step_2_body').addClass('hidden')
          $('.step_3_body').removeClass('hidden')
        });
      });
      step_2_elem.removeClass('active')
      step_2_elem.addClass('complete')
    }
  })
})

$('#registrationStep3SubmitButton').on('click', function() {
  var numberId = $('input[name="registrationNumber"]:checked').val()
  var reg_id = $(this).data('regid')
  $.put('/cars/registration', {'number': numberId, 'registrationId': reg_id}, function(resp) {
    var step_3_elem = $('#registrationFrameBuyer' + reg_id + ' .step_3')
    var step_3_progress = $('#registrationFrameBuyer' + reg_id + ' .step_3 .progress-bar')
    step_3_progress.one('transitionend', function() {
      var step_4_elem = $('#registrationFrameBuyer' + reg_id + ' .step_4')
      var step_4_progress = $('#registrationFrameBuyer' + reg_id + ' .step_4 .progress-bar')
      step_4_elem.addClass('active');
      step_4_progress.one('transitionend', function() {
        var step_4_elem = $('#registrationFrameBuyer' + reg_id + ' .step_4');
        step_4_elem.removeClass('disabled');
        hide_step_bodies($('#registrationFrameBuyer' + resp.registration_id))
        $('#registrationFrameBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
        enable_wizard_dot()
      });
    });
    loadRegPaymentPage(reg_id);
    if(step_3_elem.hasClass('complete')) {
      hide_step_bodies($('#registrationFrameBuyer' + resp.registration_id))
      $('#registrationFrameBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
    } else {
      step_3_elem.removeClass('active')
      step_3_elem.addClass('complete')
    }
  });
})

// function loadRegPaymentPage(reg_id) {
//   var product_id = 'reg' + reg_id
//   if (!$('#registrationModalBuyer' + reg_id + ' .tax_is_paid_text').length) {
//     if(paymentStatusIntervals[product_id]) {
//       clearInterval(paymentStatusIntervals[product_id])
//     }
//     $('#' + product_id + 'PayFrameModal').html('')
//     $.get('/payment/checkout?product_id=' + product_id, function(resp) {
//       var orderId = resp.response.pg_order_id
//       var checkoutUrl = resp.response.pg_redirect_url
//       $('<iframe>', {
//         src: checkoutUrl,
//         id:  'payFrame',
//         frameborder: 0,
//         scrolling: 'no'
//       }).appendTo('#' + product_id + 'PayFrameModal');
//       var checkStatusInterval = setInterval(function () {
//         $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
//           if (resp.response.pg_transaction_status === 'ok') {
//             clearInterval(checkStatusInterval)
//             var step_3_elem = $('#reregistrationFrameBuyer' + reg_id + ' .step_3')
//             var step_3_progress = $('#reregistrationFrameBuyer' + reg_id + ' .step_3 .progress-bar')
//             step_3_progress.one('transitionend', function() {
//               var step_4_elem = $('#reregistrationFrameBuyer' + reg_id + ' .step_4')
//               var step_4_progress = $('#reregistrationFrameBuyer' + reg_id + ' .step_4 .progress-bar')
//               step_4_elem.addClass('active');
//               step_4_progress.one('transitionend', function() {
//                 var step_4_elem = $('#reregistrationFrameBuyer' + reg_id + ' .step_4');
//                 step_4_elem.removeClass('disabled');
//                 hide_step_bodies($('#reregistrationFrameBuyer' + reg_id))
//                 $('#reregistrationFrameBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
//                 var is_paid_text = '<div class="tax_is_paid_text">Оплата произведена</div>'
//                 var number_freeze_text = '<p class="text-warning">Невозможно сменить номер после оплаты!</p>'
//                 $('#reregistrationFrameBuyer' + reg_id + ' .step_3_body').html(is_paid_text)
//                 $('#reregistrationFrameBuyer' + reg_id + ' .step_2_body').html(number_freeze_text)
//                 enable_wizard_dot();
//               });
//             });
//             if(step_3_elem.hasClass('complete')) {
//               hide_step_bodies($('#reregistrationFrameBuyer' + reg_id))
//               $('#reregistrationFrameBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
//             } else {
//               step_3_elem.removeClass('active')
//               step_3_elem.addClass('complete')
//             }
//           }
//         });
//       }, 10000)
//       paymentStatusIntervals[product_id] = checkStatusInterval
//     })
//   }
// }
