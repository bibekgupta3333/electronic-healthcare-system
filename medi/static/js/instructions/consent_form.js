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
