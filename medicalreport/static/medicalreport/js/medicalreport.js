function updateRejectType(element){
  var rejectID = $(element).attr('id').replace('rejected_reason-', '');
  $('#rejected_reason').val(rejectID);
}

function renderReport(element){
  var reportID = $(element).attr('id').replace('report-', '');
  $('.reports').removeClass('active');
  $('#report-' + reportID).addClass('active');
  $('.attachments').hide();
  $('#attachment-' + reportID).show();
}
