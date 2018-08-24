var status = -1;
var statusDict = {};
statusDict["All"] = -1;
statusDict["New"] = 0;
statusDict["In Progress"] = 1;
statusDict["Overdue"] = 2;
statusDict["Complete"] = 3;
statusDict["Rejected"] = 4;

function filterGlobal () {
    $('#instructionsTable').DataTable().search(
        $('#search').val(),
    ).draw();
}

function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}

function getObjectKeyByValue(obj, val){
    for(var key in obj){
        if(obj[key] == val) return key;
    }
}

function statusFilter(selected_status){
    window.location = '/instruction/view_data/?status=' + statusDict[selected_status] + '&type=' + $('#filterInstructionType').val();
}

function typeFilter(){
    if(getUrlParameter('status')){
        status = getUrlParameter('status');
    }
    window.location = '/instruction/view_data/?status=' + status + '&type=' + $('#filterInstructionType').val();
}