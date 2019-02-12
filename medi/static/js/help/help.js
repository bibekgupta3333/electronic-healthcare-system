function showDivControl( tag ) {
    if( tag == 'video') {
        $('#videoTitle').show();
        $('#videoPlayerId').show();
        $('#pdfPreview').hide();
    } else {
        $('#videoTitle').hide();
        $('#videoPlayerId').hide();
        $('#pdfPreview').show();
    }
}

function changeScreen( code ) {
    var filePath, titlePreview;
    var url, title;
    var code = parseInt( code );
    switch( code ) {
        case 21:
            url = 'https://player.vimeo.com/video/312823548';
            title = 'SARs-Flow User Guide'
            $('#videoPlayerId').attr('src', url );
            $('#videoTitle').text( title );
            $('#videoPlayerId').attr('src', $('#videoPlayerId').attr('src'));
            showDivControl('video');
            break;
        case 52:
            filePath = '/static/documents/DataPolicy.pdf';
            titlePreview = 'Data Policy';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            showDivControl('pdf');
            $('#iframe').attr('src', $('#iframe').attr('src'));
            break;
        case 53:
            filePath = '/static/documents/TermAndConditions.pdf';
            titlePreview = 'Term & Conditions';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            showDivControl('pdf');
            $('#iframe').attr('src', $('#iframe').attr('src'));
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

function cleanSymbol() {
    var maxId = 5;
    for( i = 0; i <= maxId; i++ ) {
        var idStr = '#symbol-' + i;
        $(idStr).addClass(oldClass);
    }
}