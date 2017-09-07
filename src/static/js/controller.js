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

let sign_result = function(data) {
  var storagePath = ''
  var password = ''
  var keyAlias = ''
  var webSocket = new WebSocket('wss://127.0.0.1:13579/')
  var xmlToSign = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><inspector-result>'
  Object.keys(data).forEach(function(key) {
    xmlToSign += '<' + key + '>'
    xmlToSign += data[key]
    xmlToSign += '</' + key + '>'
  })
  xmlToSign += '</inspector-result>'
  console.log(xmlToSign)

  webSocket.onopen = function () {
    webSocket.send('{"method":"browseKeyStore","args":["PKCS12","P12",""]}')
  }

  webSocket.onmessage = function (event) {
    var eventData = JSON.parse(event.data)
    if (eventData.result.endsWith && eventData.result.endsWith('.p12')) {
      storagePath = eventData.result
      $('#declinePrelimenary' + data.id + 'Modal').modal('hide')
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
      data['sign'] = eventData.result
      $.put('/controller/inspection/', data, function(resp) {
        if (resp.result == 'success') {
          location.reload()
        }
      })
    }
  }
}

$('.accept-prelimenary-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_prelimenary_success: 1,
    prelimenary_result: "Подтверждено " + (new Date())
  }
  sign_result(data)
})

$('.decline-prelimenary-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_prelimenary_success: 0,
    prelimenary_result: $('#declinePrelimenary' + inspection_id + 'Reason').val(),
  }
  sign_result(data)
})

$('.accept-revision-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_revision_success: 1,
    revision_result: "Подтверждено " + (new Date())
  }
  sign_result(data)
})

$('.decline-revision-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_revision_success: 0,
    revision_result: $('#declineRevision' + inspection_id + 'Reason').val(),
  }
  sign_result(data)
})

$('.accept-final-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_success: 1,
    result: "Подтверждено " + (new Date())
  }
  sign_result(data)
})

$('.decline-final-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_success: 0,
    result: $('#declineFinal' + inspection_id + 'Reason').val(),
  }
  sign_result(data)
})

$('.logout-button').on('click', function() {
  $.post("/pki/logout/", function(data) {
    if (data.status === 'success') {
      location.reload()
    }
  });
})

$('.filter-group button').on('click', function() {
  $('.filter-group button').removeClass('btn-primary')
  $(this).addClass('btn-primary')
  var filter_type = $(this).data('filter')
  if (filter_type === 'all') {
    $('.panel-inspection').show()
  } else if (filter_type === 'wait-prelimenary') {
    $('.panel-inspection').hide()
    $('.panel-inspection').each(function(index, inspection) {
      if ($(inspection).find('.inspection-status').text().trim() == 'Ожидается предварительная проверка') {
        $(inspection).show()
      }
    })
  } else if (filter_type === 'wait-revision') {
    $('.panel-inspection').hide()
    $('.panel-inspection').each(function(index, inspection) {
      if ($(inspection).find('.inspection-status').text().trim() == 'Ожидается результат осмотра ТС') {
        $(inspection).show()
      }
    })
  } else if (filter_type === 'wait-final') {
    $('.panel-inspection').hide()
    $('.panel-inspection').each(function(index, inspection) {
      if ($(inspection).find('.inspection-status').text().trim() == 'Ожидается заключение') {
        $(inspection).show()
      }
    })
  } else if (filter_type === 'ended') {
    $('.panel-inspection').hide()
    $('.panel-inspection').each(function(index, inspection) {
      if ($(inspection).find('.inspection-status').text().trim() == 'Инспекция завершена') {
        $(inspection).show()
      }
    })
  } else if (filter_type === 'canceled') {
    $('.panel-inspection').hide()
    $('.panel-inspection').each(function(index, inspection) {
      if ($(inspection).find('.inspection-status').text().trim().indexOf('тказано') > -1) {
        $(inspection).show()
      }
    })
  }
})

$('#pkiLoginButton').on('click', function() {
  var storagePath = ''
  var password = ''
  var keyAlias = ''
  var webSocket = new WebSocket('wss://127.0.0.1:13579/')
  var xmlToSign = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><login>' + Date.now() + '</login>'

  webSocket.onopen = function () {
    webSocket.send('{"method":"browseKeyStore","args":["PKCS12","P12",""]}')
  }

  webSocket.onmessage = function (event) {
    var eventData = JSON.parse(event.data)
    if (eventData.result.endsWith && eventData.result.endsWith('.p12')) {
      storagePath = eventData.result
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
            'method': 'getKeys', 'args': ['PKCS12', storagePath, password, 'AUTH']
          }))
        }
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
      data = {
        'sign': eventData.result,
        'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
      }
      $.post('/controller/login/', data, function(resp) {
        console.log(resp)
        if (resp.status == 'success') {
          location.reload()
        } else if (resp.status == 'error') {
          $('#pkiLoginError').text(resp.error_text)
          $('#pkiLoginError').show()
        }
      })
    }
  }
})
