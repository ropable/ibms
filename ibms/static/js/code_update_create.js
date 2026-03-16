'use strict';

// DOM element selectors
const divOptionOne = document.getElementById('id_option_one');
const divOptionTwo = document.getElementById('id_option_two');
const divTemplateLink = document.getElementById('id_template_link');
const divCodeUpdateForm = document.getElementById('id_code_update_form');
const divFormInvalid = document.getElementById('id_form_invalid');

// Click event listeners for the two options.
divOptionOne.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'visible';
  divCodeUpdateForm.style.visibility = 'hidden';
});
divOptionTwo.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'hidden';
  divCodeUpdateForm.style.visibility = 'visible';
});

// If the filter results table is present, default this div to being visible.
if (divFormInvalid) {
  divTemplateLink.style.visibility = 'hidden';
  divCodeUpdateForm.style.visibility = 'visible';
}
