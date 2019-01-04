
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
        "<img src='/static/images/emis_setup/Spin-1s-40px.gif' style='height: 50px; width: 50px;'/> Checking..."
    );
    setTimeout(function () {
        $.ajax({
            url: url,
            success: function (data) {
                if(data["status"] == 400){
                    $(".btn-checkSetup").hide();
                    $(".emisSetupSuccess").removeClass("d-none");
                    setTimeout(function () {
                        document.location.href = "/onboarding/emr-setup-final/" + data["practice_code"]
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