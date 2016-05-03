var clubCodeInput = document.getElementById('id_club_code');
var contestantValidation;

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


function ContestantValidation() {
    this.validationRaised = false;
    this.firstName = '';
    this.lastName = '';
    this.gender = '';
    this.age = '';
    this.school = '';
    this.stylesDistances = '';

    this.checkName = RegExp('[A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]{3,}');
}

ContestantValidation.prototype = {
    /*
     * Initializes validation.
     */
    initialize: function() {
        this.validationRaised = false;
    },
    /*
     * Checking whether add_contestant form has validation errors.
     */
    raiseValidation: function(fullFormId, message) {
        var message = message !== undefined ? message : 'To pole zawiera niepoprawną wartość';

        $('#' + fullFormId).attr('class', 'validate invalid');
        $('label[for="' + fullFormId + '"]')
            .attr('data-error', message)
            .attr('class', 'error-message');

        this.validationRaised = true;
    },
    /*
     * Checking whether add_contestant form has validation errors.
     */
    clearValidation: function(fullFormId) {
        $('#' + fullFormId).attr('class', 'validate valid');
        $('label[for="' + fullFormId + '"]').attr('class', '');
    },
    /*
     * Validates first name.
     */
    validateFirstName: function(formId) {
        this.firstName = document.forms['contestants'][formId + '-first_name'].value;

        if(!this.firstName) {
            this.raiseValidation(formId + '-first_name', 'Pole Imię nie może być puste.');
        }
        else if (!this.checkName.test(this.firstName)) {
            this.raiseValidation(formId + '-first_name', 'Wprowadzone imię jest nieprawidłowe.');
        } else {
            this.clearValidation(formId + '-first_name');
        }
    },
    /*
     * Validates last name.
     */
    validateLastName: function(formId) {
        this.lastName = document.forms['contestants'][formId + '-last_name'].value;

        if (!this.lastName) {
            this.raiseValidation(formId + '-last_name', 'Pole Nazwisko nie może być puste.');
        }
        else if (!this.checkName.test(this.lastName)) {
            this.raiseValidation(formId + '-last_name', 'Wprowadzone nazwisko jest nieprawidłowe.');
        } else {
            this.clearValidation(formId + '-last_name');
        }
    },
    /*
     * Validates gender.
     */
    validateGender: function(formId) {
        this.gender = document.forms['contestants'][formId + '-gender'].value;

        if(this.gender != 'F' && this.gender != 'M') {
            this.raiseValidation(formId + '-gender', 'Wybierz płeć.');
        } else {
            this.clearValidation(formId + '-gender');
        }
    },
    /*
     * Validates age.
     */
    validateAge: function(formId) {
        this.age = document.forms['contestants'][formId + '-age'].value;

        if (!this.age) {
            this.raiseValidation(formId + '-age', 'Pole Wiek nie może być puste.');
        }
        else if (this.age < minAge || this.age > maxAge ) {
            this.raiseValidation(formId + '-age', 'Wiek zawodnika nie mieści się w przedziale przeznaczonym dla tego konkursu.');
        } else {
            this.clearValidation(formId + '-age');
        }
    },
    /*
     * Validates school.
     */
    validateSchool: function(formId) {
        this.school = document.forms['contestants'][formId + '-school'].value;

        if (!this.school) {
            this.raiseValidation(formId + '-school', 'Pole Rodzaj Szkoły nie może być puste.');
        } else {
            this.clearValidation(formId + '-school');
        }
    },
    /*
     * Validates styles and distances.
     */
    validateStylesDistances: function(formId) {
        this.stylesDistances = document.forms['contestants'][formId + '-styles_distances'].value;

        if (!this.stylesDistances) {
            this.raiseValidation(formId + '-styles_distances', 'Pole Style i dystanse nie może być puste.');
        } else {
            this.clearValidation(formId + '-styles_distances');
        }
    },
    /*
     * Checking whether add_contestant form has validation errors.
     */
    validateContestantForm: function() {
        this.initialize();

        var form_idx = $('#id_form-TOTAL_FORMS').val();
        var id = 'id_form-' + (parseInt(form_idx) - 1);
        var validators = [
            'validateFirstName', 'validateLastName', 'validateGender',
            'validateAge', 'validateSchool', 'validateStylesDistances'
        ]

        for (var i = 0, len = validators.length ; i < len; i++) {
            this[validators[i]](id);
        }

        return !this.validationRaised;
    }
}

/*
 * Generates formset. Moreover, handles MaterializeCSS selects.
 */
$('#add_more').click(function() {
    if(!contestantValidation.validateContestantForm()) {
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
    contestantValidation = new ContestantValidation();

    onClubCodeValidation();
    $('select').material_select();
    $('.modal-trigger').leanModal();
    $('.datetime').mask('99.99.9999 99:99', {placeholder: 'dd.mm.yyyy hh:mm'});
});

/*
 * Parsing user data from js to html.
 */
function parseUserData(json) {
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
    })
    fragment.appendChild(elementUl);

    return fragment
}

/*
 * Handling user info request and inserting data into html container.
 */
function getUserInfo(user) {
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

