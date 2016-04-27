var clubCodeInput = document.getElementById('id_club_code');
var contestantsPreview = document.getElementById('contestants-preview');
var visibleContestFormId = '0';

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
    'use strict';
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
    'use strict';
    if (clubCodeInput && clubCodeInput.value) {
        document.register_form.club_checkbox.checked = true;
        clubCodeInput.className = 'visible';
        clubCodeInput.required = true;
    }
}

/*
 * Checking whether add_contestant form has validation errors.
 */

function validateContestantForm(formID) {
    'use strict';
    var id = 'id_form-' + formID;
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
 * Loads cached form.
 */
function loadCachedContestant(formId) {
    'use strict';
    var contestantForm = document.getElementById('id_form-' + formId);
    var contestantFormList = document.getElementsByClassName('contestant-form');
    var totalForms = parseInt($('#id_form-TOTAL_FORMS').val());
    var isLatestForm = (parseInt(formId - visibleContestFormId) <= 1);

    if(!isLatestForm && !validateContestantForm(visibleContestFormId)) {
        return false;
    }
    updateTextOfContestantPreview(visibleContestFormId);

    for (var i = 0, len = contestantFormList.length; i < len; i++) {
        if (contestantFormList[i].style.display !== 'none') {
            contestantFormList[i].style.display = 'none';
        }
    }

    contestantForm.style = '';
    visibleContestFormId = formId;
    console.log(visibleContestFormId);
}

/*
 * Updates contestant's preview text with value provided in form.
 */
function updateTextOfContestantPreview(formId) {
    'use strict';
    var preview = document.getElementById('preview-' + formId);
    var firstName = document.forms['contestants']['id_form-' + formId + '-first_name'].value;
    var lastName = document.forms['contestants']['id_form-' + formId + '-last_name'].value;

    if (preview) {
        preview.textContent = firstName + ' ' + lastName;
    }
}

/*
 * Appends a new item to the list of added contestans.
 */
function appendToContestantsPreview(formId) {
    'use strict';
    var firstName = document.forms['contestants']['id_form-' + formId + '-first_name'].value;
    var lastName = document.forms['contestants']['id_form-' + formId + '-last_name'].value;
    var elementLi = document.createElement('li');
    var span = document.createElement('span');
    var contestantsPreviewUl = contestantsPreview.getElementsByClassName('collection')[0];

    if (contestantsPreview.className.indexOf('invisible') > -1) {
        contestantsPreview.className = contestantsPreview.className.replace('invisible', '');
    }

    span.className = 'chip';
    span.id = 'preview-' + formId;
    span.addEventListener('click', function() {
        loadCachedContestant(formId);
    }, false);
    span.appendChild(document.createTextNode(firstName + ' ' + lastName));

    elementLi.className = 'collection-item';
    elementLi.appendChild(span);

    contestantsPreviewUl.appendChild(elementLi);
}

/*
 * Generates formset. Moreover, handles MaterializeCSS selects.
 */
$('#add_more').click(function() {
    'use strict';
    var formId = '';

    if(!validateContestantForm(visibleContestFormId)) {
        return false;
    }
    updateTextOfContestantPreview(visibleContestFormId);

    formId = parseInt($('#id_form-TOTAL_FORMS').val());

    $('select').material_select('destroy');

    // Hides visible form
    $('#id_form-' + visibleContestFormId).hide();

    // If visible form is the one with the highest id then appends it to preview list and adds a new form
    // otherwise shows that form.
    if (parseInt(formId - visibleContestFormId) <= 1) {
        appendToContestantsPreview(formId - 1);

        $('#formset').append($('#empty_form').html().replace(/__prefix__/g, formId));
        $('#id_form-' + formId).show();
        $('#id_form-TOTAL_FORMS').val(formId + 1);

        $('html, body').animate({ scrollTop: 0 });
    } else {
        formId -= 1;
        $('#id_form-' + formId).show();
    }
    $('select').material_select();

    // Upon adding new contestant, a visible form is always the one with the highest id number
    visibleContestFormId = formId;
});


/*
 * Populates modal with contest info.
 */
function getContestInfo(pk) {
    'use strict';
    var organizer = '';
    var contact = '';
    var organizer_contact = '';
    var result = '';

    $.ajax({
        url: '/api/v1/contests/' + pk + '/?format=json',
        dataType: 'json',
        success: function(json){
            result = 'Data i godzina: ' + json['date'] + '<br> Miejsce: ' + json['place'] +
            '<br> Dla kogo: od ' + json['age_min'] + ' do ' + json['age_max'] + ' lat' +
            '<br> Termin zgłaszania zawodników: ' +  json['deadline'];

            organizer = json['organizer'];
            if (organizer) {
                organizer_contact = organizer['contact'];
                if (organizer_contact) {
                    if(organizer['phone_number']){
                        contact += '<br> Telefon: ' + organizer_contact['phone_number'];
                    }
                    contact += '<br> Email: ' + organizer_contact['email'];
                    if(organizer_contact['website']){
                        contact += '<br> Strona Internetowa: <a href="' + organizer_contact['website'] + '">' +
                        organizer_contact['website'] + '</a>';
                    }
                }

                result += '<br> Organizator: ' + organizer['name'] + ', ' + contact;
            }

            result += '<br> Opis: ' + (json['description'] ? json['description'] : 'Brak');

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

/*
 * Parsing user data from js to html.
 */
function parseUserData(json) {
    'use strict';
    var fieldsNames = [
        ['Email', 'email'],
        ['Data rejestracji', 'date_joined'],
        ['Klub', 'club'],
        ['Nazwa organizacji', 'organization_name'],
        ['Adres organizacji', 'organization_address']
    ]
    var fragment = document.createDocumentFragment();
    var elementUl = element = document.createElement('ul');
    var elementLi;

    fieldsNames.forEach(function(field) {
        elementLi = document.createElement('li');
        elementLi.appendChild(document.createTextNode(field[0] + ': ' + json[field[1]]));
        elementUl.appendChild(elementLi);
    });
    fragment.appendChild(elementUl);

    return fragment
}

/*
 * Handling user info request and inserting data into html container.
 */
function getUserInfo(user) {
    'use strict';
    if ($('#content' + user).css('display') == 'none' || $('#content' + user).css('display') == 'block') {
        $.ajax({
            url: '/api/v1/users/' + user,
            dataType: 'json',
            success: function(json) {
                user_data = parseUserData(json);

                $('#content' + user).html(user_data);
                $('#content' + user).removeClass('invisible').addClass('inline');
            }
        });
    }
    else {
        $('#content' + user).html('');
        $('#content' + user).removeClass('inline').addClass('invisible');
    }
}

