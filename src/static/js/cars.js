$(".datepicker").flatpickr({
  'locale': 'ru',
  'altFormat': 'j F Y',
  'minDate': 'today',
  'altInput': true,
  'dateFormat': 'Y-m-j'
});

$.put = function(url, data, callback, type){
  if ( $.isFunction(data) ){
    type = type || callback,
    callback = data,
    data = {}
  }
  return $.ajax({
    url: url,
    type: 'PUT',
    success: callback,
    data: data,
    contentType: type
  });
}

$.delete = function(url, data, callback, type){
  if ( $.isFunction(data) ){
    type = type || callback,
    callback = data,
    data = {}
  }
   return $.ajax({
    url: url,
    type: 'DELETE',
    success: callback,
    data: data,
    contentType: type
  });
}

$('.car-taxes .pay-button, .car-fines .pay-button').on('click', function() {
  var target = this;
  $.get('/payment/checkout?product_id=' + target.dataset.productid, function(resp) {
    var orderId = resp.response.pg_order_id
    var checkoutUrl = resp.response.pg_redirect_url
    $('<iframe>', {
      src: checkoutUrl,
      id:  target.dataset.productid + 'PayFrame',
      frameborder: 0,
      scrolling: 'no'
    }).appendTo('#' + target.dataset.productid + 'PayFrameModal');
    var checkStatusInterval = setInterval(function () {
      $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
        if (resp.response.pg_transaction_status === 'ok') {
          clearInterval(checkStatusInterval)
          window.location.reload(true);
        }
      });
    }, 10000)
  })
})

var paymentStatusIntervals = {}



var enable_wizard_dot = function() {
  $('.reregistration-modal-buyer .complete .bs-wizard-dot, .reregistration-modal-buyer .active .bs-wizard-dot').unbind('click')
  $('.reregistration-modal-buyer .complete .bs-wizard-dot, .reregistration-modal-buyer .active .bs-wizard-dot').on('click', function() {
    var dot = $(this)
    var step = dot.parent('.bs-wizard-step')
    var modal = dot.closest('.modal')
    if (step.hasClass('step_1')) {
      hide_step_bodies(modal)
      modal.find('.step_1_body').removeClass('hidden')
    }
    if (step.hasClass('step_2')) {
      hide_step_bodies(modal)
      modal.find('.step_2_body').removeClass('hidden')
    }
    if (step.hasClass('step_3')) {
      hide_step_bodies(modal)
      modal.find('.step_3_body').removeClass('hidden')
    }
    if (step.hasClass('step_4')) {
      hide_step_bodies(modal)
      modal.find('.step_4_body').removeClass('hidden')
    }
  })
}

var hide_step_bodies = function(modal) {
  modal.find('.step_1_body').addClass('hidden')
  modal.find('.step_2_body').addClass('hidden')
  modal.find('.step_3_body').addClass('hidden')
  modal.find('.step_4_body').addClass('hidden')
}
enable_wizard_dot();

$('.no-transit-numbers-button').on('click', function() {
  var car_id = $(this).data('car-id')
  $.post('/cars/deregistration', {'car_id': car_id}, function(resp) {
    if (resp.deregistration_id) {
      var step_1_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_1')
      var step_1_progress = $('#carPanel' + car_id + ' .deregistrationModal .step_1 .progress-bar')
      step_1_progress.one('transitionend', function() {
        var step_2_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_2')
        var step_2_progress = $('#carPanel' + car_id + ' .deregistrationModal .step_2 .progress-bar')
        step_2_elem.addClass('active');
        step_2_progress.one('transitionend', function() {
          var step_2_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_2');
          step_2_elem.removeClass('disabled');
          $('#carPanel' + car_id + ' .deregistrationModal .deregistration-time-button')[0].setAttribute('data-deregistrationid', resp.deregistration_id)
          $('#carPanel' + car_id + ' .deregistrationModal .step_1_body').addClass('hidden')
          $('#carPanel' + car_id + ' .deregistrationModal .step_2_body').removeClass('hidden')
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
              var step_1_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_1')
              var step_1_progress = $('#carPanel' + car_id + ' .deregistrationModal .step_1 .progress-bar')
              step_1_progress.one('transitionend', function() {
                var step_2_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_2')
                var step_2_progress = $('#carPanel' + car_id + ' .deregistrationModal .step_2 .progress-bar')
                step_2_elem.addClass('active');
                step_2_progress.one('transitionend', function() {
                  var step_2_elem = $('#carPanel' + car_id + ' .deregistrationModal .step_2');
                  step_2_elem.removeClass('disabled');
                  $('#carPanel' + car_id + ' .deregistrationModal .deregistration-time-button')[0].setAttribute('data-deregistrationid', resp.deregistration_id)
                  $('#carPanel' + car_id + ' .deregistrationModal .step_1_body').addClass('hidden')
                  $('#carPanel' + car_id + ' .deregistrationModal .step_2_body').removeClass('hidden')
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
  var data = {
    'deregistrationId': deregistrationId,
    'inspectionCenterId': target.closest('.deregistrationModal').find('.inspection-place-input').val(),
    'inspectionDate': target.closest('.deregistrationModal').find('.datepicker').val(),
    'inspectionTimeRange': target.closest('.deregistrationModal').find('.inspection-time-input').val(),
  };
  $.put('/cars/deregistration', data, function(resp) {
    if (resp.deregistration_id) {
      var inspection_place = target.closest('.deregistrationModal').find('.inspection-place-input option:selected').text();
      var inspection_date = target.closest('.deregistrationModal').find('.datepicker.form-control').val()
      var inspection_time = target.closest('.deregistrationModal').find('.inspection-time-input').val()
      $('#deregistrationModal' + resp.car_id + ' .step_2_body p:first-child').text('Ваша бронь: ' + inspection_place + ', ' + inspection_date + ', ' + inspection_time )
      if (!$('#deregistrationModal' + resp.car_id + ' .step_2_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь:')) {
        $('#deregistrationModal' + resp.car_id + ' .step_2_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
      }
      target.innerText = 'Изменить бронь'
    }
  })
})
