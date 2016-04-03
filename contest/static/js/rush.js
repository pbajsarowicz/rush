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
 * Checking whether add_contestant form has validation errors.
 */

function validateContestantForm() {
    var form_idx = $('#id_form-TOTAL_FORMS').val();
    var id = 'id_form-' + (parseInt(form_idx) - 1);

    var firstName = document.forms['contestants'][id + '-first_name'].value;
    var lastName = document.forms['contestants'][id + '-last_name'].value;
    var gender = document.forms['contestants'][id + '-gender'].value;
    var age = document.forms['contestants'][id + '-age'].value;
    var school = document.forms['contestants'][id + '-school'].value;
    var styles = document.forms['contestants'][id + '-styles_distances'].value

    var errorMessage = document.createDocumentFragment();
    var paragraph;

    var checkName = RegExp('[A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]{3,}');

    if(!firstName) {
        paragraph = document.createElement('p');
        paragraph.innerHTML = 'Pole <b>Imie</b> nie może być puste.';
        errorMessage.appendChild(paragraph);
    }
    else if (!checkName.test(firstName)) {
        paragraph = document.createElement('p');
        paragraph.appendChild(document.createTextNode('Wprowadzone imie jest nieprawidłowe.'));
        errorMessage.appendChild(paragraph);
    }

    if(!lastName) {
        paragraph = document.createElement('p');
        paragraph.innerHTML = 'Pole <b>Nazwisko</b> nie może być puste.';
        errorMessage.appendChild(paragraph);
    }
    else if (!checkName.test(lastName)) {
        paragraph = document.createElement('p');
        paragraph.appendChild(document.createTextNode('Wprowadzone nazwisko jest nieprawidłowe.'));
        errorMessage.appendChild(paragraph);
    }

    if(gender != 'F' && gender != 'M') {
        paragraph = document.createElement('p');
        paragraph.appendChild(document.createTextNode('Wybierz poprawną płeć.'));
        errorMessage.appendChild(paragraph);
    }

    if(!age) {
        paragraph = document.createElement('p');
        paragraph.innerHTML = 'Pole <b>Wiek</b> nie może być puste.';
        errorMessage.appendChild(paragraph);
    }
    else if(age < minAge || age > maxAge ) {
        paragraph = document.createElement('p');
        paragraph.appendChild(document.createTextNode('Wiek zawodnika nie mieści się ' +
        'w przedziale przeznaczonym dla tego konkursu.'));
        errorMessage.appendChild(paragraph);
    }

    if(!school) {
        paragraph = document.createElement('p');
        paragraph.innerHTML = 'Pole <b>Rodzaj szkoły</b> nie może być puste.';
        errorMessage.appendChild(paragraph);
    }

    if(!styles) {
        paragraph = document.createElement('p');
        paragraph.innerHTML = 'Pole <b>Style i dystanse</b> nie może być puste.';
        errorMessage.appendChild(paragraph);
    }

    $('#errors').html(errorMessage);
    if(paragraph) {
        $('html, body').animate({ scrollTop: 0 });
        return false;
    }
    return true;
}

/*
 * Generates formset. Moreover, handles MaterializeCSS selects.
 */
$('#add_more').click(function() {

    if(!validateContestantForm()) {
        return false;
    }

    $('select').material_select('destroy');

    var form_idx = $('#id_form-TOTAL_FORMS').val();
    $('#id_form-' + (parseInt(form_idx) - 1)).hide();
    $('#formset').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);

    $('select').material_select();
    $('html, body').animate({ scrollTop: 0 });
});


/*
 * Populates modal with contest info.
 */
function getContestInfo(pk) {
    var organizer = '';
    var contact = '';
    var result = ''
    $.ajax({
        url: '/api/v1/contests/' + pk + '/?format=json',
        dataType: 'json',
        success: function(json){
            organizer = json['organizer'];
            if(organizer['phone_number']){
                contact += '<br> Telefon: ' + organizer['phone_number'];
            }
            if(organizer['email']){
                contact += '<br> Email: ' + organizer['email'];
            }
            if(organizer['website']){
                contact += '<br> Strona Internetowa: <a href="' + organizer['website'] + '">' +
                organizer['website'] + '</a>';
            }

            result = 'Data i godzina: ' + json['date'] + '<br> Miejsce: ' + json['place'] +
            '<br> Dla kogo: od ' + json['age_min'] + ' do ' + json['age_max'] + ' lat' +
            '<br> Termin zgłaszania zawodników: ' +  json['deadline'] + '<br> Organizator: ' +
            organizer['name'] + contact + '<br> Opis: ' + json['description'];

            document.getElementById('text' + pk).innerHTML = result;
        }
    });
}

/*
 * Action on document ready.
 */
$(document).ready(function() {
    onClubCodeValidation();
    $('select').material_select();
    $('.modal-trigger').leanModal();
    $('.datetime').mask('99.99.9999 99:99', {placeholder: 'dd.mm.yyyy hh:mm'});
});
