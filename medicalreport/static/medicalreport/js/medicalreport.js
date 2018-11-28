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

function enable_submit_button(){
  $('#submitButton').prop("disabled", true);
  if($('#id_gp_practitioner').val()){
      if($('#id_prepared_and_signed_0').is(":checked")){
          $('#submitButton').prop("disabled", false);
      } else if($('#id_prepared_and_signed_1').is(":checked")){
          if($('#id_prepared_by').val()){
              $('#submitButton').prop("disabled", false);
          }
      }
  }
}

function subMitMedicalReport(event){
    if(!$('#accept_disclaimer').is(':checked')){
        create_alert('Please accept the Medidata Exchange Ltd disclaimer.', 'error');
        return false;
    }
    if(event == "draft"){
        $('#event_flag').val('draft');
    } else {
        $('#event_flag').val('submit');
    }
    $('#medicalReportForm').submit();
}

function saveReport(inst = false){
    var post_url = $('#medicalReportForm').attr("action"); //get form action url
    var request_method = $('#medicalReportForm').attr("method"); //get form GET/POST method
    var form_data = $('#medicalReportForm').serialize(); //Encode form elements for submission
    $.ajax({
        url : post_url,
        type: request_method,
        data : form_data
    })
    .done(function(){
        if (!inst) {
            create_alert('Report has been saved.', 'success');
        }
    })
    .fail(function() {
        create_alert('Something went wrong, please try again.', 'error');
    });
}
