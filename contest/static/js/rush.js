var clubCodeInput = document.getElementById('id_club_code');
var contestant;

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
    var userId = userData['id'];
    $.ajax({
        type: action,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            document.getElementById('discard-user-' + userId).onclick = function(){ return false; };
            document.getElementById('create-user-' + userId).onclick = function(){ return false; };
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
        $('label[for="id_club_code"').addClass('visible');
        clubCodeInput.className = 'visible';
        clubCodeInput.required = true;
    } else {
        $('label[for="id_club_code"').removeClass('visible').addClass('invisible');
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
        $('label[for="id_club_code"').removeClass('invisible').addClass('visible');
        document.register_form.club_checkbox.checked = true;
        clubCodeInput.className = 'visible';
        clubCodeInput.required = true;
    }
}

/*
 * Contestant's validation prototype.
 */
function ContestantValidation() {
    'use strict';
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
        'use strict';
        this.validationRaised = false;
    },
    /*
     * Checking whether add_contestant form has validation errors.
     */
    raiseValidation: function(fullFormId, message) {
        'use strict';
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
        'use strict';
        $('#' + fullFormId).attr('class', 'validate valid');
        $('label[for="' + fullFormId + '"]').attr('class', '');
    },
    /*
     * Validates first name.
     */
    validateFirstName: function(formId) {
        'use strict';
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
        'use strict';
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
        'use strict';
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
        'use strict';
        this.age = document.forms['contestants'][formId + '-age'].value;

        if (!this.age) {
            this.raiseValidation(formId + '-age', 'Pole Wiek nie może być puste i może zawierać tylko cyfry.');
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
        'use strict';
        this.school = document.forms['contestants'][formId + '-school'].value;

        if (!this.school) {
            this.raiseValidation(formId + '-school', 'Wybierz rodzaj szkoły.');
        } else {
            this.clearValidation(formId + '-school');
        }
    },
    /*
     * Validates styles and distances.
     */
    validateStylesDistances: function(formId) {
        'use strict';
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
    validateForm: function(formId) {
        'use strict';
        this.initialize();

        var totalForms = document.getElementById('id_form-TOTAL_FORMS').value;
        var id = 'id_form-' + (formId !== undefined ? formId : parseInt(totalForms - 1));

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
 * Contestant prototype.
 */
function Contestant() {
    'use strict';
    this.visibleContestFormId = '0';  // Stores id of the currently visible form.
    this.savedFormsIds = [];
    this.contestantFormList = document.getElementsByClassName('contestant-form');
    this.contestantsPreview = document.getElementById('contestants-preview');
    this.validation = new ContestantValidation();
}

Contestant.prototype = {
    /*
     * Returns currently visible form if any was given as an argument.
     */
    getForm: function(formId) {
        'use strict';
        return formId === undefined ? this.visibleContestFormId : formId;
    },
    /*
     * Checks if given form has been already saved.
     * @default - currently visible form.
     */
    isAlreadySavedForm: function(formId) {
        'use strict';
        var formId = this.getForm(formId);

        return this.savedFormsIds.indexOf(formId) > -1;
    },
    /*
     * Checks if given form is latest in an enumeration.
     */
    isLastForm: function(formId) {
        'use strict';
        var formId = this.getForm(formId);

        return parseInt(this.getTotalForms() - formId) === 1;
    },
    /*
     * Returns value of TOTAL_FORMS.
     */
    getTotalForms: function() {
        'use strict';
        return parseInt(document.getElementById('id_form-TOTAL_FORMS').value);
    },
    /*
     * Removes last form from the set.
     */
    removeLastForm: function() {
        'use strict';
        var totalForms = this.getTotalForms();

        document.getElementById('id_form-' + parseInt(totalForms - 1)).remove()
        document.getElementById('id_form-TOTAL_FORMS').value -= 1;
    },
    /*
     * Loads cached form.
     * Handles the following scenarios upon changing active form from the preview list:
     * 1. If it's not the very last form the validation is ran.
     * 2. If this is the latest form and it's hasn't been saved yet removes it.
     * 3. Otherwise, it updates preview of active form.
     * Finally, clears errors and brings `visibleContestFormId` up-to-date.
     */
    loadCachedContestant: function(formId) {
        'use strict';
        var contestantForm = document.getElementById('id_form-' + formId);
        var totalForms = this.getTotalForms();
        var isLastForm = this.isLastForm();
        var isAlreadySavedForm = this.isAlreadySavedForm();

        if(isAlreadySavedForm && !this.validateForm()) {
            return false;
        } else if (isLastForm && !isAlreadySavedForm) {
            this.removeLastForm();
        } else {
            this.updateTextOfContestantPreview();
        }

        for (var i = 0, len = this.contestantFormList.length; i < len; i++) {
            if (this.contestantFormList[i].style.display !== 'none') {
                this.contestantFormList[i].style.display = 'none';
            }
        }

        contestantForm.style.display = '';
        this.visibleContestFormId = formId;
    },
    /*
     * Updates contestant's preview text with value provided in form.
     */
    updateTextOfContestantPreview: function(formId) {
        'use strict';
        var formId = this.getForm(formId);
        var preview = document.getElementById('preview-' + formId);
        var firstName = document.forms['contestants']['id_form-' + formId + '-first_name'].value;
        var lastName = document.forms['contestants']['id_form-' + formId + '-last_name'].value;
        var contestantName = firstName + ' ' + lastName;

        if (contestantName.length >= 15)
            contestantName = contestantName.substr(0, 15) + '...';

        if (this.contestantsPreview.className.indexOf('invisible') > -1) {
            this.contestantsPreview.className = this.contestantsPreview.className.replace('invisible', '');
        }

        if (preview) {
            preview.textContent = contestantName;
        }
    },
    /*
     * Updates list of currently added forms, which is used to maintain already applied forms.
     */
    updateSavedFromsIds: function(formId) {
        this.savedFormsIds.push(formId);
    },
    /*
     * Appends a new item to the list of added contestans.
     */
    appendToContestantsPreview: function(formId) {
        'use strict';
        var firstName = document.forms['contestants']['id_form-' + formId + '-first_name'].value;
        var lastName = document.forms['contestants']['id_form-' + formId + '-last_name'].value;
        var elementLi = document.createElement('li');
        var span = document.createElement('span');
        var contestantsPreviewUl = this.contestantsPreview.getElementsByClassName('collection')[0];
        var contestant = this;
        var contestantName = firstName + ' ' + lastName;

        if (contestantName.length >= 15)
            contestantName = contestantName.substr(0, 15) + '...';

        if (this.contestantsPreview.className.indexOf('invisible') > -1) {
            this.contestantsPreview.className = this.contestantsPreview.className.replace('invisible', '');
        }

        span.className = 'chip';
        span.id = 'preview-' + formId;

        span.addEventListener('click', function() {
            contestant.loadCachedContestant(formId);
        }, false);
        span.appendChild(document.createTextNode(contestantName));

        elementLi.className = 'collection-item';
        elementLi.appendChild(span);

        contestantsPreviewUl.appendChild(elementLi);
    },
    /*
     * Runs the following scenario:
     * 1. Validates visible form.
     * 2. Appends or updates its preview.
     * 3. Adds a new empty form.
     * 4. Sets a just added form as visible one.
     */
    addNextContestant: function() {
        'use strict';
        var newFormId = this.getTotalForms();

        if(!this.validateForm()) {
            return false;
        }

        $('select').material_select('destroy');
        document.getElementById('id_form-' + this.visibleContestFormId).style.display = 'none';

        if (!this.isAlreadySavedForm()) {
            this.updateSavedFromsIds(this.visibleContestFormId);
            this.appendToContestantsPreview(this.visibleContestFormId);
        } else {
            this.updateTextOfContestantPreview(this.visibleContestFormId);
        }

        $('#formset').append($('#empty_form').html().replace(/__prefix__/g, newFormId));
        document.getElementById('id_form-' + newFormId).style.display = 'inherit';
        document.getElementById('id_form-TOTAL_FORMS').value = parseInt(newFormId + 1);

        $('html, body').animate({ scrollTop: 0 });
        $('select').material_select();

        this.visibleContestFormId = newFormId;
    },
    /*
     * Gets `formId` and runs validation.
     */
    validateForm: function(formId) {
        var formId = this.getForm(formId);

        return this.validation.validateForm(formId);
    }
}

/*
 * Calls a method that handles adding a new form.
 */
$('#add_more').click(function() {
    'use strict';
    contestant.addNextContestant();
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
    contestant = new Contestant();

    onClubCodeValidation();
    $('label[for="id_club_code"').addClass('invisible');
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
    var elementUl = document.createElement('ul');
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
    var user_data;

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

/*
 * Parsing contestant data from js to html.
 */
function parseContestantData(json) {
    'use strict';
    var fieldsNames = [
        ['Imię', 'first_name'],
        ['Nazwisko', 'last_name'],
        ['Płeć', 'gender'],
        ['Wiek', 'age'],
        ['Rodzaj Szkoły', 'school'],
        ['styl i dystans', 'styles_distances']
    ];
    var fragment = document.createDocumentFragment();
    var elementUl = document.createElement('ul');
    var elementLi;

    fieldsNames.forEach(function(field) {
        elementLi = document.createElement('li');
        elementLi.appendChild(document.createTextNode(field[0] + ': ' + json[field[1]]));
        elementUl.appendChild(elementLi);
    });
    fragment.appendChild(elementUl);

    return fragment;
}

/*
 * Handling contestant info request and inserting data into html container.
 */
function getContestantInfo(contestant) {
    'use strict';
    var contestant_data;

    if ($('#content' + contestant).attr('class') == 'invisible') {
        if ($('#content' + contestant).html().length == 0) {
            $.ajax({
                url: '/api/v1/contestants/' + contestant,
                dataType: 'json',
                success: function(json) {
                    contestant_data = parseContestantData(json);
                    $('#content' + contestant).html(contestant_data);
                }
            });
        }
        $('#content' + contestant).removeClass('invisible').addClass('inline');
    } else {
        $('#content' + contestant).removeClass('inline').addClass('invisible');
    }
}
/*
 Deletes contestant.
 */
function removeContestant(userId) {
    'use strict';
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        type: 'DELETE',
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        url: '/api/v1/contestants/' + userId,
        error: function() {
            Materialize.toast('Ups... wystąpił problem', 4000);
        },
        success: function() {
            location.reload();
        }
    });
}
