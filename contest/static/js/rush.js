/*
 * Creates an account.
 */
function manageUser(userId, create) {
    'use strict';
    var action = create ? 'POST' : 'DELETE';
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var data = {'csrfmiddlewaretoken': csrfToken};
    var message = '';
    var userRow = $('#user-' + userId);

    $.ajax({
        type: action,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        url: '/administrator/konta/' + userId,
        error: function(){
            Materialize.toast('Ups... wystąpił problem', 4000);
        },
        success: function(){
            userRow.remove();
            message = create ? 'Utworzono konto' : 'Odrzucono zgłoszenie';
            Materialize.toast(message, 4000);
        }
    });
}


function hide() {
    if (document.register_form.club_checkbox.checked) {
        document.getElementById('id_club_code').style.display = "inline";
        document.getElementById('id_club_code').required = true;
    } else {
        document.getElementById('id_club_code').style.display = 'none';
        document.getElementById('id_club_code').required = false;
    }
}
