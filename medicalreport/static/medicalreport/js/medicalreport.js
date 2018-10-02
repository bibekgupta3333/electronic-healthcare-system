function updateRejectType(element){
  var rejectID = $(element).attr('id').replace('rejected_type-', '');
  $('#rejected_type').val(rejectID);
}
