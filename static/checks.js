function passCheck() {

  if ($('#password').val() == $('#confirmation').val()) {
    $('#message').html('Confirmation and password match').css('color', 'green');
  } else
    $('#message').html('Confirmation does not match password').css('color', 'red');

}
