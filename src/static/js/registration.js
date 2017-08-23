$('#NewRegistrationVinCodeButton').on('click', function() {
  var step_1_elem = $('.step_1')
  var step_1_progress = $('.step_1 .progress-bar')
  step_1_progress.one('transitionend', function() {
    var step_2_elem = $('.step_2')
    var step_2_progress = $('.step_2 .progress-bar')
    step_2_elem.addClass('active');
    step_2_progress.one('transitionend', function() {
      var step_2_elem = $('.step_2');
      step_2_elem.removeClass('disabled');
      $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
      $('.step_1_body').addClass('hidden')
      $('.step_2_body').removeClass('hidden')
    });
  });
  step_1_elem.removeClass('active')
  step_1_elem.addClass('complete')
})

$('.send-documents-button').on('click', function() {
  $.ajax({
    url: '/cars/registration',
    type: 'POST',
    data: new FormData($('#newRegistrationForm')[0]),
    cache: false,
    contentType: false,
    processData: false,
    success: function(response) {
      var step_2_elem = $('.step_2')
      var step_2_progress = $('.step_2 .progress-bar')
      step_2_progress.one('transitionend', function() {
        var step_3_elem = $('.step_3')
        var step_3_progress = $('.step_3 .progress-bar')
        step_3_elem.addClass('active');
        step_3_progress.one('transitionend', function() {
          var step_3_elem = $('.step_3');
          step_3_elem.removeClass('disabled');
          $('#newRegistrationForm input[name="vin_code"]').val($('#newRegistrationVinCode').val())
          $('.step_2_body').addClass('hidden')
          $('.step_3_body').removeClass('hidden')
        });
      });
      step_2_elem.removeClass('active')
      step_2_elem.addClass('complete')
    }
  })
})
