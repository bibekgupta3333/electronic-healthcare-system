function render_permission() {
  var totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
  var htmlTH = '';
  for(var i = 1; i<=totalForms; i++) {
    var children = $('#id_form-' + (i-1) + '-permissions li label');
    var html = '';
    children.map(function(index, el) {
      if(i==1){
        htmlTH += '<th>' + el.innerText + '</th>';
      }
      el.innerHTML = el.innerHTML.replace(el.innerText,'');
      html += '<td>' + el.innerHTML + '</td>';
    });
    $('#permissionTD_' + i).replaceWith(html);
  }
  $('#permissionTH').replaceWith(htmlTH);
}
