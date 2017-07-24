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
