function changeScreen( code ) {
    var filePath, titlePreview;
    var code = parseInt( code );
    switch( code ) {
        case 52:
            filePath = '/static/documents/DataPolicy.pdf';
            titlePreview = 'Data Policy';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            break;
        case 53:
            filePath = '/static/documents/TermAndConditions.pdf';
            titlePreview = 'Term & Conditions';
            $('#path1').attr('data', filePath + '#zoom=100' );
            $('#path2').attr('data', filePath );
            $('#previewTitle').text( titlePreview );
            $('#linkPreviewModeId').attr('href', filePath );
            $('#iframe').attr('src', $('#iframe').attr('src'));
            break;
    }
}