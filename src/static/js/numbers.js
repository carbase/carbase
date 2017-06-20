$('.number .buy-button').on('click', function() {
  var payButton = $(this)
  payButton.parent().hide()
  var numberHtml = payButton.parent().find('.row').prop('outerHTML')
  today = (new Date()).toLocaleDateString("ru-RU", { year: 'numeric', month: 'long', day: 'numeric' })
  numberHtml = '<div class="number">' + numberHtml
  numberHtml += '<button class="btn btn-default btn-primary number-info">Куплен ' + today + ' за ' + payButton.data('price') + '₸</button>'
  numberHtml += '</div>'
  $('#numberPlatesModalMy').append(numberHtml)
  // $.get('/cars/checkout?product_id=num' + payButton.data('number-id'), function(resp) {
  //   var orderId = resp.response.pg_order_id
  //   var checkoutUrl = resp.response.pg_redirect_url
  //   $('<iframe>', {
  //     src: checkoutUrl,
  //     frameborder: 0,
  //     scrolling: 'no'
  //   }).appendTo('#numberplatesPaymentContainer');
  //   $('#availableNumberList').hide();
  //   var checkStatusInterval = setInterval(function () {
  //     $.get('/cars/payment_status?order_id=' + orderId, function(resp) {
  //       if (resp.response.pg_transaction_status === 'ok') {
  //         clearInterval(checkStatusInterval)
  //         $('#numberplatesPaymentContainer').html('')
  //         $('#numberplatesPaymentContainer').hide()
  //         $('#availableNumberList').show()
  //         $(this).parent().hide()
  //       }
  //     });
  //   }, 10000)
  // })
});

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
        $('#reregistrationModalBuyer' + reg_id + ' .step_2_body').addClass('hidden')
        $('#reregistrationModalBuyer' + reg_id + ' .step_3_body').removeClass('hidden')
      });
    });
    loadRegPaymentPage(reg_id);
    step_2_elem.removeClass('active')
    step_2_elem.addClass('complete')
  });
})
