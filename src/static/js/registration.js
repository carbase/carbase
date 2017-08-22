$('.send-documents-button').on('click', function() {
  $.ajax({
    url: '/cars/registration',
    type: 'POST',
    data: new FormData($('#newRegistrationForm')[0]),
    cache: false,
    contentType: false,
    processData: false,
    success: function(response) {
      console.log(response)
    }
  })
})
