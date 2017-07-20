$('.step_1_body .submit-iin-button').on('click', function() {
  var target = this
  var car_id = target.dataset.carid;
  var data = {
    'car_id': car_id,
    'buyer': 'IIN' + $('#reregistration' + car_id + 'BuyerIIN').val(),
    'agreement': $('#reregistration' + car_id + 'AgreementSelector').val()
  };
  $.post('/cars/reregistration', data, function(resp) {
    if (resp.reregistration_id) {
      var step_1_elem = $('#reregistrationFrame' + car_id + ' .step_1')
      var step_1_progress = $('#reregistrationFrame' + car_id + ' .step_1 .progress-bar')
      step_1_progress.one('transitionend', function() {
        var step_2_elem = $('#reregistrationFrame' + car_id + ' .step_2')
        var step_2_progress = $('#reregistrationFrame' + car_id + ' .step_2 .progress-bar')
        step_2_elem.addClass('active');
        step_2_progress.one('transitionend', function() {
          var step_2_elem = $('#reregistrationFrame' + car_id + ' .step_2');
          step_2_elem.removeClass('disabled');
          $('#reregistration' + car_id + 'reregistrationId').val(resp.reregistration_id)
          $('#reregistrationFrame' + car_id + ' .step_1_body').addClass('hidden')
          $('#reregistrationFrame' + car_id + ' .step_2_body .agreement-text').html(resp.agreement)
          $('#reregistrationFrame' + car_id + ' .step_2_body').removeClass('hidden')
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

$('.agreementSign .cancel-button').on('click', function() {
  var target = this
  var reg_id = $(target).data('reregistrationid')
  $.delete('/cars/reregistration', {'reregistrationId': reg_id}, function() {
    window.location.reload(true);
  });
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
      $.put('/cars/reregistration', data, function(resp) {
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
