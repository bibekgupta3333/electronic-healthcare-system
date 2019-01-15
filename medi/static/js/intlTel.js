function setDefaultCountry(phoneID, codeID){
  $.get("https://ipinfo.io", function() {}, "jsonp").always(function(resp) {
    var countryCode = (resp && resp.country) ? resp.country : "";
    countryCode = countryCode.toLocaleLowerCase();
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
    $("#" + codeID).val(phoneCode);
  });
}

function setUpTel(phoneID, codeID){
  var inputPhone = document.querySelector("#" + phoneID);
    intlTelInput(inputPhone, {
    separateDialCode: true,
    initialCountry: "auto"
  });
  inputPhone.addEventListener("countrychange", function() {
    var code = $(this).parent().find(".selected-flag")[0].title.split(": ")[1];
    $(this).parent().find(".selected-dial-code").html(code);
    $("#" + codeID).val($("#" + phoneID).parent().find(".selected-flag")[0].title.split("+")[1]);
  });
  setDefaultCountry(phoneID, codeID);
}
