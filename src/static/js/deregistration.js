$(".datepicker").flatpickr({
  'locale': 'ru',
  'altFormat': 'j F Y',
  'minDate': 'today',
  'altInput': true,
  'dateFormat': 'Y-m-j'
});

$('.no-transit-numbers-button').on('click', function() {
  var car_id = $(this).data('car-id')
  var post_data = {'car_id': car_id, 'is_transit_number': 0, 'is_paid': 1}
  $.post('/cars/deregistration', post_data, function(resp) {
    if (resp.deregistration_id) {
      var step_1_elem = $('#deregistrationFrame' + car_id + ' .step_1')
      var step_1_progress = $('#deregistrationFrame' + car_id + ' .step_1 .progress-bar')
      step_1_progress.one('transitionend', function() {
        var step_2_elem = $('#deregistrationFrame' + car_id + ' .step_2')
        var step_2_progress = $('#deregistrationFrame' + car_id + ' .step_2 .progress-bar')
        step_2_elem.addClass('active');
        step_2_progress.one('transitionend', function() {
          var step_2_elem = $('#deregistrationFrame' + car_id + ' .step_2');
          step_2_elem.removeClass('disabled');
          $('#deregistrationFrame' + car_id + ' .deregistration-time-button')[0].setAttribute('data-deregistrationid', resp.deregistration_id)
          $('#deregistrationFrame' + car_id + ' .deregistration-time-button')[0].setAttribute('data-carid', car_id)
          $('#deregistrationFrame' + car_id + ' .step_1_body').addClass('hidden')
          $('#deregistrationFrame' + car_id + ' .step_2_body').removeClass('hidden')
        });
      });
      step_1_elem.removeClass('active')
      step_1_elem.addClass('complete')
    }
  });
})


$('.with-transit-numbers-button').on('click', function() {
  var car_id = $(this).data('car-id')
  $.post('/cars/deregistration', {'is_transit_number': 1, 'car_id': car_id}, function(resp) {
    if (resp.deregistration_id) {
      var product_id = 'tran' + resp.deregistration_id
      $.get('/payment/checkout?product_id=' + product_id, function(resp) {
        var orderId = resp.response.pg_order_id
        var checkoutUrl = resp.response.pg_redirect_url
        $('<iframe>', {
          src: checkoutUrl,
          id:  'myFrame',
          frameborder: 0,
          scrolling: 'no'
        }).appendTo('#dereg' + car_id + 'TransitNumbersPayFrame');
        var checkStatusInterval = setInterval(function () {
          $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
            if (resp.response.pg_transaction_status === 'ok') {
              clearInterval(checkStatusInterval)
              var step_1_elem = $('#deregistrationFrame' + car_id + ' .step_1')
              var step_1_progress = $('#deregistrationFrame' + car_id + ' .step_1 .progress-bar')
              step_1_progress.one('transitionend', function() {
                var step_2_elem = $('#deregistrationFrame' + car_id + ' .step_2')
                var step_2_progress = $('#deregistrationFrame' + car_id + ' .step_2 .progress-bar')
                step_2_elem.addClass('active');
                step_2_progress.one('transitionend', function() {
                  var step_2_elem = $('#deregistrationFrame' + car_id + ' .step_2');
                  step_2_elem.removeClass('disabled');
                  $('#deregistrationFrame' + car_id + ' .deregistration-time-button')[0].setAttribute('data-deregistrationid', resp.deregistration_id)
                  $('#deregistrationFrame' + car_id + ' .deregistration-time-button')[0].setAttribute('data-carid', car_id)
                  $('#deregistrationFrame' + car_id + ' .step_1_body').addClass('hidden')
                  $('#deregistrationFrame' + car_id + ' .step_2_body').removeClass('hidden')
                });
              });
              step_1_elem.removeClass('active')
              step_1_elem.addClass('complete')
            }
          });
        }, 10000)
        paymentStatusIntervals[product_id] = checkStatusInterval
      })
    }
  });
})

$('.deregistration-time-button').on('click', function() {
  var target = $(this)
  var deregistrationId = target.data('deregistrationid')
  var car_id = target.data('carid')
  var data = {
    'deregistrationId': deregistrationId,
    'inspectionCenterId': $('#deregistrationFrame' + car_id + ' .inspection-place-input').val(),
    'inspectionDate': $('#deregistrationFrame' + car_id + ' .datepicker').val(),
    'inspectionTimeRange': $('#deregistrationFrame' + car_id + ' .inspection-time-input').val(),
  };
  $.put('/cars/deregistration', data, function(resp) {
    if (resp.deregistration_id) {
      var inspection_place = $('#deregistrationFrame' + car_id + ' .inspection-place-input option:selected').text();
      var inspection_date = $('#deregistrationFrame' + car_id + ' .datepicker.form-control').val()
      var inspection_time = $('#deregistrationFrame' + car_id + ' .inspection-time-input').val()
      $('#deregistrationFrame' + car_id + ' .step_2_body p:first-child').text('Ваша бронь: ' + inspection_place + ', ' + inspection_date + ', ' + inspection_time )
      if (!$('#deregistrationFrame' + car_id + '  .step_2_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь:')) {
        $('#deregistrationModal' + resp.car_id + ' .step_2_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
      }
      target.innerText = 'Изменить бронь'
    }
  })
})
