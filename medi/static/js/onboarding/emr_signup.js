
function init_select2_postcode(init_data) {
    $('#id_postcode').select2({
        data: init_data,
        ajax: {
            url: function (params) {
                return "https://api.postcodes.io/postcodes/"+ params.term +"/autocomplete"
            },
            processResults: function (data) {
                let formed_data = [];
                for(let i=0; i < data['result'].length; i++){
                    formed_data.push({'id': data['result'][i], 'text': data['result'][i]});
                }
                return {
                    results: formed_data
                }
            }
        }
    });
}

function init_select2_surgery_name(init_data, ajax_url) {

    $('#id_surgery_name').select2({
        data: init_data,
        minimumInputLength: 3,
        tags: true,
        ajax: {
            delay: 500,
            url: ajax_url,
            data: function (params) {
                let query = {
                    name: params.term,
                };
                return query;
            },
            processResults: function (data) {
                return {
                    results: data.items
                }
            }
        }
    });
}

function init_select2_practice_code(init_data, ajax_url) {
    $('#id_practice_code').select2({
        data: init_data,
        minimumInputLength: 3,
        tags: true,
        ajax: {
            delay: 500,
            url: ajax_url,
            data: function (params) {
                let query = {
                    code: params.term,
                };
                return query;
            },
            processResults: function (data) {
                return {
                    results: data.items
                }
            }
        }
    });
}

// Condtions for check validate submit btn.
            // Variable for check.
            let validateSurgeryName;
            let validatePostCode;
            let validatePraticeCode;
            let validateAddress1;
            let validateCity;
            let validateCountry;
            let validateContectNumber;
            let validateEMISCode;

            let validateFirstName;
            let validateSurName;
            let validateEmail1;
            let validateEmail2;
            let validatePassword1;
            let validatePassword2;

            // Func for set value when field change.
            $.setValidate = function( inputValue ) {
                if( inputValue != "" ){
                    return true;
                } else {
                    return false;
                }
            }

            //  Func for check validate and enabled btn.
            $.checkValidate = function() {
                if( validateAddress1 && validateCity && validateCountry && validateContectNumber && validateEMISCode ) {
                    if( validateFirstName && validateSurName && validateEmail1 && validateEmail2 && validatePassword1 && validatePassword2 ) {
                        return $('#BtnSignUp').prop('disabled', false);
                    }
                } 
                return $('#BtnSignUp').prop('disabled', true);
            }

            //  func call .setValidate for set value and check conditions.
            $('#id_address_line1').change(function() {
                 validateAddress1 = $.setValidate( $.trim( $('#id_address_line1').val() ) );
                 $.checkValidate();
            });
            $('#id_city').change(function() {
                 validateCity = $.setValidate( $.trim( $('#id_city').val() ) );
                 $.checkValidate();
            });
            $('#id_country').change(function() {
                 validateCountry = $.setValidate( $.trim( $('#id_country').val() ) );
                 $.checkValidate();
            });
            $('#id_contact_num').change(function() {
                 validateContectNumber = $.setValidate( $.trim( $('#id_contact_num').val() ) );
                 $.checkValidate();
            });
            $('#id_emis_org_code').change(function() {
                 validateEMISCode = $.setValidate( $.trim( $('#id_emis_org_code').val() ) );
                 $.checkValidate();
            });
            $('#id_first_name').change(function() {
                 validateFirstName = $.setValidate( $.trim( $('#id_first_name').val() ) );
                 $.checkValidate();
            });
            $('#id_surname').change(function() {
                 validateSurName = $.setValidate( $.trim( $('#id_surname').val() ) );
                 $.checkValidate();
            });
            $('#id_email1').change(function() {
                 validateEmail1 = $.setValidate( $.trim( $('#id_email1').val() ) );
                 $.checkValidate();
            });
            $('#id_email2').change(function() {
                 validateEmail2 = $.setValidate( $.trim( $('#id_email2').val() ) );
                 $.checkValidate();
            });
            $('#id_password1').change(function() {
                 validatePassword1 = $.setValidate( $.trim( $('#id_password1').val() ) );
                 $.checkValidate();
            });
            $('#id_password2').change(function() {
                 validatePassword2 = $.setValidate( $.trim( $('#id_password2').val() ) );
                 $.checkValidate();
            });