function onSelect(element){
  $('.card-body').hide();
  $('.buttons').hide();
  $('#id_' + element.value).show();
  $('#btn_' + element.value).show();
  if (element.value === "accept"){
      $("#id_consent_form").removeAttr("required");
  }else{
      $("#id_consent_form").attr("required", "true");
  }
}

function renderType(selectType){
  $('.card-body').hide();
  $('.buttons').hide();
  $('#id_' + selectType).show();
  $('#btn_' + selectType).show();
  if (selectType === "accept"){
      $("#id_consent_form").removeAttr("required");
  }else if (selectType === "upload"){
      $("#id_consent_form").attr("required", "true");
  }
}

function updateRejectType(element){
    var rejectID = $(element).attr('id').replace('rejected_reason-', '');
    $('#rejected_reason').val(rejectID);
    $('#consent_reject').val($('#id_patient_input_email').val());
}
