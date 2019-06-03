
function copyToClipboard(text, el) {
    var copyTest = document.queryCommandSupported("copy");
    var elOriginalText = el.attr("data-original-title");

    if (copyTest === true) {
        var copyTextArea = document.createElement("textarea");
        copyTextArea.value = text;
        document.body.appendChild(copyTextArea);
        copyTextArea.select();
        try {
            var successful = document.execCommand("copy");
            var msg = successful ? "Copied!" : "Whoops, not copied!";
            el.attr("data-original-title", msg).tooltip("show");
        } catch (err) {

        }
        document.body.removeChild(copyTextArea);
        el.attr("data-original-title", elOriginalText);
    } else {
        window.prompt("Copy to clipboard: Ctrl+C or Command+C, Enter", text);
    }
}


function pollingEmis(url) {
    $("#checkingEmisButton").addClass("pendingCheck");
    $("#checkingEmisButton").html(
        "<img src='/static/images/emis_setup/Spin-1s-40px.gif' style='height: 50px; width: 50px;'/> Authenticating..."
    );
    setTimeout(function () {
        $.ajax({
            url: url,
            success: function (data) {
                if(data["status"] >= 200 && data["status"] < 400) {
                    $(".btn-checkSetup").hide();
                    $(".emisSetupSuccess").removeClass("d-none");
                    setTimeout(function () {
                        document.location.href = "/accounts/login/";
                    }, 2000)
                } else {
                    $('#checkingEmisButton').prop("disabled", false);
                    $("#checkingEmisButton").removeClass("pendingCheck");
                    $("#checkingEmisButton").html("<i class='fas fa-question'></i>&nbsp; Check Setup");
                    $("#failSetupEmisModal").modal({
                        backdrop: "static"
                    });
                }
            },
        });
    }, 2000);
}

function pollingNewEmis(url) {
    $("#checkingEmisButton").addClass("pendingCheck");
    $("#checkingEmisButton").html(
        "<img src='/static/images/emis_setup/Spin-1s-40px.gif' style='height: 20px; width: 20px;'/> Authenticating..."
    );
    setTimeout(function () {
        $.ajax({
            url: url,
            success: function (data) {
                if(data["status"] >= 200 && data["status"] < 400) {
                    $(".btn-checkChangeSetup").hide();
                    $(".emisSetupSuccess").removeClass("d-none");
                    setTimeout(function () {

                    }, 2000)
                } else {
                    $(".emisSetupFail").removeClass("d-none");
                    $('#checkingEmisButton').prop("disabled", false);
                    $("#checkingEmisButton").removeClass("pendingCheck");
                    $("#checkingEmisButton").html("<i class='fas fa-question'></i>&nbsp; Check Setup");
                }
            },
        });
    }, 2000);
}

function validateBTN( progressPercent ) {
    if( progressPercent == 20 || progressPercent == 47 || progressPercent == 63 ){
        $('#backBTN').prop('disabled',true);
    } else {
        $('#backBTN').prop('disabled',false);
    }
    
    if( progressPercent == 43 || progressPercent == 59 || progressPercent == 87 ){
        $('#nextBTN').prop('disabled',true);
        $('#completeBTN').prop('disabled',false);
        $('#username-block').show();
    } else {
        $('#nextBTN').prop('disabled',false);
        $('#completeBTN').prop('disabled',true);
    }
}

function fromReload() {
    $('#id_label').removeClass('text-danger');
    $('#progress_bar').removeClass('bg-danger');

    $('#id_label').addClass('text-success');
    $('#progress_bar').addClass('bg-success');

    $('#progress_percent').text('91%');
    $('#progress_bar').attr('aria-valuenow', '91');
    $('#progress_bar').css('width', '91%');

    picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2004.jpg';
    titleCaption = 'c) Enter user details as ‘Mr emr emr’ Enter password ‘emr and then your EMIScode’ and paste in your password you copied from the clip board';
    $('#setup-min-pic').attr('href', picPath );
    $('#setup-full-pic').attr('src', picPath );
    $('#setup-caption').text( titleCaption );
    $('#username-block').show();

    $('#step2-block').show();
    picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2011.png';
    titleCaption = 'g) Click "Activate Application" at the top';
    $('#setup-min-pic_2').attr('href', picPath );
    $('#setup-full-pic_2').attr('src', picPath );
    $('#setup-caption_2').text( titleCaption );

    $('#step3-block').show();
    picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2018.png';
    titleCaption = 'n) Click "OK". Setup is complete';
    $('#setup-min-pic_3').attr('href', picPath );
    $('#setup-full-pic_3').attr('src', picPath );
    $('#setup-caption_3').text( titleCaption );

    $('#step4-block').show();
    $('#main-btn-block').hide();
    $('#secon-btn-block').show();
}

function changeAttr( status ) {
    var picPath, titleCaption;
    var percent = parseInt( $('#progress_bar').attr('aria-valuenow') );
    var aCaption = 'a) Menu > Configuration > Organisation Configuration',
        bCaption = 'b) Click the "Add" button, select "New user"',
        cCaption = 'c) Enter user details as "Mr emr emr" Enter password "emr and then your EMIScode" and paste in your password you copied from the clip board',
        dCaption = 'd) Now you need to assign the correct role for your user. Give "emr emr" the role of "General Medical Practitioner". For the "User Mnemonic" add in your emr+EMIScode as before.',
        eCaption = 'If you have RBAC roles in your surgery, please ensure you add "Mr emr emr" and assign him as "Clinical Practitioner Access Role"',
        aPic = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2002.png',
        bPic = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2003.png',
        cPic = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2004.jpg',
        dPic = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2019.jpg',
        ePic = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2020.jpg'
        ;
    switch( percent ) {
        // Step 1 Control.
        case 35:
            if( status == 'back' ) {
                break;
            }
            $('#setup-min-pic').attr('href', bPic );
            $('#setup-full-pic').attr('src', bPic );
            $('#setup-caption').text( bCaption );
            break;
        case 39:
            if( status == 'next' ){
                $('#setup-min-pic').attr('href', cPic );
                $('#setup-full-pic').attr('src', cPic );
                $('#setup-caption').text( cCaption );
            } else {
                $('#setup-min-pic').attr('href', aPic );
                $('#setup-full-pic').attr('src', aPic );
                $('#setup-caption').text( aCaption );
            }
            break;
        case 43:
            if( status == 'next' ){
                $('#setup-min-pic').attr('href', dPic );
                $('#setup-full-pic').attr('src', dPic );
                $('#setup-caption').text( dCaption );
            } else {
                $('#setup-min-pic').attr('href', bPic );
                $('#setup-full-pic').attr('src', bPic );
                $('#setup-caption').text( bCaption );
            }
            break;
        case 47:
            if( status == 'next' ){
                $('#setup-min-pic').attr('href', ePic );
                $('#setup-full-pic').attr('src', ePic );
                $('#setup-caption').text( eCaption );
            } else {
                $('#setup-min-pic').attr('href', cPic );
                $('#setup-full-pic').attr('src', cPic );
                $('#setup-caption').text( cCaption );
            }
            break;
        case 51:
            $('#setup-min-pic').attr('href', dPic );
            $('#setup-full-pic').attr('src', dPic );
            $('#setup-caption').text( dCaption );
            break;
        // Step 2 Control.
        case 59:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2009.png';
                titleCaption = 'g) Select "Partner API" at the bottom';
                $('#setup-min-pic_2').attr('href', picPath );
                $('#setup-full-pic_2').attr('src', picPath );
                $('#setup-caption_2').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2008.png';
                titleCaption = 'f) Menu > System Tools > EMAS Manager';
                $('#setup-min-pic_2').attr('href', picPath );
                $('#setup-full-pic_2').attr('src', picPath );
                $('#setup-caption_2').text( titleCaption );
            }
            break;
        case 63:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2011.png';
                titleCaption = 'h) Click "Activate Application" at the top';
                $('#setup-min-pic_2').attr('href', picPath );
                $('#setup-full-pic_2').attr('src', picPath );
                $('#setup-caption_2').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2009.png';
                titleCaption = 'g) Select "Partner API" at the bottom';
                $('#setup-min-pic_2').attr('href', picPath );
                $('#setup-full-pic_2').attr('src', picPath );
                $('#setup-caption_2').text( titleCaption );
            }
            break;
        // Step 3 control.
        case 71:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2013.jpg';
                titleCaption = 'i) Find the new user you created and tick the box next to it';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2012.png';
                titleCaption = 'h) Click "Edits Users" button';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
        case 71:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2014.jpg';
                titleCaption = "j) You’ll be asked to enter that password again. Click ok. Then ok again.";
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2013.jpg';
                titleCaption = 'i) Find the new user you created and tick the box next to it';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
        case 75:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2015.png';
                titleCaption = 'k) Click "OK"';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2014.jpg';
                titleCaption = "j) You’ll be asked to enter that password again. Click ok. Then ok again.";
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
        case 79:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2016.png';
                titleCaption = 'l) Click "Login Access" button';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2015.png';
                titleCaption = 'k) Click "OK"';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
        case 83:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2017.jpg';
                titleCaption = 'm) Find the new user you created and tick the boxes to the right of it';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2016.png';
                titleCaption = 'l) Click "Login Access" button';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
        case 87:
            if( status == 'next' ){
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2018.png';
                titleCaption = 'n) Click "OK". Setup is complete';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            } else {
                picPath = '/static/images/emis_setup/Medidata%20-%20Activating%20in%20EMIS%2017.jpg';
                titleCaption = 'm) Find the new user you created and tick the boxes to the right of it';
                $('#setup-min-pic_3').attr('href', picPath );
                $('#setup-full-pic_3').attr('src', picPath );
                $('#setup-caption_3').text( titleCaption );
            }
            break;
    }
}