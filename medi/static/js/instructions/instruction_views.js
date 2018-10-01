var status = -1;
var inst_statusDict = {}, user_roleDict = {};
inst_statusDict["All"] = -1;
inst_statusDict["New"] = 0;
inst_statusDict["In Progress"] = 1;
inst_statusDict["Overdue"] = 2;
inst_statusDict["Complete"] = 3;
inst_statusDict["Rejected"] = 4;

user_roleDict["All"] = -1;
user_roleDict["Manager"] = 0;
user_roleDict["GP"] = 1;
user_roleDict["SARS"] = 2;

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

function instructionStatusFilter(selected_status){
    window.location = '/instruction/view_pipeline/?status=' + inst_statusDict[selected_status] + '&type=' + $('#filterInstructionType').val();
}

function userStatusFilter(selected_status){
    window.location = '/accounts/view_users/?status=' + user_roleDict[selected_status] + '&type=' + $('#filterUserType').val();
}

function typeFilter(){
    if(getUrlParameter('status')){
        status = getUrlParameter('status');
    }
    window.location = '/instruction/view_pipeline/?status=' + status + '&type=' + $('#filterInstructionType').val();
}

function userTypeFilter() {
    if(getUrlParameter('status')){
        status = getUrlParameter('status');
    }
    window.location = '/accounts/view_users/?status=' + status + '&type=' + $('#filterUserType').val();
}