
// auto redirect when cohort is selected from dropdown
$('#cohort-select').on('change', function(){
  if ($('#cohort-select').val()) {
    window.location.href = "/cohort/" + $('#cohort-select').val();
  }
});