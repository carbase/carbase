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

$('.accept-prelimenary-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_prelimenary_success: 1,
    prelimenary_result: "Подтверждено" + (new Date())
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})

$('.decline-prelimenary-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_prelimenary_success: 0,
    prelimenary_result: $('#declinePrelimenary' + inspection_id + 'Reason').val(),
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})

$('.accept-revision-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_revision_success: 1,
    revision_result: "Подтверждено " + (new Date())
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})

$('.decline-revision-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_revision_success: 0,
    revision_result: $('#declineRevision' + inspection_id + 'Reason').val(),
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})

$('.accept-final-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_success: 1,
    result: "Подтверждено " + (new Date())
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})

$('.decline-final-submit').on('click', function() {
  var inspection_id = $(this).data('inspectionid')
  var data = {
    id: inspection_id,
    is_success: 0,
    result: $('#declineFinal' + inspection_id + 'Reason').val(),
  }
  $.put('/controller/inspection/', data, function(resp) {
    if (resp.result == 'success') {
      location.reload()
    }
  })
})
