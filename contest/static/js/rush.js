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
 * Contestant's validation prototype.
 */
function ContestantValidation() {
    'use strict';
    this.validationRaised = false;
    this.firstName = '';
    this.lastName = '';
    this.gender = '';
    this.yearOfBirth = '';
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
    validateYearOfBirth: function(formId) {
        'use strict';
        this.yearOfBirth = document.forms['contestants'][formId + '-year_of_birth'].value;

        if (!this.yearOfBirth) {
            this.raiseValidation(formId + '-year_of_birth', 'Pole Wiek nie może być puste i może zawierać tylko cyfry.');
        }
        else if (this.yearOfBirth  < lowestYear || this.yearOfBirth  > highestYear ) {
            this.raiseValidation(formId + '-year_of_birth', 'Wiek zawodnika nie mieści się w przedziale przeznaczonym dla tego konkursu.');
        } else {
            this.clearValidation(formId + '-year_of_birth');
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
     * Validates school/club name.
     */
    validateOrganization: function(formId) {
        'use strict';
        this.stylesDistances = document.forms['contestants'][formId + '-organization'].value;

        if (!this.stylesDistances) {
            this.raiseValidation(formId + '-organization', 'Pole Klub/Szkoła nie może być puste.');
        } else {
            this.clearValidation(formId + '-organization');
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
            'validateYearOfBirth',
        ];

        if (!isIndividualContestant) {
            validators.push('validateSchool', 'validateOrganization');
        }

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
     * Prepares a previewed value of contestant name (if too long - truncates the original one).
     */
    getPreviewContestantName: function(firstName, lastName) {
        'use strict';
        var contestantName = firstName + ' ' + lastName;

        if (contestantName.length >= 15) {
            return contestantName.substr(0, 15) + '...';
        }
        return contestantName;
    },
    /*
     * Shows a bar which represents a preview of already added contestants.
     */
    showPreviewBar: function() {
        'use strict';
        if (this.contestantsPreview.className.indexOf('invisible') > -1) {
            this.contestantsPreview.className = this.contestantsPreview.className.replace('invisible', '');
        }
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
        var contestantName = this.getPreviewContestantName(firstName, lastName);

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
        var contestantName = this.getPreviewContestantName(firstName, lastName);

        this.showPreviewBar();

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
        if (isIndividualContestant) {
            return false;
        }

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
function nextContestant(prefix) {
    'use strict';
    if (checkStyles(prefix)) {
        contestant.addNextContestant();
    }
}

/*
 * Calls a method that handles validating given styles.
 */
$('#add_more').click(function() {
    'use strict';
    $("a[id^='validation-start']").get(-2).click();
});

/*
 * Checks last contestant on submitting form.
 */
$('#submit_form').click(function() {
    'use strict';
    return checkStyles('form-' + ($("div[id^='id_form']").length - 2));
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
    var files = '';
    var url = '';
    var file_name = '';
    var file_number = 0;

    $.ajax({
        url: '/api/v1/contests/' + pk + '/?format=json',
        dataType: 'json',
        success: function(json) {
            result = 'Nazwa zawodów: ' + json['name'] + '<br> Data i godzina: ' + json['date'] + '<br> Miejsce: ' + json['place'] +
            '<br> Dla kogo: od rocznika ' + json['lowest_year'] + ' do ' + json['highest_year'] +
            '<br> Termin zgłaszania zawodników: ' +  json['deadline'] + '<br> Pliki: ';

            files = json['files']
            for (var i = 0, len = files.length ; i < len; i++) {
                result += '<br><a href="' + files[i].url + '"' + 'target="_blank" download>' + files[i].name + '</a>';
            }

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

    $('select').material_select();
    $('.modal-trigger').leanModal();
    $('.datetime').mask('99.99.9999 99:99', {placeholder: 'dd.mm.yyyy hh:mm'});

    if (document.querySelector('.representative:checked')) {
        document.querySelector('.representative:checked').click();
    }
});

/*
 * Handles representative on registration.
 */
function changeRepresentative(option) {
    'use strict';
    var fieldType = option.value;
    var card= document.getElementById('representative-card');
    var cardTitle= document.getElementById('representative-card-title');
    var clubCodeElement= document.getElementById('club_code-element');
    var registrationButton= document.getElementById('registration-button');
    var organizationNameInput= document.getElementById('id_organization_name');
    var organizationAddressInput= document.getElementById('id_organization_address');
    var clubCodeInput= document.getElementById('id_club_code');

    if (fieldType === 'SCHOOL') {
        cardTitle.innerHTML = 'Podaj dane szkoły';
        clubCodeElement.className = 'row invisible';
        registrationButton.innerHTML = 'Wyślij zapytanie o konto';

        organizationNameInput.required = true;
        organizationAddressInput.required = true;
        clubCodeInput.required = false;

        if (card.className.indexOf('invisible') !== -1) {
            card.className = card.className.replace(/\binvisible\b/,'');
        }
    } else if (fieldType === 'CLUB') {
        cardTitle.innerHTML = 'Podaj dane klubu';
        clubCodeElement.className = 'row';
        registrationButton.innerHTML = 'Wyślij zapytanie o konto';

        organizationNameInput.required = true;
        organizationAddressInput.required = true;
        clubCodeInput.required = true;

        if (card.className.indexOf('invisible') !== -1) {
            card.className =  card.className.replace(/\binvisible\b/,'');
        }
    } else {
        registrationButton.innerHTML = 'Zarejestruj się';

        organizationNameInput.required = false;
        organizationAddressInput.required = false;
        clubCodeInput.required = false;

        if (card.className.indexOf('invisible') === -1) {
            card.className += ' invisible';
        }
    }
}

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
        ['Wiek', 'year_of_birth'],
        ['Rodzaj Szkoły', 'school'],
        ['Styl i dystans', 'style']
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

/*
 * Show styles input.
 */
function showStyles(styleName) {
    'use strict';
    switch (styleName) {
        case 'dowolny':
            if ($('#dowolny').is(':checked')) {
                $('#dowolny-styles').removeClass('invisible');
            } else {
                $('#dowolny-styles').addClass('invisible');
                ['D25', 'D50', 'D100', 'D200', 'D400', 'D800', 'D1500'].forEach(function(item) {
                    $('#' + item).attr('checked', false);
                });
            }
            break;
        case 'grzbietowy':
            if ($('#grzbietowy').is(':checked')) {
                $('#grzbietowy-styles').removeClass('invisible');
            } else {
                $('#grzbietowy-styles').addClass('invisible');
                ['G25', 'G50', 'G100', 'G200'].forEach(function(item) {
                    $('#' + item).attr('checked', false);
                });
            }
            break;
        case 'klasyczny':
            if ($('#klasyczny').is(':checked')) {
                $('#klasyczny-styles').removeClass('invisible');
            } else {
                $('#klasyczny-styles').addClass('invisible');
                ['K25', 'K50', 'K100', 'K200'].forEach(function(item) {
                    $('#' + item).attr('checked', false);
                });
            }
            break;
        case 'motylkowy':
            if ($('#motylkowy').is(':checked')) {
                $('#motylkowy-styles').removeClass('invisible');
            } else {
                $('#motylkowy-styles').addClass('invisible');
                ['M25', 'M50', 'M100', 'M200'].forEach(function(item) {
                    $('#' + item).attr('checked', false);
                });
            }
            break;
        case 'zmienny':
            if ($('#zmienny').is(':checked')) {
                $('#zmienny-styles').removeClass('invisible');
            } else {
                $('#zmienny-styles').addClass('invisible');
                ['Z100', 'Z200'].forEach(function(item) {
                    $('#' + item).attr('checked', false);
                });
            }
    }
}

/*
 * Validate given styles when adding contest.
 */
function validateStyles() {
    'use strict';
    var errorMessage;
    var isValidated = true;
    if (
        !($('#dowolny').is(':checked') || $('#grzbietowy').is(':checked') ||
        $('#klasyczny').is(':checked') || $('#motylkowy').is(':checked') ||
        $('#zmienny').is(':checked'))
    ) {
        if ($('#style-error').length === 0) {
        	errorMessage = 'Co najmniej jeden styl musi zostać wybrany.';
            $('#style').after('<p class="errorlist" id="style-error">' + errorMessage + '</p>');
        }
        return false;
    }

    if ($('#dowolny').is(':checked')) {
        if (
            !($('#D25').is(':checked') || $('#D50').is(':checked') ||
            $('#D100').is(':checked') || $('#D200').is(':checked') ||
            $('#D400').is(':checked') || $('#D800').is(':checked') ||
            $('#D1500').is(':checked'))
        ) {
            errorMessage = 'Nie wybrano dystansu.';
            $('label[for="dowolny"]').html(
                'Dowolny <span class="errorlist" style="padding-left: 4em;">' + errorMessage + '</span>'
            );
            isValidated = false;
        }
        else {
            $('label[for="dowolny"]').html('Dowolny');
        }
    }

    if ($('#grzbietowy').is(':checked')) {
        if (
            !($('#G25').is(':checked') || $('#G50').is(':checked') ||
            $('#G100').is(':checked') || $('#G200').is(':checked'))
        ) {
            errorMessage = 'Nie wybrano dystansu.';
            $('label[for="grzbietowy"]').html(
                'Grzbietowy <span class="errorlist" style="padding-left: 4em;">' + errorMessage + '</span>'
            );
            isValidated = false;
        }
        else {
            $('label[for="grzbietowy"]').html('Grzbietowy');
        }
    }

    if ($('#klasyczny').is(':checked')) {
        if (
            !($('#K25').is(':checked') || $('#K50').is(':checked') ||
            $('#K100').is(':checked') || $('#K200').is(':checked'))
        ) {
            errorMessage = 'Nie wybrano dystansu.';
            $('label[for="klasyczny"]').html(
                'Klasyczny <span class="errorlist" style="padding-left: 4em;">' + errorMessage + '</span>'
            );
            isValidated = false;
        }
        else {
            $('label[for="klasyczny"]').html('Klasyczny');
        }
    }

    if ($('#motylkowy').is(':checked')) {
        if (
            !($('#M25').is(':checked') || $('#M50').is(':checked') ||
            $('#M100').is(':checked') || $('#M200').is(':checked'))
        ) {
            errorMessage = 'Nie wybrano dystansu.';
            $('label[for="motylkowy"]').html(
                'Motylkowy <span class="errorlist" style="padding-left: 4em;">' + errorMessage + '</span>'
            );
            isValidated = false;
        }
        else {
            $('label[for="motylkowy"]').html('Motylkowy');
        }
    }

    if ($('#zmienny').is(':checked')) {
        if (!($('#Z100').is(':checked') || $('#Z200').is(':checked'))) {
            errorMessage = 'Nie wybrano dystansu.';
            $('label[for="zmienny"]').html(
                'Zmienny <span class="errorlist" style="padding-left: 4em;">' + errorMessage + '</span>'
            );
            isValidated = false;
        }
        else {
            $('label[for="zmienny"]').html('Zmienny');
        }
    }

    if (isValidated) {
        var styles = [
            'D25', 'D50', 'D100', 'D200', 'D400', 'D800', 'D1500', 'G25', 'G50', 'G100', 'G200',
            'K25', 'K50', 'K100', 'K200', 'M25', 'M50', 'M100', 'M200', 'Z100', 'Z200'
        ];
        var result = '';
        styles.forEach(function(item) {
            if ($('#' + item).is(':checked')) {
                result += ',' + item;
            }
        });
        $('#styles-summary').val('');
        $('#styles-summary').val(result);
        return true;
    }
    return false;
}

/*
 * Check if user took at least 1 distance (add_contestant form).
 */
function checkStyles(prefix) {
    'use strict';
    var result = '';
    $('.distance_' + prefix).each(function() {
        if ($(this).is(':checked')) {
            result += ',' + (this.id).split('_', 1);
        }
    });
    if (result) {
        $('#id_' + prefix + '-styles').val(result);
        $('#distance-error').remove();
        return true;
    }
    else {
        if ($('#distance-error').length === 0) {
            $('#validation-start_' + prefix).before('<span class="errorlist" id="distance-error">Nie wybrano żadnego dystansu.</span>');
        }
        return false;
    }
}

/*
 * Check if user took at least 1 distance (edit_contestant form).
 */
function checkEditedStyles() {
    'use strict';
    var result = '';
    $('.distance').each(function() {
        if ($(this).is(':checked')) {
            result += ',' + this.id
        }
    });
    if (result) {
        $('#id_styles').val('');
        $('#id_styles').val(result.substr(1));
        $('#distance-error').remove();
        return true;
    }
    else {
        if ($('#distance-error').length === 0) {
            $('#style').after('<span class="errorlist" id="distance-error">Nie wybrano żadnego dystansu.</span>');
        }
        return false;
    }
}
