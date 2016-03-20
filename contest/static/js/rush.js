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

    var firstName = document.forms['contestants'][id+ '-first_name'].value;
    var lastName = document.forms['contestants'][id + '-last_name'].value;
    var gender = document.forms['contestants'][id + '-gender'].value;
    var age = document.forms['contestants'][id + '-age'].value;
    var school = document.forms['contestants'][id + '-school'].value;
    var styles = document.forms['contestants'][id + '-styles_distances'].value
    var errorMessage = '';

    var checkName = RegExp('[A-Za-z]{3,}');

    if(firstName == null || firstName == '')
        errorMessage += '<p>Pole <b>Imie</b> nie może być puste.</p>';
    else if (!checkName.test(firstName))
        errorMessage += '<p>Wprowadzone imie jest nieprawidłowe.</p>';

    if(lastName == null || lastName == '')
        errorMessage += '<p>Pole <b>Nazwisko</b> nie może być puste.</p>';
    else if (!checkName.test(lastName))
        errorMessage += '<p>Wprowadzone nazwisko jest nieprawidłowe.</p>';

    if(gender != 'F' && gender != 'M')
        errorMessage += '<p>Wybierz poprawną płeć.</p>';

    if(age == null || age == '')
        errorMessage += '<p>Pole <b>Wiek</b> nie może być puste.</p>';
    else if(age < minAge || age > maxAge )
        errorMessage += '<p>Wiek zawodnika nie mieści się w przedziale ' +
        'przeznaczonym dla tego konkursu.</p>';

    if(school == null || school == '')
        errorMessage += '<p>Pole <b>Rodzaj szkoły</b> nie może być puste.</p>';

    if(styles == null || styles == '')
        errorMessage += '<p>Pole <b>Style i dystanse</b> nie może być puste.</p>';

    if(errorMessage){
        $('#errors').html(errorMessage);
        $('html, body').animate({ scrollTop: 0 });
        return false;
    }
    else
        $('#errors').html('');
    return true
}

/*
 * Generates formset. Moreover, handles MaterializeCSS selects.
 */
$('#add_more').click(function() {

    if(validateContestantForm() == false)
        return false

    $('select').material_select('destroy');

    var form_idx = $('#id_form-TOTAL_FORMS').val();
    var id = 'id_form-' + (parseInt(form_idx) - 1);
    $('#' + id).hide();
    $('#formset').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);

    $('select').material_select();
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
});
