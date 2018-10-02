function updateRejectType(element){
  var rejectID = $(element).attr('id').replace('rejected_reason-', '');
  $('#rejected_reason').val(rejectID);
}
