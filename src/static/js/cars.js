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

function openPaymentModal(target) {
  $.get('/cars/checkout?product_id='+target.dataset.productid, function(resp) {
    var orderId = resp.response.order_id
    var checkoutUrl = resp.response.checkout_url
    $ipsp.get('checkout').config({
      'wrapper': '#' + target.dataset.productid + 'PayFrameModal',
      'styles': {
        'body': {'overflow': 'hidden'},
        '.page-section-shopinfo': {display: 'none'},
        '.page-section-footer': {display: 'none'}
      }
    }).scope(function () {
      this.setModal(false)
      this.width(625)
      this.height(460)
      this.addCallback(function (data, type) {
        if (data.action === 'redirect') {
          var frameModal = document.getElementById(target.dataset.productid + 'PayFrameModal')
          frameModal.innerHTML = '<p style="text-align:center">Проверка оплаты</p>'
          var checkStatusInterval = setInterval(function () {
            $.get('/cars/payment_status?order_id=' + orderId, function(resp) {
              if (resp.response.order_status === 'approved') {
                clearInterval(checkStatusInterval)
                $('#' + target.dataset.productid + 'PayModal').modal('hide')
                $('#' + target.dataset.productid + 'PaidResult').html('<span>Оплачено</span>')
                $('#' + target.dataset.productid + 'Row').removeClass('text-danger')
                $('#' + target.dataset.productid + 'Row').addClass('text-success')
              }
            });
          }, 1000)
        }
        return false
      })
      this.loadUrl(checkoutUrl)
    })
  })
}

function loadRegPaymentPage(reg_id) {
  var product_id = 'reg' + reg_id
  $.get('/cars/checkout?product_id=' + product_id, function(resp) {
    var orderId = resp.response.order_id
    var checkoutUrl = resp.response.checkout_url
    $ipsp.get('checkout').config({
      'wrapper': '#' + product_id + 'PayFrameModal',
      'styles': {
        'body': {'overflow': 'hidden'},
        '.page-section-shopinfo': {display: 'none'},
        '.page-section-footer': {display: 'none'}
      }
    }).scope(function () {
      this.setModal(false)
      this.width(625)
      this.height(460)
      this.addCallback(function (data, type) {
        if (data.action === 'redirect') {
          var frameModal = document.getElementById(product_id + 'PayFrameModal')
          frameModal.innerHTML = '<p style="text-align:center">Проверка оплаты</p>'
          var checkStatusInterval = setInterval(function () {
            $.get('/cars/payment_status?order_id=' + orderId, function(resp) {
              if (resp.response.order_status === 'approved') {
                clearInterval(checkStatusInterval)
                var step_2_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_2')
                var step_2_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_2 .progress-bar')
                step_2_progress.one('transitionend', function() {
                  var step_3_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_3')
                  var step_3_progress = $('#reregistrationModalBuyer' + reg_id + ' .step_3 .progress-bar')
                  step_3_elem.addClass('active');
                  step_3_progress.one('transitionend', function() {
                    var step_3_elem = $('#reregistrationModalBuyer' + reg_id + ' .step_3');
                    step_3_elem.removeClass('disabled');
                    $('#reregistrationModalBuyer' + reg_id + ' .step_2_body').addClass('hidden')
                    $('#reregistrationModalBuyer' + reg_id + ' .step_3_body').removeClass('hidden')
                  });
                });
                step_2_elem.removeClass('active')
                step_2_elem.addClass('complete')
              }
            });
          }, 1000)
        }
        return false
      })
      this.loadUrl(checkoutUrl)
    })
  })
}

function createAgreement(target) {
  var car_id = target.dataset.carid;
  var data = {'car_id': car_id, 'buyer': 'IIN' + $('#reregistration' + car_id + 'BuyerIIN').val()};
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
          $('#carPanel' + car_id + ' .reregistrationModal .step_2_body').removeClass('hidden')
        });
      });
      step_1_elem.removeClass('active')
      step_1_elem.addClass('complete')
    }
  })
}

function pkiSign(agreementid) {
  var storagePath = ''
  var password = ''
  var keyAlias = ''
  var webSocket = new WebSocket('wss://127.0.0.1:13579/')
  var xmlToSign = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  xmlToSign += document.getElementById('agreementXml' + agreementid).innerHTML
  webSocket.onopen = function () {
    webSocket.send('{"method":"browseKeyStore","args":["PKCS12","P12",""]}')
  }

  webSocket.onmessage = function (event) {
    var eventData = JSON.parse(event.data)
    if (eventData.result.endsWith && eventData.result.endsWith('.p12')) {
      storagePath = eventData.result
      password = prompt('Введите пароль')
      webSocket.send(JSON.stringify({
        'method': 'getKeys', 'args': ['PKCS12', storagePath, password, 'SIGN']
      }))
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
      data.append('side', side)
      data.append('signed_xml', eventData.result)
      xhr.send(data)
    }
  }
}

function signAgreement(target) {
  var side = target.dataset.side;
  var data = { 'reregistrationId': target.dataset.reregistrationid };
  var storagePath = ''
  var password = ''
  var keyAlias = ''
  var webSocket = new WebSocket('wss://127.0.0.1:13579/')
  var xmlToSign = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  xmlToSign += document.getElementById('agreementXml' + target.dataset.reregistrationid).innerHTML

  webSocket.onopen = function () {
    webSocket.send('{"method":"browseKeyStore","args":["PKCS12","P12",""]}')
  }

  webSocket.onmessage = function (event) {
    var eventData = JSON.parse(event.data)
    if (eventData.result.endsWith && eventData.result.endsWith('.p12')) {
      storagePath = eventData.result
      password = prompt('Введите пароль')
      webSocket.send(JSON.stringify({
        'method': 'getKeys', 'args': ['PKCS12', storagePath, password, 'SIGN']
      }))
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
        if (side == 'seller') {
          $('#sellerSign' + data.reregistrationId).html(resp.seller_sign)
        }
        if (side == 'buyer') {
          $('#buyerSign' + data.reregistrationId).html(resp.buyer_sign)
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
                $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_1_body').addClass('hidden')
                $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_2_body').removeClass('hidden')
              });
            });
            loadRegPaymentPage(resp.reregistration_id);
            step_1_elem.removeClass('active')
            step_1_elem.addClass('complete')
          }
        }
      })
    }
  }


}

function change_inspection_time(target) {
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
      $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:first-child').text('Ваша бронь: ' + inspection_place + ', ' + inspection_date + ', ' + inspection_time )
      console.log($('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:nth-child(2)').text().trim())
      if (!$('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь:')) {
        $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
      }
      target.innerText = 'Изменить бронь'
    }
  })
}
