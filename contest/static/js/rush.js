var clubCodeInput = document.getElementById('id_club_code');

/*
 * Creates an account.
 */
function manageUser(user, create) {
    'use strict';
    var action = create ? 'POST' : 'DELETE';
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var message = '';
    var userData = JSON.parse(user);
    var userName = userData['first_name'] + ' ' + userData['last_name'];
    var userRow = $('#user-' + userData['id']);

    $.ajax({
        type: action,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        url: '/administrator/konta/' + userData['id'],
        error: function(){
            Materialize.toast('Ups... wystąpił problem', 4000);
        },
        success: function(){
            userRow.remove();

            message = create ? userName + ': utworzono konto ' : userName + ': odrzucono zgłoszenie';
            Materialize.toast(message, 4000);
        }
    });
}

/*
 * Hides club code input.
 */
function hideClubCode() {
    if (document.register_form.club_checkbox.checked) {
        clubCodeInput.className = 'visible';
        clubCodeInput.required = true;
    } else {
        clubCodeInput.className = 'invisible';
        clubCodeInput.required = false;
        clubCodeInput.value = '';
    }
}

/*
 * Supports initialization of club code in case of validation errors appear.
 */
    function onClubCodeValidation() {
        if (clubCodeInput && clubCodeInput.value) {
            document.register_form.club_checkbox.checked = true;
            clubCodeInput.className = 'visible';
            clubCodeInput.required = true;
        }
    }

/*
 * Action on document ready.
 */
$(document).ready(function() {
    onClubCodeValidation();
    $('select').material_select();
});

/*
 * Action after clicking 'szczegoly' on main page
 */
$(document).ready(function(){
    // the "href" attribute of .modal-trigger must specify the modal ID that wants to be triggered
    $('.modal-trigger').leanModal();
});

function getContestInfo(pk) {
    $.ajax({
        url: '/api/contests/' + pk + '/?format=json',
        dataType: 'json',
        success: function(json, x, y){
            var organizer = json['organizer'];
            var contact = '';
            if( organizer['phone_number']){
                contact += '<br> Telefon: ' + organizer['phone_number'];
            }
            if( organizer['email']){
                contact += '<br> Email: ' + organizer['email'];
            }
            if( organizer['website']){
                contact += '<br> Strona Internetowa: <a href="'+organizer['website']+'">' + organizer['website'] + '</a>'
            }

            var result = 'Data i godzina: ' + json['date'].substr(0, 10) + ' ' + json['date'].substr(11, 8) +
            '<br> Miejsce: ' + json['place'] + '<br> Dla kogo: ' + json['for_who'] + '<br> Termin zgłaszania zawodników: ' +
            json['deadline'].substr(0, 10) + ' ' + json['deadline'].substr(11, 8) + '<br> Organizator: ' +
            organizer['name'] + contact + '<br> Opis: ' + json['description'];

            document.getElementById('text'+pk).innerHTML = result
        }
    });
}
