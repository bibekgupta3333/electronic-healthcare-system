function showDivControl( tag ) {
    if( tag == 'video') {
        $('#videoTitle').show();
        $('#videoPlayerId').show();
        $('#pdfPreview').hide();
        $('#download-block').hide();
    } else if( tag == 'pdf' ) {
        $('#videoTitle').hide();
        $('#videoPlayerId').hide();
        $('#pdfPreview').show();
        $('#download-block').hide();
    } else {
        $('#videoTitle').hide();
        $('#videoPlayerId').hide();
        $('#pdfPreview').show();
        $('#download-block').show();
    }
}

function changeScreen( code ) {
    var filePath, titlePreview;
    var url, title;
    var code = parseInt( code );
    switch( code ) {
        // Dropdown 1
        case 11:
            filePath = '/static/documents/Set Up Guide Final 2.pdf';
            titlePreview = 'Set-up user guide';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
            break;
        case 12:
            url = 'https://player.vimeo.com/video/312782124';
            title = 'Set-up video'
            $('#videoPlayerId').attr('src', url );
            $('#videoTitle').text( title );
            $('#videoPlayerId').attr('src', $('#videoPlayerId').attr('src'));
            showDivControl('video');
            break;
        // Dropdown 2
        case 21:
            filePath = '/static/documents/SARs User guide Final.pdf';
            titlePreview = 'SARs user guide';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
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
            filePath = '/static/documents/SARs process with eMR.pdf';
            titlePreview = 'SARs process map';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
            break;
        case 24:
            filePath = '/static/documents/Dual Consent Form for SARs Jan 31 2019.pdf';
            titlePreview = 'Dual Consent Form';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
            break;
        // Dropdown 4
        case 41:
            filePath = '/static/documents/SARs for Patients.pdf';
            titlePreview = 'SARs for Patients';
            downloadPath = '/static/documents/SARs for Patients.docx';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#linkDownload').attr('href', downloadPath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('doc');
            break;
        case 42:
            filePath = '/static/documents/SARs for Solicitors.pdf';
            titlePreview = 'SARs for Solicitors';
            downloadPath = '/static/documents/SARs for Solicitors.docx';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#linkDownload').attr('href', downloadPath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('doc');
            break;
        // Dropdown 5
        case 52:
            filePath = '/static/documents/DataPolicy.pdf';
            titlePreview = 'Data Policy';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
            break;
        case 53:
            filePath = '/static/documents/TermAndConditions.pdf';
            titlePreview = 'Term & Conditions';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            showDivControl('pdf');
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