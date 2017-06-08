$(".datepicker").flatpickr({
  'locale': 'ru',
  'dateFormat': 'j F Yг.'
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

function signAgreement(target) {
  var side = target.dataset.side;
  var data = { 'reregistrationId': target.dataset.reregistrationid };
  if (side == 'seller') {
    data['seller_sign'] = 'seLLerSign'
    data['amount'] = $('#reregistrationAgreement' + data.reregistrationId + 'amount').val()
  }
  if (side == 'buyer') {
    data['buyer_sign'] = 'bUYerSign'
  }
  $.put('/cars/agreement', data, function(resp) {
    if (side == 'seller') {
      $('#sellerSign' + data.reregistrationId).html(data.seller_sign)
    }
    if (side == 'buyer') {
      $('#buyerSign' + data.reregistrationId).html(data.buyer_sign)
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

function change_inspection_time(target) {
  var data = { 'reregistrationId': target.dataset.reregistrationid };
  var inspection_place = $('#inspectionPlaceInput'+ data.reregistrationId).val()
  var inspection_date = $('#inspectionDateInput'+ data.reregistrationId).val()
  var inspection_time = $('#inspectionTimeInput'+ data.reregistrationId).val()
  data['inspection_time'] = inspection_date + ' ' + inspection_time + ' ' + inspection_place
  $.put('/cars/agreement', data, function(resp) {
    if (resp.reregistration_id) {
      $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:first-child').text('Ваша бронь: ' + inspection_place + ' ' + inspection_date + ' ' + inspection_time )
      if (!$('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:nth-child(2)').text().trim().startsWith('Вы можете изменить бронь: ')) {
        $('#reregistrationModalBuyer' + resp.reregistration_id + ' .step_3_body p:nth-child(2)').prepend('Вы можете изменить бронь: ')
      }
      target.innerText = 'Изменить бронь'
    }
  })
}
