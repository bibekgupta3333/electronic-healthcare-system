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
  if($('#id_prepared_and_signed_0').is(":checked")){
      $('#submitButton').prop("disabled", false);
  } else if($('#id_prepared_and_signed_1').is(":checked")){
      if($('#id_prepared_by').val()){
          $('#submitButton').prop("disabled", false);
      }
  }

}

function subMitMedicalReport(event){
    if(event == "draft"){
        $('#event_flag').val('draft');
        $('#medicalReportForm').submit();
    }
    else if(event == "preview"){
        $('#event_flag').val('preview');
        $('#medicalReportForm').submit();
    }
    else if(event == "add-medication"){
        $('#id_prepared_by').removeAttr("required");
        $('#addMedicationButton').prop("disabled", true);
        $('#event_flag').val("add-medication");
        $('#medicalReportForm').submit();
    }
    else if(event == "add-allergies"){
        $('#id_prepared_by').removeAttr("required");
        $('#addAllergiesButton').prop("disabled", true);
        $('#event_flag').val("add-allergies");
        $('#medicalReportForm').submit();
    }
    else {
        $('#confirmSubmitModal').modal("show");
    }
}

function submitConfirmReport( event ) {
    if( event == "confirm" ) {
        if( !$('#accept_disclaimer').is(':checked')) {
            $('#confirmSubmitModal').modal('hide');
            create_alert('Please accept the Medidata Exchange Ltd disclaimer.', 'error');
            return false;
        }
        $('#event_flag').val('submit');
        $('#overlay').show();
        $('#medicalReportForm').submit();
        $('#confirmSubmitModal').modal('hide');
    } else {
        $('#confirmSubmitModal').modal('hide');
        create_alert('Invalid action. Please contact admin.', 'error');
        return false;
    }
}

function saveReport(){
    var inst = arguments.length > 1 && arguments[0] !== undefined ? arguments[0] : false;
    var post_url = $('#medicalReportForm').attr("action"); //get form action url
    var request_method = $('#medicalReportForm').attr("method"); //get form GET/POST method
    var form_data = $('#medicalReportForm').serialize(); //Encode form elements for submission
    $.ajax({
        url : post_url,
        type: request_method,
        data : form_data
    }).done(function(){
        if (!inst) {
            create_alert('Report has been saved.', 'success');
        }
    }).fail(function() {
        create_alert('Something went wrong, please try again.', 'error');
    });
}

function addWordLibrary() {
    var post_url = $('#addWordForm').attr("action"); //get form action url
    var request_method = $('#addWordForm').attr("method"); //get form GET/POST method
    var form_data = $('#addWordForm').serialize(); //Encode form elements for submission
    $.ajax({
        url: post_url,
        type: request_method,
        data: form_data
    }).done(function(response) {
        if (typeof response['add_word_error_message'] != 'undefined') {
            $('#errorMessage').text(response['add_word_error_message']);
        } else {
            $('#errorMessage').text('');
            create_alert(response['message'], 'success');
            $("#addWordModal").modal('hide');
        }
    }).fail(function() {
        create_alert('Something went wrong, please try again.', 'error');
    });
}
