var paymentStatusIntervals = {}

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

$('.payAllModal input[type=checkbox]').change(function(){
    if($(this).is(':checked')) {
        $(this).closest('.list-group-item').addClass('list-group-item-info')
    } else {
        $(this).closest('.list-group-item').removeClass('list-group-item-info')
    }
    updatePayAllModalAmount()
});

var updatePayAllModalAmount = function() {
  $('.payAllModalAmount').each(function() {
    var amountSum = 0
    $(this).closest('.list-group').find('.list-group-item-info').each(function() {
      amountSum += parseFloat($(this).find('.pay-amount').text())
    })
    $(this).text(amountSum)
  })
}
updatePayAllModalAmount()

$('.payAllModalButton').on('click', function() {
  var amountSum = 0
  var paymentIds = []
  $(this).closest('.list-group').find('.list-group-item-info').each(function() {
    paymentIds.push($(this).find('input[type="checkbox"]').val())
    amountSum += parseFloat($(this).find('.pay-amount').text())
  })
  $(this).closest('.payAllModal').find('.step_1').hide()
  var product_id = paymentIds.join('|')
  var step_2_div = $(this).closest('.payAllModal').find('.step_2')
  $.get('/payment/checkout?product_id=' + product_id, function(resp) {
    var orderId = resp.response.pg_order_id
    var checkoutUrl = resp.response.pg_redirect_url
    $('<iframe>', {
      src: checkoutUrl,
      frameborder: 0,
      scrolling: 'no'
    }).appendTo(step_2_div);
    var checkStatusInterval = setInterval(function () {
      $.get('/payment/payment_status?order_id=' + orderId, function(resp) {
        if (resp.response.pg_transaction_status === 'ok') {
          clearInterval(checkStatusInterval)
          window.location.reload(true);
        }
      });
    }, 10000)
  })
  step_2_div.show()
})
