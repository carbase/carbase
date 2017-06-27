var pki_storagePath;
$('.login-keys-button').on('click', function() {
  var pki_webSocket = new WebSocket('wss://127.0.0.1:13579/');
  pki_webSocket.onclose = function(event) {
    if (!event.wasClean) {
      $('#certInfo').html(
        '<p class="error-title">Ошибка при подключении к NCALayer!</p>' +
        '<p class="error-text">Убедитесь что установлено и запущено приложение <a href="http://pki.gov.kz/index.php/ru/ncalayer" target="_blank">NCALayer</a>.' +
        '<br>Установите корневые <a href="http://pki.gov.kz/help/index.html#/?installed=true" target="_blank">регистрационные свидетельства НУЦ РК</a></p>'
      )
    }
  }
  pki_webSocket.onmessage = function(event) {
    var resp = JSON.parse(event.data);
    if (resp.result && !resp.errorCode && resp.result.version) {
      pki_webSocket.send(JSON.stringify({
        'method': 'browseKeyStore',
        'args': ['PKCS12', 'P12', '']
      }));
    } else if (resp.result && resp.result.endsWith && resp.result.endsWith('.p12')) {
      pki_storagePath = resp.result;
      pki_webSocket.close();
      $("#certLocationButton").hide();
      $('#certInfo').html('');
      $("#certPassword").css('display', 'table');
    }
  }
})

$('.login-button').on('click', function() {
  var pki_password = document.getElementById('certPasswordInput').value;
  var pki_webSocket = new WebSocket('wss://127.0.0.1:13579/');
  pki_webSocket.onmessage = function(event) {
    var resp = JSON.parse(event.data);
    if (resp.result && !resp.errorCode && resp.result.version) {
      pki_webSocket.send(JSON.stringify({
        'method': 'getKeys',
        'args': ['PKCS12', pki_storagePath, pki_password, 'AUTH']
      }));
    } else if (resp.result && resp.result.startsWith && resp.result.startsWith('RSA|')) {
      var pki_alias = resp.result.split('|').pop()
      var xmlToSign = '<?xml version="1.0" encoding="utf-8"?>';
      xmlToSign += '<root><time>' + Date.now() + '</time></root>'
      pki_webSocket.send(JSON.stringify({
        "method": "signXml",
        "args": ['PKCS12', pki_storagePath, pki_alias, pki_password, xmlToSign]
      }))
    } else if (resp.result && resp.result.startsWith && resp.result.startsWith('<?xml')) {
      var csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val();
      $.post("/pki/login/", {'signedXml': resp.result, 'csrfmiddlewaretoken': csrfmiddlewaretoken}, function(data) {
        if (data.status === 'success') {
          window.location.replace('/cars');
        } else {
          $('#certInfo').html('<p class="error-title">' + data.error_text + '</p>')
          $("#certLocationButton").show();
          $("#certPassword").hide();
        }
      });

    }
  }
})

$('.logout-button').on('click', function() {
  $.post("/pki/logout/", function(data) {
    if (data.status === 'success') {
      window.location.replace('/');
    }
  });
})

$('#emailAddressSubmit').on('click', function() {
  var data = {
    'emailAddress': $('#emailAddressInput').val(),
    'csrfmiddlewaretoken': $('#emailAddressForm [name="csrfmiddlewaretoken"]').val()
  }
  var url = '/pki/emailAddress/'
  $.post(url, data, function() {
    $('#emailAddressForm').hide();
  });
});
