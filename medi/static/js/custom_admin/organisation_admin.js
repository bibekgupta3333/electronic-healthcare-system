(function($) {
    function diaplayAdditionInformation(organisationType){
        if(organisationType=="Insurance"){
                $('.additionInfo').show();
                $('.Insurance').show();
            } else if(organisationType=="Medicolegal") {
                $('.additionInfo').show();
                $('.Insurance').hide();
            } else {
                $('.additionInfo').hide();
                $('.Insurance').hide();
            }
    }

    $(document).ready(function() {
        diaplayAdditionInformation(($('#id_type option:selected').text()).split(' ')[0]);

        $('#id_type').on('change',function() {
            var selected = ($('#id_type option:selected').text()).split(' ')[0];
            diaplayAdditionInformation(selected);
        });
    });
})(django.jQuery);