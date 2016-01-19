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
            Materialize.toast('Ups... wystąpił problem', 4000,'',function(){});
        },
        success: function(){
            userRow.remove();
            message = create ? 'Utworzono konto' : 'Odrzucono zgłoszenie';
            Materialize.toast(message, 4000);
        }
    });
}
