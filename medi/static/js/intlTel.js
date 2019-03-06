function setDefaultCountry(phoneID, codeID, countryCode){
  var phoneCode = $(".country-list li[data-country-code=" + countryCode + "]").attr("data-dial-code");
  var telephoneCode = $("#id_patient_telephone_code").val();
  if(telephoneCode){
    countryCode = $(".country-list li[data-dial-code=" + telephoneCode + "]").attr("data-country-code");
    phoneCode = telephoneCode;
  }
  $("#" + codeID).parent().find(".intl-tel-input").addClass("iti-sdc-3");
  $("#" + codeID).parent().find(".selected-flag").attr("title", "+" + phoneCode);
  $("#" + codeID).parent().find(".selected-flag .iti-flag").addClass(countryCode);
  $("#" + codeID).parent().find(".selected-flag .selected-dial-code").html("+" + phoneCode);
  $("li[data-country-code='" + countryCode + "']").addClass("active");
  $("li[data-country-code='" + countryCode + "']").attr("aria-selected", true);
  $("#country-listbox").attr("aria-activedescendant", "iti-item-" + countryCode);
  $("#" + codeID).val(phoneCode);
}

function setUpTel(phoneID, codeID){
  $.get("https://ipinfo.io", function() {}, "jsonp").always(function(resp) {
    var inputPhone = document.querySelector("#" + phoneID);
    var countryCode = (resp && resp.country) ? resp.country : "";
    countryCode = countryCode.toLocaleLowerCase();
    intlTelInput(inputPhone, {
      separateDialCode: true,
      initialCountry: countryCode
    });
    $("#" + phoneID).on('keyup click', function () {
      var number = $(this).val();
      if(number.length > 0 && number[0] == '0'){
        $(this).val(number.substring(1));
      }
    });
    inputPhone.addEventListener("keyup", function() {
      var code = $(this).parent().find(".selected-flag")[0].title.split(": ")[1];
      if(code !== undefined){
        $(this).parent().find(".selected-dial-code").html(code);
        $("#" + codeID).val($("#" + phoneID).parent().find(".selected-flag")[0].title.split("+")[1]);
      }
    });
    inputPhone.addEventListener("close:countrydropdown", function() {
      var code = $(this).parent().find(".selected-flag")[0].title.split(": ")[1];
      $(this).parent().find(".selected-dial-code").html(code);
      $("#" + codeID).val($("#" + phoneID).parent().find(".selected-flag")[0].title.split("+")[1]);
    });
    inputPhone.addEventListener("countrychange", function() {
      var code = $(this).parent().find(".selected-flag")[0].title.split(": ")[1];
      $(this).parent().find(".selected-dial-code").html(code);
      $("#" + codeID).val($("#" + phoneID).parent().find(".selected-flag")[0].title.split("+")[1]);
    });
    setDefaultCountry(phoneID, codeID, countryCode);
  });
}

$(document).ready(function () {
  $('#id_patient_telephone_mobile').change( function() {
    if( $('#id_patient_telephone_mobile').val().length > 11) {
        $('#id_patient_telephone_mobile').addClass('is-invalid');
        $('#help-msg-phone1').removeClass('text-muted');
        $('#help-msg-phone1').addClass('text-danger');
    } else {
        $('#id_patient_telephone_mobile').removeClass('is-invalid');
        $('#help-msg-phone1').addClass('text-muted');
        $('#help-msg-phone1').removeClass('text-danger');
    }
  });

  $('#id_patient_alternate_phone').change( function() {
    if( $('#id_patient_alternate_phone').val().length > 11) {
        $('#id_patient_alternate_phone').addClass('is-invalid');
        $('#help-msg-phone2').removeClass('text-muted');
        $('#help-msg-phone2').addClass('text-danger');
    } else {
        $('#id_patient_alternate_phone').removeClass('is-invalid');
        $('#help-msg-phone2').addClass('text-muted');
        $('#help-msg-phone2').removeClass('text-danger');
    }
  });
});