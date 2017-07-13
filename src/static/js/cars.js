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

$('.agreementSign .cancel-button').on('click', function() {
  var target = this
  var reg_id = $(target).data('reregistrationid')
  $.delete('/cars/agreement', {'reregistrationId': reg_id}, function() {
    window.location.reload(true);
  });
})

$('#reregistrationStep2SubmitButton').on('click', function() {
  var numberId = $('input[name="reregistrationNumber"]:checked').val()
  var reg_id = $(this).data('regid')
  $.put('/cars/agreement', {'number': numberId, 'reregistrationId': reg_id}, function(resp) {
    var step_2_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_2')
    var step_2_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_2 .progress-bar')
    step_2_progress.one('transitionend', function() {
      var step_3_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_3')
      var step_3_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_3 .progress-bar')
      step_3_elem.addClass('active');
      step_3_progress.one('transitionend', function() {
        var step_3_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_3');
        step_3_elem.removeClass('disabled');
        hide_step_bodies($('#reregistrationModalBuyer' + resp.reregistration_id))
        $('#reregistrationModalBuyer' + reg_id + ' .step_3_body').removeClass('hidden')
        enable_wizard_dot()
      });
    });
    loadRegPaymentPage(reg_id);
    if(step_2_elem.hasClass('complete')) {
      hide_step_bodies($('#reregistrationModalBuyer' + resp.reregistration_id))
      $('#reregistrationModalBuyer' + reg_id + ' .step_3_body').removeClass('hidden')
    } else {
      step_2_elem.removeClass('active')
      step_2_elem.addClass('complete')
    }
  });
})

var paymentStatusIntervals = {}

function loadRegPaymentPage(reg_id) {
  var product_id = 'reg' + reg_id
  if (!$('#reregistrationModalBuyer' + reg_id + ' .tax_is_paid_text').length) {
    if(paymentStatusIntervals[product_id]) {
      clearInterval(paymentStatusIntervals[product_id])
    }
    $('#' + product_id + 'PayFrameModal').html('')
    $.get('/payment/checkout?product_id=' + product_id, function(resp) {
      var orderId = resp.response.pg_order_id
      var checkoutUrl = resp.response.pg_redirect_url
      $('<iframe>', {
        src: checkoutUrl,
        id:  'myFrame',
        frameborder: 0,
        scrolling: 'no'
      }).appendTo('#' + product_id + 'PayFrameModal');
      var checkStatusInterval = setInterval(function () {
        $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
          if (resp.response.pg_transaction_status === 'ok') {
            clearInterval(checkStatusInterval)
            var step_3_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_3')
            var step_3_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_3 .progress-bar')
            step_3_progress.one('transitionend', function() {
              var step_4_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_4')
              var step_4_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_4 .progress-bar')
              step_4_elem.addClass('active');
              step_4_progress.one('transitionend', function() {
                var step_4_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_4');
                step_4_elem.removeClass('disabled');
                hide_step_bodies($('#reregistrationModalBuyer' + reg_id))
                $('#reregistrationModalBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
                var is_paid_text = '<div class="tax_is_paid_text">Оплата произведена</div>'
                var number_freeze_text = '<p class="text-warning">Невозможно сменить номер после оплаты!</p>'
                $('#reregistrationModalBuyer' + reg_id + ' .step_3_body').html(is_paid_text)
                $('#reregistrationModalBuyer' + reg_id + ' .step_2_body').html(number_freeze_text)
                enable_wizard_dot();
              });
            });
            if(step_3_elem.hasClass('complete')) {
              hide_step_bodies($('#reregistrationModalBuyer' + reg_id))
              $('#reregistrationModalBuyer' + reg_id + ' .step_4_body').removeClass('hidden')
            } else {
              step_3_elem.removeClass('active')
              step_3_elem.addClass('complete')
            }
          }
        });
      }, 10000)
      paymentStatusIntervals[product_id] = checkStatusInterval
    })
  }
}

$('.reregistrationModal .submit-iin-button').on('click', function() {
  var target = this
  var car_id = target.dataset.carid;
  var data = {
    'car_id': car_id,
    'buyer': 'IIN' + $('#reregistration' + car_id + 'BuyerIIN').val(),
    'agreement': $('#reregistration' + car_id + 'AgreementSelector').val()
  };
  $.post('/cars/agreement', data, function(resp) {
    if (resp.reregistration_id) {
      var step_1_elem = $('#carPanel' + car_id + ' .reregistrationModal .step_1')
      var step_1_progress = $('#carPanel' + car_id + ' .reregistrationModal .step_1 .progress-bar')
      step_1_progress.one('transitionend', function() {
        var step_2_elem = $('#carPanel' + car_id + ' .reregistrationModal .step_2')
        var step_2_progress = $('#carPanel' + car_id + ' .reregistrationModal .step_2 .progress-bar')
        step_2_elem.addClass('active');
        step_2_progress.one('transitionend', function() {
          var step_2_elem = $('#carPanel' + car_id + ' .reregistrationModal .step_2');
          step_2_elem.removeClass('disabled');
          $('#reregistration' + car_id + 'reregistrationId').val(resp.reregistration_id)
          $('#carPanel' + car_id + ' .reregistrationModal .step_1_body').addClass('hidden')
          $('#carPanel' + car_id + ' .reregistrationModal .step_2_body .agreement-text').html(resp.agreement)
          $('#carPanel' + car_id + ' .reregistrationModal .step_2_body').removeClass('hidden')
        });
      });
      $.each($('.agreementSign button'), function (index, item) {
        $(item).attr('data-reregistrationid', resp.reregistration_id);
      });
      step_1_elem.removeClass('active')
      step_1_elem.addClass('complete')
    }
  })
})

$('.agreementSign .sign-button').on('click', function() {
  var target = this
  var side = target.dataset.side;
  var data = { 'reregistrationId': target.dataset.reregistrationid };
  var storagePath = ''
  var password = ''
  var keyAlias = ''
  var webSocket = new WebSocket('wss://127.0.0.1:13579/')
  var xmlToSign = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  xmlToSign += '<agreement-text>'
  xmlToSign += $(target).closest('.modal-body').find('.agreement-text').text().trim()
  xmlToSign += '</agreement-text>'
  webSocket.onopen = function () {
    webSocket.send('{"method":"browseKeyStore","args":["PKCS12","P12",""]}')
  }

  webSocket.onmessage = function (event) {
    var eventData = JSON.parse(event.data)
    if (eventData.result.endsWith && eventData.result.endsWith('.p12')) {
      storagePath = eventData.result
      var reregistrationModal = $(target).closest('.modal')
      reregistrationModal.modal('hide')
      var passwordPrompt = bootbox.prompt({
        title: "Введите пароль",
        inputType: 'password',
        buttons: {
          confirm: {
            label: 'Ok',
            className: 'btn-success'
          },
          cancel: {
            label: 'Cancel',
            className: 'hidden',
          }
        },
        callback: function (result) {
          password = result
          webSocket.send(JSON.stringify({
            'method': 'getKeys', 'args': ['PKCS12', storagePath, password, 'SIGN']
          }))
        }
      });
      passwordPrompt.on('hidden.bs.modal', function() {
        reregistrationModal.modal('show');
      });
    }
    if (eventData.result.startsWith && eventData.result.startsWith('RSA|')) {
      keyAlias = eventData.result.split('|')[3]
      webSocket.send(JSON.stringify({
        'method': 'signXml',
        'args': [
          'PKCS12',
          storagePath,
          keyAlias,
          password,
          xmlToSign
        ]
      }))
    }
    if (eventData.result.startsWith && eventData.result.startsWith('<?xml version="1.0"')) {
      if (side == 'seller') {
        data['seller_sign'] = eventData.result
        data['amount'] = $('#reregistrationAgreement' + data.reregistrationId + 'amount').val()
      }
      if (side == 'buyer') {
        data['buyer_sign'] = eventData.result
      }
      $.put('/cars/agreement', data, function(resp) {
        var qr_code
        if (side == 'seller') {
          qr_code = '<img src="https://chart.googleapis.com/chart?cht=qr&amp;chs=350x350&amp;chl=' + resp.seller_sign + '">'
          $('#sellerSign' + data.reregistrationId).html(qr_code)
        }
        if (side == 'buyer') {
          qr_code = '<img src="https://chart.googleapis.com/chart?cht=qr&amp;chs=350x350&amp;chl=' + resp.buyer_sign + '">'
          $('#buyerSign' + data.reregistrationId).html(qr_code)
          if (resp.reregistration_id) {
            var step_1_elem = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_1')
            var step_1_progress = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_1 .progress-bar')
            step_1_progress.one('transitionend', function() {
              var step_2_elem = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2')
              var step_2_progress = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2 .progress-bar')
              step_2_elem.addClass('active');
              step_2_progress.one('transitionend', function() {
                var step_2_elem = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2');
                step_2_elem.removeClass('disabled');
                hide_step_bodies($('#reregistrationModalBuyer' + resp.reregistration_id))
                $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2_body').removeClass('hidden')
                enable_wizard_dot();
              });
            });
            loadRegPaymentPage(resp.reregistration_id);
            if(step_1_elem.hasClass('complete')) {
              hide_step_bodies($('#reregistrationModalBuyer' + resp.reregistration_id))
              $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2_body').removeClass('hidden')
            } else {
              step_1_elem.removeClass('active')
              step_1_elem.addClass('complete')
            }
          }
        }
      })
    }
  }
})

$('.reserve-time-button').on('click', function() {
  var target = this
  var data = {
    'reregistrationId': target.dataset.reregistrationid,
    'inspectionCenterId': $('#inspectionPlaceInput'+ target.dataset.reregistrationid).val(),
    'inspectionDate': $('#inspectionDateInput'+ target.dataset.reregistrationid).val(),
    'inspectionTimeRange': $('#inspectionTimeInput'+ target.dataset.reregistrationid).val(),
  };
  $.put('/cars/agreement', data, function(resp) {
    if (resp.reregistration_id) {
      var inspection_place = $('#inspectionPlaceInput'+ resp.reregistration_id + ' option:selected').text();
      var inspection_date = $('#reregistrationModalBuyer' + resp.reregistration_id + ' .datepicker.form-control').val()
      var inspection_time = $('#inspectionTimeInput'+ resp.reregistration_id).val()
      $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_4_body p:first-child').text('Ваша бронь: ' + inspection_place + ', ' + inspection_date + ', ' + inspection_time )
      if (!$('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_4_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь:')) {
        $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_4_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
      }
      target.innerText = 'Изменить бронь'
    }
  })
})

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
