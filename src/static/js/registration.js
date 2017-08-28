$(".datepicker").flatpickr({
  'locale': 'ru',
  'altFormat': 'j F Y',
  'minDate': 'today',
  'altInput': true,
  'dateFormat': 'Y-m-j'
});
$('#NewRegistrationVinCodeButton').on('click', function() {
  var step_1_elem = $('.step_1')
  var step_1_progress = $('.step_1 .progress-bar')
  step_1_progress.one('transitionend', function() {
    var step_2_elem = $('.step_2')
    var step_2_progress = $('.step_2 .progress-bar')
    step_2_elem.addClass('active')
    step_2_progress.one('transitionend', function() {
      var step_2_elem = $('.step_2')
      step_2_elem.removeClass('disabled')
      $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
      $('.step_1_body').addClass('hidden')
      $('.step_2_body').removeClass('hidden')
    })
  })
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
        step_3_elem.addClass('active')
        step_3_progress.one('transitionend', function() {
          var step_3_elem = $('.step_3')
          step_3_elem.removeClass('disabled')
          $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
          $('.step_2_body').addClass('hidden')
          $('.step_3_body').removeClass('hidden')
          $('#registrationStep3SubmitButton').attr('data-regid', response.registration_id)
        })
      })
      step_2_elem.removeClass('active')
      step_2_elem.addClass('complete')
    }
  })
})

$('#registrationStep3SubmitButton').on('click', function() {
  var numberId = $('input[name="registrationNumber"]:checked').val()
  var reg_id = $(this).data('regid')
  $.put('/cars/registration', {'number': numberId, 'registrationId': reg_id}, function(resp) {
    var step_3_elem = $('.step_3')
    var step_3_progress = $('.step_3 .progress-bar')
    step_3_progress.one('transitionend', function() {
      var step_4_elem = $('.step_4')
      var step_4_progress = $('.step_4 .progress-bar')
      step_4_elem.addClass('active')
      step_4_progress.one('transitionend', function() {
        var step_4_elem = $('.step_4')
        step_4_elem.removeClass('disabled')
        $('.step_3_body').addClass('hidden')
        $('.step_4_body').removeClass('hidden')
      })
    })
    loadRegPaymentPage(reg_id)
    if(step_3_elem.hasClass('complete')) {
      $('.step_3_body').addClass('hidden')
      $('.step_4_body').removeClass('hidden')
    } else {
      step_3_elem.removeClass('active')
      step_3_elem.addClass('complete')
    }
  })
})

function loadRegPaymentPage(reg_id) {
  var product_id = 'new' + reg_id
  if(paymentStatusIntervals[product_id]) {
    clearInterval(paymentStatusIntervals[product_id])
  }
  $('#newRegPayFrameModal').html('')
  $.get('/payment/checkout?product_id=' + product_id, function(resp) {
    var orderId = resp.response.pg_order_id
    var checkoutUrl = resp.response.pg_redirect_url
    $('<iframe>', {
      src: checkoutUrl,
      id:  'payFrame',
      frameborder: 0,
      scrolling: 'no'
    }).appendTo('#newRegPayFrameModal')
    var checkStatusInterval = setInterval(function () {
      $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
        if (resp.response.pg_transaction_status === 'ok') {
          clearInterval(checkStatusInterval)
          var step_4_elem = $('.step_4')
          var step_4_progress = $('.step_4 .progress-bar')
          step_4_progress.one('transitionend', function() {
            var step_5_elem = $('.step_5')
            var step_5_progress = $('.step_5 .progress-bar')
            step_5_elem.addClass('active')
            step_5_progress.one('transitionend', function() {
              step_5_elem.removeClass('disabled')
              $('.step_4_body').addClass('hidden')
              $('.reserve-time-button').attr('data-registrationid', reg_id)
              $('.step_5_body').removeClass('hidden')
            })
          })
          step_4_elem.removeClass('active')
          step_4_elem.addClass('complete')
        }
      })
    }, 10000)
    paymentStatusIntervals[product_id] = checkStatusInterval
  })
}

$('.reserve-time-button').on('click', function() {
  var target = $(this)
  var registrationId = target.data('registrationid')
  var data = {
    'registrationId': registrationId,
    'inspectionCenterId': $('#inspectionPlaceInput').val(),
    'inspectionDate': $('#inspectionDateInput').val(),
    'inspectionTimeRange': $('#inspectionTimeInput').val(),
  };
  $.put('/cars/registration', data, function(resp) {
    var inspection_place = $('#inspectionPlaceInput option:selected').text();
    var inspection_date = $('.datepicker.form-control').val()
    var inspection_time = $('#inspectionTimeInput').val()
    $('.step_5_body p:first-child').text('Ваша бронь: ' + inspection_place + ', ' + inspection_date + ', ' + inspection_time )
    if (!$('.step_5_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь:')) {
      $('.step_5_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
    }
    target.innerText = 'Изменить бронь'
  })
})
