'use strict';

// Parse additional variables from the DOM element.
const context = JSON.parse(document.getElementById('javascript_context').textContent);

// DOM element selectors
const divOptionOne = document.getElementById('id_option_one');
const divOptionTwo = document.getElementById('id_option_two');
const divTemplateLink = document.getElementById('id_template_link');
const divCodeUpdateForm = document.getElementById('id_code_update_form');
const divFormInvalid = document.getElementById('id_form_invalid');
const fySelectEl = document.getElementById('id_fy');
const ccSelectEl = document.getElementById('id_costCentre');
const budgetAreaTextEl = document.getElementById('id_budgetArea');
const budgetAreaDatalist = document.getElementById('budget_areas_list');

// Click event listeners for the two options.
divOptionOne.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'visible';
  divCodeUpdateForm.style.visibility = 'hidden';
});
divOptionTwo.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'hidden';
  divCodeUpdateForm.style.visibility = 'visible';
});

// Disable the FY select list (defaults to the newest) and budget area text (requires CC to be selected first).
fySelectEl.disabled = true;
budgetAreaTextEl.disabled = true;

// If the filter results table is present, default this div to being visible.
if (divFormInvalid) {
  divTemplateLink.style.visibility = 'hidden';
  divCodeUpdateForm.style.visibility = 'visible';
}

// If the Cost Centre select list changes, update the Budget Area datalist attribute.
ccSelectEl.addEventListener('change', function () {
  budgetAreaTextEl.disabled = true;
  const fy = fySelectEl.value;
  const cc = ccSelectEl.value;
  budgetAreaTextEl.value = null;
  budgetAreaDatalist.innerHTML = '';
  updateBudgetAreaDatalist(fy, cc);
  budgetAreaTextEl.disabled = false;
});

async function updateBudgetAreaDatalist(fy, cc = null) {
  let url = `${context.ajax_ibmdata_budgetarea_url}?financialYear=${fy}&costCentre=${cc}`;

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      const option = document.createElement('option');
      option.value = choice[0];
      budgetAreaDatalist.append(option);
    }
  } catch (error) {
    console.error(error.message);
  }
}
