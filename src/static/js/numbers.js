var bind_buy_button = function() {
  $('.number .buy-button').on('click', function() {
    var payButton = $(this)
    $.get('/cars/checkout?product_id=num' + payButton.data('number-id'), function(resp) {
      var orderId = resp.response.pg_order_id
      var checkoutUrl = resp.response.pg_redirect_url
      $('<iframe>', {
        src: checkoutUrl,
        frameborder: 0,
        scrolling: 'no'
      }).appendTo('#numberplatesPaymentContainer');
      $('#availableNumberList').hide();
      var checkStatusInterval = setInterval(function () {
        $.get('/cars/payment_status?order_id=' + orderId, function(resp) {
          if (resp.response.pg_transaction_status === 'ok') {
            clearInterval(checkStatusInterval)
            $('#numberplatesPaymentContainer').html('')
            $('#numberplatesPaymentContainer').hide()
            $('#availableNumberList').show()
            payButton.parent().hide()
            var numberHtml = payButton.parent().find('.row').prop('outerHTML')
            today = (new Date()).toLocaleDateString("ru-RU", { year: 'numeric', month: 'long', day: 'numeric' })
            numberHtml = '<div class="number">' + numberHtml
            numberHtml += '<button class="btn btn-default btn-primary number-info">Куплен ' + today + ' за ' + payButton.data('price') + '₸</button>'
            numberHtml += '</div>'
            $('#numberPlatesModalMy').append(numberHtml)
          }
        });
      }, 10000)
    })
  })
}
bind_buy_button()

$('#numberPlatesModalBuySearchGroup button').on('click', function() {
  var pattern = $('#numberPlatesModalBuySearchGroup input').val()
  $.get('/cars/numbers?q=' + pattern, function(resp) {
    $('#numberPlatesModalNumbers').html('')
    resp.forEach(function(number) {
      var numberElement = '<div class="number">'
      numberElement += '<div class="row">'
      numberElement += '<span class="digits">' + number.digits + '</span>'
      numberElement += ' <span class="chars">' + number.characters + '</span>'
      numberElement += ' <span class="region">' + number.region + '</span>'
      numberElement += '</div>'
      numberElement += '<button data-price="' + number.price + '" data-number-id="' + number.id + '" class="btn btn-default btn-success buy-button">'
      numberElement += 'Купить за ' + number.price + '₸'
      numberElement += '</button>'
      numberElement += '</div>'
      $('#numberPlatesModalNumbers').append(numberElement)
    })
    bind_buy_button()
  })
})


$('#numberPlatesReregistrationSearchGroup button').on('click', function() {
  var pattern = $('#numberPlatesReregistrationSearchGroup input').val()
  $.get('/cars/numbers?q=' + pattern, function(resp) {
    $('#numberPlatesReregistrationNumbers').html('')
    resp.forEach(function(number) {
      var numberElement = '<label><input type="radio" name="reregistrationNumber" value="' + number.id + '">'
      numberElement += '<div class="number">'
      numberElement += '<div class="row">'
      numberElement += '<span class="digits">' + number.digits + '</span>'
      numberElement += ' <span class="chars">' + number.characters + '</span>'
      numberElement += ' <span class="region">' + number.region + '</span>'
      numberElement += '</div>'
      numberElement += '<button class="btn btn-default btn-success">'
      numberElement += 'Купить за ' + number.price + '₸'
      numberElement += '</button>'
      numberElement += '</div>'
      numberElement += '</label>'
      $('#numberPlatesReregistrationNumbers').append(numberElement)
    })
    bind_buy_button()
  })
})
