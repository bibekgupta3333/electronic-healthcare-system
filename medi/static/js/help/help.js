function showDivControl( tag ) {
    $('#default-preview').hide();
    if( tag == 'video') {
        $('.video-title').show();
        $('.video-player').show();
        $('.pdf-block').hide();
    } else {
        $('.video-title').hide();
        $('.video-player').hide();
        $('.pdf-block').hide();
    }
}

function changeScreen( code ) {
    var filePath, titlePreview;
    var url, title;
    var code = parseInt( code );
    switch( code ) {
        // Dropdown 1
        case 11:
            showDivControl('pdf');
            $('#preview-11').show();
            break;
        case 12:
            url = 'https://player.vimeo.com/video/312782124';
            title = 'Set-up video'
            $('#videoPlayerId').attr('src', url );
            $('#videoTitle').text( title );
            $('#default-preview').hide();
            $('#videoPlayerId').attr('src', $('#videoPlayerId').attr('src'));
            showDivControl('video');
            break;

        // Dropdown 2
        case 21:
            showDivControl('pdf');
            $('#preview-21').show();
            break;
        case 22:
            url = 'https://player.vimeo.com/video/317073626';
            title = 'SARs video'
            $('#videoPlayerId').attr('src', url );
            $('#videoTitle').text( title );
            $('#videoPlayerId').attr('src', $('#videoPlayerId').attr('src'));
            showDivControl('video');
            break;
        case 23:
            showDivControl('pdf');
            $('#preview-23').show();
            break;
        case 24:
            showDivControl('pdf');
            $('#preview-24').show();
            break;

        // Dropdown 4
        case 41:
            showDivControl('doc');
            $('#preview-41').show();
            break;
        case 42:
            showDivControl('doc');
            $('#preview-42').show();
            break;

        // Dropdown 5
        case 52:
            showDivControl('pdf');
            $('#preview-52').show();
            break;
        case 53:
            showDivControl('pdf');
            $('#preview-53').show();
            break;
    }
}

let oldClass = 'fas fa-caret-right';
let newClass = 'fas fa-caret-down';
$('.choice-1').click(function() {
    cleanSymbol()
    $('#symbol-1').removeClass(oldClass);
    $('#symbol-1').addClass(newClass);
});
$('.choice-2').click(function() {
    cleanSymbol()
    $('#symbol-2').removeClass(oldClass);
    $('#symbol-2').addClass(newClass);
});
$('.choice-3').click(function() {
    cleanSymbol()
    $('#symbol-3').removeClass(oldClass);
    $('#symbol-3').addClass(newClass);
});
$('.choice-4').click(function() {
    cleanSymbol()
    $('#symbol-4').removeClass(oldClass);
    $('#symbol-4').addClass(newClass);
});
$('.choice-5').click(function() {
    cleanSymbol()
    $('#symbol-5').removeClass(oldClass);
    $('#symbol-5').addClass(newClass);
});
$('.choice-6').click(function() {
    cleanSymbol()
    $('#symbol-6').removeClass(oldClass);
    $('#symbol-6').addClass(newClass);
});

function cleanSymbol() {
    var maxId = 6;
    for( i = 0; i <= maxId; i++ ) {
        var idStr = '#symbol-' + i;
        $(idStr).addClass(oldClass);
    }
}