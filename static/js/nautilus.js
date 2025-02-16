/*
All frontend animations are done here. This includes:
- Form field animation: Accomplished via event bubbling using closest() to only animate the field within the used form
- Adding addtional evolution forms via 'add new form' button
- Charts: Chart.js package is used for schema visualisation as scatter plot as well as evolution operations per transaction
 */

/*
-----------------------------------------------------------------------------------------
Add and Remove new evolution form
-----------------------------------------------------------------------------------------
 */

// Source: https://schinckel.net/2017/02/05/django-dynamic-formsets/
function Formset(element) {

    if (!(this instanceof Formset)) {
        return new Formset(element);
    }
    let formset = this;
    let emptyForm = element.querySelector('.empty-form').firstElementChild;
    let formsList = element.querySelector('.forms');
    let listButton = element.querySelector('.controls');
    let initialForms = element.querySelector('[name$=INITIAL_FORMS]');
    //let initialForms = "{{ formset.initial_form_count }}";
    let totalForms = element.querySelector('[name$=TOTAL_FORMS]');
    //let totalForms = "{{ formset.total_form_count }}";
    let prefix = initialForms.name.replace(/INITIAL_FORMS$/, '');

    function addForm(event) {
        // Duplicate empty form.
        let newForm = emptyForm.cloneNode(true);
        // Update all references to __prefix__ in the elements names.
        renumberForm(newForm, '__prefix__', totalForms.value);
        // Make it able to delete itself.
        newForm.querySelector('[data-formset-remove-form]').addEventListener('click', removeForm);
        // Append the new form to the formsList.
        listButton.insertAdjacentElement('beforebegin', newForm);
        element.dispatchEvent(new CustomEvent('add-form.formset', {
            detail: {
                form: newForm,
                formset: formset
            }
        }));
        // Update the totalForms.value
        totalForms.value = Number(totalForms.value) + 1;
    }

    function getForm(target) {
        let parent = target.parentElement;
        if (parent == document) {
            return null;
        }
        if (parent == formsList) {
            return target;
        }
        return getForm(parent);
    }

    function renumberForm(form, oldValue, newValue) {
        //let prefix = "{{ formset.prefix }}";
        let matchValue = prefix + oldValue.toString();
        let match = new RegExp(matchValue);
        let replace = prefix + newValue.toString();

        ['name', 'id', 'for'].forEach(function (attr) {
            form.querySelectorAll('[' + attr + '*=' + matchValue + ']').forEach(function (el) {
                el.setAttribute(attr, el.getAttribute(attr).replace(match, replace));
            });
        });

        element.dispatchEvent(new CustomEvent('renumber-form.formset', {
            detail: {
                form: form,
                oldValue: oldValue,
                newValue: newValue,
                formset: formset
            }
        }));
    }

    function removeForm(event) {
        // Find the form "row": the child of formsList that is the parent of the element
        // that triggered this event.
        let formToRemove = getForm(event.target);
        // Renumber the rows that come after us.
        let nextElement = formToRemove.nextElementSibling;
        let nextElementIndex = Array.prototype.indexOf.call(formsList.children, formToRemove);
        while (nextElement) {
            renumberForm(nextElement, nextElementIndex + 1, nextElementIndex);
            nextElement = nextElement.nextElementSibling;
            nextElementIndex = nextElementIndex + 1;
        }
        // Remove this row.
        formToRemove.remove();
        element.dispatchEvent(new CustomEvent('remove-form.formset', {
            detail: {
                form: formToRemove,
                formset: formset
            }
        }));
        // Decrement the management form's count.
        totalForms.value = Number(totalForms.value) - 1;
    }

    element.querySelector('[data-formset-add-form]').addEventListener('click', addForm);
    element.formset = this;

    element.dispatchEvent(new CustomEvent('init.formset', {
        detail: {
            formset: this
        }
    }));

    this.addForm = addForm;
}

new Formset(document.querySelector('#id-evo-op-form'));


/*
-----------------------------------------------------------------------------------------
Evolution Form Animation via event bubbling
-----------------------------------------------------------------------------------------
 */

// ToDo: Add all ids of all fields and labels here
let id_evo_op_field = document.querySelectorAll('[id^="id_form-"][id$="-evo_op"]');
let id_type_field = document.querySelectorAll('[id^="id_form-"][id$="-type"]');
let id_with_field = document.querySelectorAll('[id^="id_form-"][id$="-with_field"]');
let form_container = document.querySelector("form");
let id_of_evo_op_formset = document.getElementById("id-evo-op-form");


// ToDo: Remake all animations for all fields and labels in evo-op form!!!
// Animations for all fields of evo_op_form
// Event bubbling - through closest inside of fieldset tag - used to animate fields of all forms
// Source: https://davidwalsh.name/event-delegate
// Get the parent DIV, add click listener...
id_of_evo_op_formset.addEventListener("change", function (e) {
    // select closest fieldset tag to changed element and select closest (which also is the only) id inside this fieldset
    // aim: select elements by ids inside of fieldset bubble (for event bubbling)
    // e.target = the clicked element
    let evo_op_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-evo_op"]');
    let join_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-join_options"]')
    let type_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-type"]');
    let from_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-from_field"]');
    let feature_text_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-feature_text_field"]');
    let with_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-with_field"]');
    let with_feature_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-with_feature_text_field"]');
    let property_key_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-property_key_field"]');
    let property_value_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-property_value_field"]');
    let initial_rel_start_node_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-initial_rel_start_node_field"]');
    let initial_rel_start_node_label_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-initial_rel_start_node_label_field"]');
    let initial_rel_end_node_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-initial_rel_end_node_field"]');
    let initial_rel_end_node_label_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-initial_rel_end_node_label_field"]');
    let to_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-to_field"]');
    let copy_with_rels_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-copy_with_rels_field"]');
    let rename_to_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-rename_to_field"]');
    let split_at_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-split_at_field"]');
    let start_node_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-start_node_field"]');
    let start_node_label_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-start_node_label_field"]');
    let start_node_prop_key_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-start_node_property_key_field"]');
    let end_node_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-end_node_field"]');
    let end_node_label_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-end_node_label_field"]');
    let end_node_prop_key_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-end_node_property_key_field"]');
    let ingoing_rel_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-ingoing_rel_field"]');
    let outgoing_rel_div = e.target.closest('fieldset').querySelector('[id^="div_id_form-"][id$="-outgoing_rel_field"]');


    // select labels
    let feature_text_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-feature_text_field"]');
    let with_feature_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-with_feature_text_field"]');
    let property_value_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-property_value_field"]');
    let start_node_label_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-start_node_label_field"]');
    let end_node_label_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-end_node_label_field"]');
    let ingoing_rel_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-ingoing_rel_field"]');
    let outgoing_rel_label = e.target.closest('fieldset').querySelector('label[for^="id_form-"][for$="-outgoing_rel_field"]');

    // select input fields
    let evo_op_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-evo_op"]');
    let join_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-join_options"]');
    let type_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-type"]');
    let from_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-from_field"]');
    let feature_text_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-feature_text_field"]');
    let with_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-with_field"]');
    let with_feature_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-with_feature_text_field"]');
    let property_key_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-property_key_field"]');
    let property_value_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-property_value_field"]');
    let initial_rel_start_node_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-initial_rel_start_node_field"]');
    let initial_rel_start_node_label_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-initial_rel_start_node_label_field"]');
    let initial_rel_end_node_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-initial_rel_end_node_field"]');
    let initial_rel_end_node_label_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-initial_rel_end_node_label_field"]');
    let to_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-to_field"]');
    let copy_with_rels_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-copy_with_rels_field"]');
    let rename_to_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-rename_to_field"]');
    let split_at_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-split_at_field"]');
    let start_node_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-start_node_field"]');
    let start_node_label_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-start_node_label_field"]');
    let start_node_prop_key_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-start_node_property_key_field"]');
    let end_node_field = e.target.closest('fieldset').querySelector('select[id^="id_form-"][id$="-end_node_field"]');
    let end_node_label_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-end_node_label_field"]');
    let end_node_prop_key_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-end_node_property_key_field"]');
    let ingoing_rel_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-ingoing_rel_field"]');
    let outgoing_rel_field = e.target.closest('fieldset').querySelector('input[id^="id_form-"][id$="-outgoing_rel_field"]');


    // geo fields
    let geo_evo_op = e.target.closest('fieldset').querySelector('span.span-evo-op');
    let geo_type = e.target.closest('fieldset').querySelector('span.span-entity-type-or-feature');
    let geo_from_entity_type = e.target.closest('fieldset').querySelector('span.span-define-from-entity-type');
    let geo_feature_text = e.target.closest('fieldset').querySelector('span.span-define-entity-type-or-feature');
    let geo_with = e.target.closest('fieldset').querySelector('span.span-with-feature');
    let geo_with_feature = e.target.closest('fieldset').querySelector('span.span-define-with-feature');
    let geo_property_key = e.target.closest('fieldset').querySelector('span.span-define-property-key');
    let geo_property_value = e.target.closest('fieldset').querySelector('span.span-define-property-value');
    let geo_initial_rel_start_node = e.target.closest('fieldset').querySelector('span.span-initial-rel-start-node');
    let geo_initial_rel_start_node_label = e.target.closest('fieldset').querySelector('span.span-initial-rel-start-node-label');
    let geo_initial_rel_end_node = e.target.closest('fieldset').querySelector('span.span-initial-rel-end-node');
    let geo_initial_rel_end_node_label = e.target.closest('fieldset').querySelector('span.span-initial-rel-end-node-label');
    let geo_to_of = e.target.closest('fieldset').querySelector('span.span-to-entity-type');
    let geo_rename_to = e.target.closest('fieldset').querySelector('span.span-rename-to');
    let geo_start_node = e.target.closest('fieldset').querySelector('span.span-start-node');
    let geo_start_node_label = e.target.closest('fieldset').querySelector('span.span-start-node-label');
    let geo_start_node_prop_key = e.target.closest('fieldset').querySelector('span.span-start-node-prop-key');
    let geo_end_node = e.target.closest('fieldset').querySelector('span.span-end-node');
    let geo_end_node_label = e.target.closest('fieldset').querySelector('span.span-end-node-label');
    let geo_end_node_prop_key = e.target.closest('fieldset').querySelector('span.span-end-node-prop-key');
    let geo_ingoing_rel = e.target.closest('fieldset').querySelector('span.span-ingoing-rel');
    let geo_outgoing_rel = e.target.closest('fieldset').querySelector('span.span-outgoing-rel');

    // handles field changes for evolution operation field
    if (e.target && e.target.matches("select.evo-op")) {
        // hide all fields
        // fields will be turned to hidden upon changing the evolution operation
        type_div.style.display = "none";
        join_div.style.display = "none";
        from_div.style.display = "none";
        feature_text_div.style.display = "none";
        to_div.style.display = "none";
        with_div.style.display = "none";
        with_feature_div.style.display = "none";
        property_value_div.style.display = "none";
        initial_rel_start_node_div.style.display = "none";
        initial_rel_start_node_label_div.style.display = "none";
        initial_rel_end_node_div.style.display = "none";
        initial_rel_end_node_label_div.style.display = "none";
        copy_with_rels_div.style.display = "none";
        rename_to_div.style.display = "none";
        split_at_div.style.display = "none";
        start_node_div.style.display = "none";
        start_node_label_div.style.display = "none";
        start_node_prop_key_div.style.display = "none";
        end_node_div.style.display = "none";
        end_node_label_div.style.display = "none";
        end_node_prop_key_div.style.display = "none";
        ingoing_rel_div.style.display = "none";
        outgoing_rel_div.style.display = "none";

        // hide geo tags
        geo_type.style.display = "none";
        geo_with.style.display = "none";
        geo_from_entity_type.style.display = "none";
        geo_with_feature.style.display = "none";
        geo_to_of.style.display = "none";
        geo_feature_text.style.display = "none";
        geo_initial_rel_start_node.style.display = "none";
        geo_initial_rel_start_node_label.style.display = "none";
        geo_initial_rel_end_node.style.display = "none";
        geo_initial_rel_end_node_label.style.display = "none";
        geo_property_key.style.display = "none";
        geo_property_value.style.display = "none";
        // geo_to_of.style.display = "none";
        geo_rename_to.style.display = "none";
        geo_start_node.style.display = "none";
        geo_start_node_label.style.display = "none";
        geo_start_node_prop_key.style.display = "none";
        geo_end_node.style.display = "none";
        geo_end_node_label.style.display = "none";
        geo_end_node_prop_key.style.display = "none";
        geo_ingoing_rel.style.display = "none";
        geo_outgoing_rel.style.display = "none";

        // set all fields to default value
        type_field.value = "";
        feature_text_field.value = "";
        to_field.value = "";
        with_field.value = "";
        with_feature_field.value = "";
        rename_to_field.value = "";
        split_at_field.value = "";
        ingoing_rel_field.value = "";
        outgoing_rel_field.value = "";

        // hide unwanted labels for input fields
        feature_text_label.style.visibility = "hidden";
        with_feature_label.style.visibility = "hidden";
        property_value_label.style.visibility = "hidden";
        start_node_label_label.style.visibility = "hidden";
        end_node_label_label.style.visibility = "hidden";
        ingoing_rel_label.style.visibility = "hidden";
        outgoing_rel_label.style.visibility = "hidden";

        // display all select options of type field
        type_div.querySelector("optgroup[label='Entity Type']").style.display = "block";
        type_div.querySelector("optgroup[label='Feature']").style.display = "block";
        type_div.querySelector("option[value='RELATIONSHIP']").style.display = "block";
        type_div.querySelector("option[value='TYPE']").style.display = "block";

        // remove options
        type_div.querySelector("option[value='DIRECTION']").style.display = "none";

        // enable options
        type_div.querySelector("option[value='RELATIONSHIP']").disabled = false;
        type_div.querySelector("option[value='PROPERTY']").disabled = false;

        // connect field to geo field
        geo_type.textContent = "-----";

        // handles field changes for evolution operation field
        if (e.target.options[e.target.selectedIndex].textContent === "add") {
            // show fields and geo tags
            type_div.style.display = "block";
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = false;

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

            // make fields required depending on evo op selected!
            type_field.setAttribute("required", "");

            // remove options
            type_div.querySelector("option[value='TYPE']").style.display = "none";

        } else if (e.target.options[e.target.selectedIndex].textContent === "delete" ||
            e.target.options[e.target.selectedIndex].textContent === "transform" ||
            e.target.options[e.target.selectedIndex].textContent === "copy") {
            // show fields and geo tags
            type_div.style.display = "block";
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = false;

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

            // make fields required depending on evo op selected!
            type_field.setAttribute("required", "");

            if (e.target.options[e.target.selectedIndex].textContent === "delete"
                || e.target.options[e.target.selectedIndex].textContent === "copy") {
                // remove options
                type_div.querySelector("option[value='LABEL']").style.display = "block";
                type_div.querySelector("option[value='TYPE']").style.display = "none";

                if (e.target.options[e.target.selectedIndex].textContent === "copy") {
                    type_div.querySelector("option[value='RELATIONSHIP']").style.display = "none";
                } else {
                    type_div.querySelector("option[value='RELATIONSHIP']").disabled = false;
                    type_div.querySelector("option[value='RELATIONSHIP']").style.display = "block";
                }

            } else if (e.target.options[e.target.selectedIndex].textContent === "transform") {
                // remove options
                type_div.querySelector("option[value='LABEL']").style.display = "none";
                type_div.querySelector("option[value='TYPE']").style.display = "none";

                // disable options
                type_div.querySelector("option[value='PROPERTY']").disabled = true;

            } else {
                // show options
                type_div.querySelector("option[value='LABEL']").style.display = "block";
                type_div.querySelector("option[value='TYPE']").style.display = "block";
            }

        } else if (e.target.options[e.target.selectedIndex].textContent === "move") {
            // show fields and geo tags
            type_div.style.display = "block";
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = false;

            // display option
            type_div.querySelector("option[value='TYPE']").style.display = "none";
            type_div.querySelector("option[value='DIRECTION']").style.display = "block";

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

            // make fields required depending on evo op selected!
            type_field.setAttribute("required", "");

        } else if (e.target.options[e.target.selectedIndex].textContent === "rename") {
            // show this fields on "rename" selected as evolution operation
            type_div.style.display = "block";

            // show geo tags
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = false;

            //remove options from type field
            type_div.querySelector("optgroup[label='Entity Type']").style.display = "none";
            type_div.querySelector("option[value='LABEL']").style.display = "block";

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

        } else if (e.target.options[e.target.selectedIndex].textContent === "split") {
            // show fields
            type_div.style.display = "block";

            // show geo tags
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = false;

            //remove options from type field
            type_div.querySelector("optgroup[label='Feature']").style.display = "none";

            // disable options
            // type_div.querySelector("option[value='RELATIONSHIP']").disabled = true;

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

        } else if (e.target.options[e.target.selectedIndex].textContent === "merge") {
            // show fields
            join_div.style.display = "block";
            type_div.style.display = "block";

            // show geo tags
            geo_type.style.display = "inline-block";

            // enable fields
            type_field.disabled = true;

            //remove options from type field
            type_div.querySelector("optgroup[label='Feature']").style.display = "none";

            // display field content in geo span
            geo_evo_op.textContent = e.target.options[e.target.selectedIndex].textContent;

            // disable options
            type_div.querySelector("option[value='RELATIONSHIP']").disabled = true;

        } else {
            // hide fields
            type_div.style.display = "none";
            feature_text_div.style.display = "none";
            to_div.style.display = "none";
            with_div.style.display = "none";
            with_feature_div.style.display = "none";
            rename_to_div.style.display = "none";
            split_at_div.style.display = "none";

            // set default value for fields

            // display field content in geo span
            geo_evo_op.textContent = "-----";
            geo_type.textContent = "-----";
            geo_feature_text.textContent = "-----";
            geo_with.textContent = "-----";
            geo_with_feature.textContent = "-----";
            geo_to_of.textContent = "-----";
            geo_rename_to.textContent = "-----";
            // clear all geo span tags

        }
    }

    // handles field changes for type field
    if (e.target && e.target.matches("select.join-options")) {
        if (e.target.options[e.target.selectedIndex].textContent === "---------") {
            // display field content in geo span
            geo_evo_op.textContent = evo_op_field.options[evo_op_field.selectedIndex].textContent
        } else {
            if (e.target.options[e.target.selectedIndex].textContent === "full outer inclusive") {
                // display field content in geo span
                geo_evo_op.textContent = evo_op_field.options[evo_op_field.selectedIndex].textContent + " all properties of";

            } else {
                // display field content in geo span
                geo_evo_op.textContent = evo_op_field.options[evo_op_field.selectedIndex].textContent + ": " + e.target.options[e.target.selectedIndex].textContent;
            }

            //enable field
            type_field.disabled = false;
        }
    }


    // handles field changes for type field
    if (e.target && e.target.matches("select.type")) {
        // hide all fields
        // fields will be turned to hidden upon changing the evolution operation
        from_div.style.display = "none";
        with_div.style.display = "none";
        with_feature_div.style.display = "none";
        feature_text_div.style.display = "none";
        property_key_div.style.display = "none";
        property_value_div.style.display = "none";
        initial_rel_start_node_div.style.display = "none";
        initial_rel_start_node_label_div.style.display = "none";
        initial_rel_end_node_div.style.display = "none";
        initial_rel_end_node_label_div.style.display = "none";
        rename_to_div.style.display = "none";
        to_div.style.display = "none";
        copy_with_rels_div.style.display = "none";
        split_at_div.style.display = "none";
        start_node_div.style.display = "none";
        start_node_label_div.style.display = "none";
        start_node_prop_key_div.style.display = "none";
        end_node_div.style.display = "none";
        end_node_label_div.style.display = "none";
        end_node_prop_key_div.style.display = "none";
        ingoing_rel_div.style.display = "none";
        outgoing_rel_div.style.display = "none";

        // hide geo tags
        geo_from_entity_type.style.display = "none";
        geo_initial_rel_start_node.style.display = "none";
        geo_initial_rel_start_node_label.style.display = "none";
        geo_initial_rel_end_node.style.display = "none";
        geo_initial_rel_end_node_label.style.display = "none";
        geo_to_of.style.display = "none";
        geo_property_key.style.display = "none";
        geo_property_value.style.display = "none";
        geo_feature_text.style.display = "none";
        geo_rename_to.style.display = "none";
        geo_start_node.style.display = "none";
        geo_start_node_label.style.display = "none";
        geo_start_node_prop_key.style.display = "none";
        geo_end_node.style.display = "none";
        geo_end_node_label.style.display = "none";
        geo_end_node_prop_key.style.display = "none";
        geo_ingoing_rel.style.display = "none";
        geo_outgoing_rel.style.display = "none";

        // set dropdowns to default value
        from_field.value = "";
        initial_rel_start_node_field.value = "";
        initial_rel_start_node_label_field.value = "";
        initial_rel_end_node_field.value = "";
        initial_rel_end_node_label_field.value = "";
        with_field.value = "";
        with_feature_field.value = "";
        rename_to_field.value = "";
        feature_text_field.value = "";
        to_field.value = "";
        split_at_field.value = "";
        copy_with_rels_field.value = "";
        start_node_field.value = "";
        start_node_label_field.value = "";
        end_node_field.value = "";
        end_node_label_field.value = "";

        // geo fields
        geo_from_entity_type.textContent = "-----";
        geo_initial_rel_start_node.textContent = "-----";
        geo_initial_rel_start_node_label.textContent = "-----";
        geo_initial_rel_end_node.textContent = "-----";
        geo_initial_rel_end_node_label.textContent = "-----";
        geo_with.textContent = "-----";
        geo_with_feature.textContent = "-----";
        geo_rename_to.textContent = "-----";
        geo_start_node.textContent = "-----";
        geo_start_node_label.textContent = "-----";
        geo_end_node.textContent = "-----";
        geo_end_node_label.textContent = "-----";
        geo_ingoing_rel.textContent = "-----";
        geo_outgoing_rel.textContent = "-----";

        // show geo tags
        geo_with.style.display = "inline-block";
        geo_with_feature.style.display = "inline-block";

        //remove placeholder for property key field
        feature_text_field.removeAttribute("placeholder");
        start_node_label_field.removeAttribute("placeholder");

        // show options
        from_field.querySelector("option[value='']").style.display = "block";
        from_field.querySelector("option[value='NODE']").style.display = "block";
        initial_rel_start_node_div.querySelector("option[value='']").style.display = "none";

        if (e.target.options[e.target.selectedIndex].textContent === "node") {
            // show fields
            with_div.style.display = "block";
            with_feature_div.style.display = "block";

            // enable with field
            with_field.disabled = false;
            with_feature_field.disabled = true;

            // remove unavailable options
            with_div.querySelector("option[value='LABEL']").style.display = "block";
            with_div.querySelector("option[value='TYPE']").style.display = "none";

            // connect field content to geo field
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;
            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete") {
                // show fields
                copy_with_rels_div.style.display = "block";

                // show geo fields
                geo_rename_to.style.display = "inline-block";

                // disable fields
                copy_with_rels_field.disabled = true;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy") {
                // show fields
                copy_with_rels_div.style.display = "block";
                start_node_label_div.style.display = "block";

                // show geo fields
                // geo_rename_to.style.display = "inline-block";
                geo_start_node.style.display = "inline-block";
                geo_start_node_label.style.display = "inline-block";

                //ToDo: necessary?
                // remove options
                start_node_div.querySelector("option[value='LABEL']").style.display = "block";

                // set placeholder
                start_node_label_field.setAttribute("placeholder", "prop key(s) to skip");

                // disable fields
                copy_with_rels_field.disabled = true;
                start_node_label_field.disabled = true;

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move") {
                // show fields
                initial_rel_start_node_div.style.display = "block";
                initial_rel_start_node_label_div.style.display = "block";
                start_node_div.style.display = "block";

                // show geo
                geo_initial_rel_start_node.style.display = "inline-block";
                geo_initial_rel_start_node_label.style.display = "inline-block";
                geo_start_node.style.display = "inline-block";

                // disable fields
                with_field.disabled = true;
                start_node_field.disabled = true;

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split") {
                // show fields
                split_at_div.style.display = "block";

                // disable fields
                split_at_field.disabled = true;

                // show geo
                geo_rename_to.style.display = "inline-block";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform") {
                // show fields
                start_node_div.style.display = "block";
                end_node_div.style.display = "block";
                ingoing_rel_div.style.display = "block";

                // show geo
                geo_start_node.style.display = "inline-block";
                geo_end_node.style.display = "inline-block";
                geo_rename_to.style.display = "inline-block";
                geo_rename_to.textContent = "to relationship with type";
                geo_ingoing_rel.style.display = "inline-block";

                // disable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;
                ingoing_rel_field.disabled = true;

                // set placeholder attribute
                ingoing_rel_field.setAttribute("placeholder", "type")

                // remove options
                with_field.querySelector("option[value='PROPERTY']").style.display = "none";

                // disable fields
                start_node_label_field.disabled = true;
                if (type_field.options[type_field.selectedIndex].textContent === "node") {
                    // set placeholder
                    // start_node_label_field.setAttribute("placeholder", "type");

                    // set placeholder
                    ingoing_rel_field.setAttribute('placeholder', 'type of rel')

                } else {
                    // set placeholder
                    // start_node_label_field.removeAttribute("placeholder");
                }


            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "merge") {
                //show fields
                start_node_div.style.display = "block";

                //show geo
                geo_start_node.style.display = "inline-block";

                //disable fields
                start_node_field.disabled = true;

                // change label of start node field
                start_node_div.querySelector('label').textContent = "And node with";

                // remove options
                with_field.querySelector("option[value='PROPERTY']").style.display = "none";
                start_node_field.querySelector("option[value='PROPERTY']").style.display = "none";
                start_node_field.querySelector("option[value='LABEL_AND_PROPERTY']").style.display = "none";

            } else {
                // hide fields
                split_at_div.style.display = "none";

                // hide geo tags
                geo_rename_to.style.display = "none";

                // show options
                with_field.querySelector("option[value='PROPERTY']").style.display = "block";

                // remove placholder
                start_node_label_field.removeAttribute("placeholder");

            }
        } else if (e.target.options[e.target.selectedIndex].textContent === "relationship"
            || e.target.options[e.target.selectedIndex].textContent === "direction") {
            // show fields
            with_div.style.display = "block";
            with_feature_div.style.display = "block";

            // enable with field
            with_field.disabled = false;
            with_feature_field.disabled = true;

            // remove unavailable options
            with_div.querySelector("option[value='LABEL']").style.display = "none";
            with_div.querySelector("option[value='TYPE']").style.display = "block";

            // connect field content to geo field
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;

            if (((evo_op_field.options[evo_op_field.selectedIndex].textContent === "add"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "split")
                    && e.target.options[e.target.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && type_field.options[type_field.selectedIndex].textContent === "direction")) {
                // show fields
                start_node_div.style.display = "block";
                end_node_div.style.display = "block";

                // show geo fields
                geo_start_node.style.display = "inline-block";
                geo_end_node.style.display = "inline-block";

                // enable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;
                if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && type_field.options[type_field.selectedIndex].textContent === "direction") {
                    // show field
                    from_div.style.display = "block";

                    // show geo
                    geo_from_entity_type.style.display = "inline-block";

                    // set value
                    from_field.value = "RELATIONSHIP";
                    geo_from_entity_type.textContent = "of " + from_field.options[from_field.selectedIndex].textContent;

                    // remove options
                    from_field.querySelector("option[value='']").style.display = "none";
                    from_field.querySelector("option[value='NODE']").style.display = "none";
                    from_field.querySelector("option[value='RELATIONSHIP']").style.display = "block";

                    // enable field
                    from_div.disabled = false;
                } else if ((evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy")
                    && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                    // show fields
                    initial_rel_start_node_div.style.display = "block";
                    initial_rel_start_node_label_div.style.display = "block";
                    initial_rel_end_node_div.style.display = "block";

                    // show geo
                    geo_initial_rel_start_node.style.display = "inline-block";
                    geo_initial_rel_start_node_label.style.display = "inline-block";
                    geo_initial_rel_end_node.style.display = "inline-block";
                    geo_initial_rel_end_node_label.style.display = "inline-block";

                    // hide fields and geo
                    initial_rel_end_node_label_div.style.display = "none";
                    // set default value (also for geo)
                    initial_rel_end_node_field.value = "";
                    initial_rel_end_node_label_field.value = "";


                    // remove options and set value
                    initial_rel_start_node_div.querySelector("option[value='']").style.display = "none";
                    initial_rel_start_node_field.value = "LABEL"

                    // en- or disable fields
                    initial_rel_start_node_field.disabled = false;
                    initial_rel_start_node_label_field.disabled = false;
                    initial_rel_end_node_field.disabled = true;
                    with_field.disabled = true;

                    // connect to geo


                } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                    // show fields
                    split_at_div.style.display = "block";

                    // disable fields
                    split_at_field.disabled = true;

                    // show geo
                    geo_rename_to.style.display = "inline-block";
                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform") {
                // show fields
                start_node_div.style.display = "block";
                end_node_div.style.display = "block";
                ingoing_rel_div.style.display = "block";
                outgoing_rel_div.style.display = "block";

                // disable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;
                ingoing_rel_field.disabled = true;
                outgoing_rel_field.disabled = true;

                // connect to geo
                geo_start_node.style.display = "inline-block";
                geo_end_node.style.display = "inline-block";
                geo_ingoing_rel.style.display = "inline-block";
                geo_outgoing_rel.style.display = "inline-block";

                // pre fill out geo
                geo_ingoing_rel.textContent = "to node with ingoing rel " + ingoing_rel_field.value;

                // set placeholder attribute
                ingoing_rel_field.setAttribute("placeholder", "type of ingoing rel");

            } else {
                // ToDo: is this part necessary?
                // hide fields
                start_node_div.style.display = "none";
                end_node_div.style.display = "none";

                // hide geo fields
                geo_start_node.style.display = "none";
                geo_end_node.style.display = "none";


            }

        }
            // all cases for features
        // TODO: kann der Code für label, type gekürzt werden?
        else if (e.target.options[e.target.selectedIndex].textContent === "label") {
            // show this fields on "rename" selected as evolution operation
            feature_text_div.style.display = "block";
            to_div.style.display = "block";
            with_div.style.display = "block";
            with_feature_div.style.display = "block";

            // connect field content to geo field
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;

            // show geo tags
            geo_to_of.style.display = "inline-block";
            geo_feature_text.style.display = "inline-block";

            // disable fields
            feature_text_field.disabled = false;
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;
            split_at_field.disabled = true;


            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                // show fields
                rename_to_div.style.display = "block";

                // change label of to field
                to_div.querySelector('label').textContent = "Of";

                // disable fields
                rename_to_field.disabled = true;

                // show geo
                geo_rename_to.style.display = "inline-block";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete") {
                // change label of to field
                to_div.querySelector('label').textContent = "From";

                // hide fields
                rename_to_div.style.display = "none";

                // hide geo tags
                geo_rename_to.style.display = "none";

            } else {
                // change label of to field
                to_div.querySelector('label').textContent = "To";

                // hide fields
                rename_to_div.style.display = "none";

                // hide geo tags
                geo_rename_to.style.display = "none";
            }

            // remove options of to field
            to_div.querySelector("option[value='RELATIONSHIP']").style.display = "none";
            to_div.querySelector("option[value='NODE']").style.display = "block";
            // show options of with field
            with_div.querySelector("option[value='LABEL']").style.display = "block";
            with_div.querySelector("option[value='TYPE']").style.display = "none";
            with_div.querySelector("option[value='PROPERTY']").style.display = "block";

        } else if (e.target.options[e.target.selectedIndex].textContent === "type") {
            // show this fields on "rename" selected as evolution operation
            feature_text_div.style.display = "block";
            // to_div.style.display = "block";
            // with_div.style.display = "block";
            // with_feature_div.style.display = "block";

            // show geo tags
            // geo_to_of.style.display = "inline-block";
            // geo_feature_text.style.display = "inline-block";

            // disable fields
            feature_text_field.disabled = false;
            split_at_field.disabled = true;

            // connect field content to geo field
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;


            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                // show fields
                start_node_div.style.display = "block";
                end_node_div.style.display = "block";
                rename_to_div.style.display = "block";

                // change label of to field
                to_div.querySelector('label').textContent = "Of";

                // disable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;
                rename_to_field.disabled = true;

                // show geo
                geo_start_node.style.display = "inline-block";
                geo_end_node.style.display = "inline-block";
                geo_rename_to.style.display = "inline-block";
            } else {
                // hide fields
                rename_to_div.style.display = "none";

                // change label of to field
                to_div.querySelector('label').textContent = "To";

                // hide geo tags
                geo_rename_to.style.display = "none";
            }

        } else if (e.target.options[e.target.selectedIndex].textContent === "property") {
            // show fields
            feature_text_div.style.display = "block";
            to_div.style.display = "block";
            with_div.style.display = "block";
            with_feature_div.style.display = "block";

            // connect to geo
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;

            // show geo tags
            geo_to_of.style.display = "inline-block";
            geo_feature_text.style.display = "inline-block";

            // disable fields
            feature_text_field.disabled = false;
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;
            split_at_field.disabled = true;


            // connect field content to geo field
            geo_type.textContent = e.target.options[e.target.selectedIndex].textContent;

            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "add") {
                // show fields
                property_value_div.style.display = "block";
                geo_property_value.style.display = "inline-block";

                //set placeholder for porperty key field
                feature_text_field.setAttribute("placeholder", "key1, key2...");

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                // show fields
                rename_to_div.style.display = "block";

                // disable fields
                rename_to_field.disabled = true;

                // show geo
                geo_rename_to.style.display = "inline-block";

                // change label of to field
                to_div.querySelector('label').textContent = "Of";


            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete") {
                // change label of to field
                to_div.querySelector('label').textContent = "From";

                // hide fields
                rename_to_div.style.display = "none";

                // hide geo tags
                geo_rename_to.style.display = "none";

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                || evo_op_field.options[evo_op_field.selectedIndex].textContent === "move") {
                // show fields
                from_div.style.display = "block";
                feature_text_div.style.display = "block";


                // show geo
                geo_from_entity_type.style.display = "inline-block";

                // disable fields
                feature_text_field.disabled = true;



            } else {
                // hide fields
                rename_to_div.style.display = "none";

                // change label of to field
                to_div.querySelector('label').textContent = "To";

                // hide geo tags
                geo_rename_to.style.display = "none";
            }

            // show options of to field
            to_div.querySelector("option[value='RELATIONSHIP']").style.display = "block";
            to_div.querySelector("option[value='NODE']").style.display = "block";

            // show options of with field
            with_div.querySelector("option[value='LABEL']").style.display = "block";
            with_div.querySelector("option[value='TYPE']").style.display = "block";
            with_div.querySelector("option[value='PROPERTY']").style.display = "block";

        } else {
            // disable fields
            feature_text_field.disabled = true;

            // set dropdowns to default value
            with_field.value = "";
            feature_text_field.value = "";

            // hide geo tags
            geo_with.style.display = "none";
            geo_with_feature.style.display = "none";
            geo_property_value.style.display = "none";
            geo_to_of.style.display = "none";
            geo_feature_text.style.display = "none";


            // connect field to geo field
            geo_type.textContent = "-----";

        }
    }

    if (e.target && e.target.matches("select.from-entity-type")) {

        //ToDo: use in else only on copy evo op in combination with to rel?
        // hide fields
        property_key_div.style.display = "none";
        property_value_div.style.display = "none";
        initial_rel_start_node_div.style.display = "none";
        initial_rel_start_node_label_div.style.display = "none";
        initial_rel_end_node_div.style.display = "none";
        initial_rel_end_node_label_div.style.display = "none";
        start_node_div.style.display = "none";
        start_node_label_div.style.display = "none";
        end_node_div.style.display = "none";
        end_node_label_div.style.display = "none";

        // hide geo
        geo_property_key.style.display = "none";
        geo_property_value.style.display = "none";
        geo_initial_rel_start_node.style.display = "none";
        geo_initial_rel_start_node_label.style.display = "none";
        geo_initial_rel_end_node.style.display = "none";
        geo_initial_rel_end_node_label.style.display = "none";
        geo_start_node.style.display = "none";
        geo_start_node_label.style.display = "none";
        geo_start_node_prop_key.style.display = "none";
        geo_end_node.style.display = "none";
        geo_end_node_label.style.display = "none";
        geo_end_node_prop_key.style.display = "none";

        // set default value
        feature_text_field.value = "";
        property_key_field.value = "";
        property_value_field.value = "";
        to_field.value = "";
        with_field.value = "";
        with_feature_field.value = "";
        initial_rel_start_node_field.value = "";
        initial_rel_start_node_label_field.value = "";
        initial_rel_end_node_field.value = "";
        initial_rel_end_node_label_field.value = "";

        // set default value for geo
        geo_feature_text.textContent = "-----";
        geo_to_of.textContent = "-----";
        geo_with.textContent = "-----";
        geo_with_feature.textContent = "-----";
        geo_property_key.textContent = "-----";
        geo_property_value.textContent = "-----";
        geo_initial_rel_start_node.textContent = "-----";
        geo_initial_rel_start_node_label.textContent = "-----";
        geo_initial_rel_end_node.textContent = "-----";
        geo_initial_rel_end_node_label.textContent = "-----";

        // disable fields
        to_field.disabled = true;
        with_field.disabled = true;
        with_feature_field.disabled = true;

        // set placeholder
        feature_text_field.removeAttribute("placeholder")

        if (e.target.options[e.target.selectedIndex].textContent === "node") {

            // set placeholder
            feature_text_field.setAttribute("placeholder", "label")
            // property_value_field.setAttribute("placeholder", "value")

            // enable field
            feature_text_field.disabled = false;

            // connect to geo
            geo_from_entity_type.textContent = "of " + e.target.options[e.target.selectedIndex].textContent;


        } else if (e.target.options[e.target.selectedIndex].textContent === "relationship") {
            // disable fields
            initial_rel_start_node_field.disabled = true;
            initial_rel_end_node_field.disabled = true;

            // show fields
            initial_rel_start_node_div.style.display = "block";
            initial_rel_end_node_div.style.display = "block";

            // show geo
            geo_initial_rel_start_node.style.display = "inline-block";
            geo_initial_rel_end_node.style.display = "inline-block";

            // set placeholder
            feature_text_field.setAttribute("placeholder", "type");

            // enable field
            feature_text_field.disabled = false;

            // connect to geo
            geo_from_entity_type.textContent = "of " + e.target.options[e.target.selectedIndex].textContent;

        } else {
            // enable field
            feature_text_field.disabled = true;
            property_key_field.disabled = true;
            property_value_field.disabled = true;
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;

            // connect to geo
            geo_from_entity_type.textContent = "-----";
            geo_to_of.textContent = "-----";
            geo_with.textContent = "-----";
            geo_with_feature.textContent = "-----";


            // set "empty" values for disabled fields
            to_field.value = "";
            with_field.value = "";
            with_feature_field.value = "";


        }
    }

    // handles field changes for start node field
    if (e.target && e.target.matches("select.start-node")) {
        // hide fields
        start_node_label_div.style.display = "none";
        start_node_prop_key_div.style.display = "none";

        // hide geo
        geo_start_node_label.style.display = "none";
        geo_start_node_prop_key.style.display = "none";
        geo_start_node_prop_key.style.display = "none";


        if (e.target.options[e.target.selectedIndex].textContent === "label") {
            // show fields
            start_node_label_div.style.display = "block";

            // enable fields
            start_node_label_field.disabled = false;

            // show geo
            geo_start_node_label.style.display = "inline-block";

            // display different geo input if add or copy/move operation was selected as evolution operation
            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "add"
                || evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && (type_field.options[type_field.selectedIndex].textContent === "type"
                        || (type_field.options[type_field.selectedIndex].textContent === "property"
                            && to_field.options[to_field.selectedIndex].textContent === "relationship")
                    )
                )
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship")
            ) {
                // connect field to geo field
                geo_start_node.textContent = "starting at node with " + e.target.options[e.target.selectedIndex].textContent;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                && type_field.options[type_field.selectedIndex].textContent === "direction") {
                // connect field to geo field
                geo_start_node.textContent = "from start node with " + e.target.options[e.target.selectedIndex].textContent;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "merge"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // connect field to geo field
                geo_start_node.textContent = "and node with " + e.target.options[e.target.selectedIndex].textContent;
            } else {
                // connect field to geo field
                geo_start_node.textContent = "to new start node with " + e.target.options[e.target.selectedIndex].textContent;
            }


        } else if (e.target.options[e.target.selectedIndex].textContent === "label & property") {
            // show fields
            start_node_label_div.style.display = "block";
            start_node_prop_key_div.style.display = "block";

            // enable fields
            start_node_prop_key_field.disabled = true;

            // show geo
            geo_start_node_label.style.display = "inline-block";
            geo_start_node_prop_key.style.display = "inline-block";

            // connect field to geo field
            geo_start_node.textContent = e.target.options[e.target.selectedIndex].textContent;

        } else if (e.target.options[e.target.selectedIndex].textContent === "property") {
            // show fields
            start_node_prop_key_div.style.display = "block";

            // show geo
            geo_start_node_prop_key.style.display = "inline-block";

            // enable fields
            start_node_prop_key_field.disabled = false;

            // connect field to geo field
            geo_start_node.textContent = start_node_prop_key_field.value;

        } else {
            // hide fields
            end_node_label_div.style.display = "none";
            // disable fields
            // start_node_label_field.disabled = true;
            end_node_field.disabled = true;

            // reset values
            start_node_label_field.value = "";
            start_node_prop_key_field.value = "";
            end_node_field.value = "";
            end_node_label_field.value = "";

            // connect field to geo field
            geo_start_node.textContent = "-----";
            geo_start_node_label.textContent = "-----";
            geo_end_node.textContent = "-----";
            geo_end_node_label.textContent = "-----";

            if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "type")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // disable field
                rename_to_field.disabled = true;

                // set default value
                rename_to_field.value = "";

                // reset geo
                geo_rename_to.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                && (type_field.options[type_field.selectedIndex].textContent === "node"
                    || type_field.options[type_field.selectedIndex].textContent === "relationship")) {
                // disable fields
                ingoing_rel_field.disabled = true;
                outgoing_rel_field.disabled = true;

                // set default value
                ingoing_rel_field.value = "";
                outgoing_rel_field.value = "";

                // connect to geo
                geo_ingoing_rel.textContent = "-----";
                geo_outgoing_rel.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // disable field
                split_at_field.disabled = true;

                // set default value for field
                split_at_field.value = "";

                // set default value for geo
                geo_rename_to.textContent = "-----";
            }
        }


    }


    // handles field changes for feature text field
    if (e.target && e.target.matches("input.feature-text")) {

        if (feature_text_field.value.length > 0) {

            // connect field content to geo field
            geo_feature_text.textContent = feature_text_field.value;

            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {


                if (type_field.options[type_field.selectedIndex].value === "LABEL") {
                    // pre fillout of value
                    with_feature_field.value = e.target.value;

                    // enable field
                    to_field.disabled = false;
                    rename_to_field.disabled = false;

                    //enable predefined fields
                    with_field.disabled = false;
                    with_feature_field.disabled = false;

                    // pre define values of dropdown menus
                    to_field.value = "NODE";
                    with_field.value = "LABEL";

                    // set geo
                    geo_to_of.textContent = "of " + to_field.options[to_field.selectedIndex].textContent;
                    geo_with.textContent = "with " + with_field.options[with_field.selectedIndex].textContent;
                    geo_with_feature.textContent = e.target.value;


                } else if (type_field.options[type_field.selectedIndex].value === "TYPE") {
                    // set geo
                    geo_with_feature.textContent = e.target.value;
                    //ToDo: remove geo field
                    // enable fields
                    start_node_field.disabled = false;
                    start_node_label_field.disabled = false;
                } else if (type_field.options[type_field.selectedIndex].value === "PROPERTY") {
                    // enable field
                    to_field.disabled = false;
                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                && type_field.options[type_field.selectedIndex].textContent === "label") {
                // enable field
                to_field.disabled = false;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                || evo_op_field.options[evo_op_field.selectedIndex].textContent === "move") {

                if (from_field.options[from_field.selectedIndex].textContent === "node") {
                    // enable fields
                    /*                    property_key_field.disabled = false;
                                        to_field.disabeld = true;*/
                    to_field.disabled = false;

                    // connect field content to geo field
                    geo_feature_text.textContent = "with label " + feature_text_field.value;
                } else if (from_field.options[from_field.selectedIndex].textContent === "relationship") {
                    // show fields
                    initial_rel_start_node_label_div.style.display = "block";

                    // remove options
                    initial_rel_start_node_div.querySelector("option[value='']").style.display = "none";
                    initial_rel_start_node_field.value = "LABEL";

                    // enable fields
                    initial_rel_start_node_field.disabled = false;
                    initial_rel_start_node_label_div.disabled = false;
                } else if (type_field.options[type_field.selectedIndex].textContent === "label") {
                    to_field.disabled = false;
                }

            } else {
                // TODO: Something missing????
                // enable field
                to_field.disabled = false;

            }
        } else {
            // disable field
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;
            property_key_field.disabled = true;
            property_value_field.disabled = true;

            // set to field to default value
            with_feature_field.value = "";
            property_key_field.value = "";
            property_value_field.value = "";

            // connect field content to geo field
            geo_feature_text.textContent = "-----";
            geo_property_value.textContent = "-----";

            if (from_field.options[from_field.selectedIndex].textContent === "relationship") {
                // hide fields
                initial_rel_start_node_label_div.style.display = "none";
                initial_rel_end_node_label_div.style.display = "none";

                // disable fields
                initial_rel_start_node_field.disabled = true;
                initial_rel_end_node_field.disabled = true;

                // set default value
                initial_rel_start_node_field.value = "";
                initial_rel_start_node_label_field.value = "";
                initial_rel_end_node_field.value = "";
                initial_rel_end_node_label_field.value = "";
                if (to_field.options[to_field.selectedIndex].textContent === "relationship") {
                    // hide fields
                    start_node_label_div.style.display = "none";
                    end_node_label_div.style.display = "none";

                    // disable fields
                    start_node_field.disabled = true;
                    end_node_field.disabled = true;

                    // set default value
                    with_field.value = "";
                    to_field.value = "";
                    start_node_field.value = "";
                    start_node_label_field.value = "";
                    end_node_field.value = "";
                    end_node_label_field.value = "";

                    // set default value for geo
                    geo_with.textContent = "-----";
                    geo_with_feature.textContent = "-----";
                    geo_to_of.textContent = "-----";
                    geo_start_node.textContent = "-----";
                    geo_start_node_label.textContent = "-----";
                    geo_end_node.textContent = "-----";
                    geo_end_node_label.textContent = "-----";

                }

            } else if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    || evo_op_field.options[evo_op_field.selectedIndex].textContent === "add")
                && (type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // hide fields
                start_node_label_div.style.display = "none";
                end_node_label_div.style.display = "none";

                // disable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;

                // set default value
                with_field.value = "";
                to_field.value = "";
                start_node_field.value = "";
                start_node_label_field.value = "";
                end_node_field.value = "";
                end_node_label_field.value = "";

                // set default value for geo
                geo_with.textContent = "-----";
                geo_with_feature.textContent = "-----";
                geo_to_of.textContent = "-----";
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
                geo_end_node.textContent = "-----";
                geo_end_node_label.textContent = "-----";


                if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                    // disable fields
                    rename_to_field.disabled = true;

                    // set default value for field
                    rename_to_field.value = "";

                    // set default value for geo
                    geo_rename_to.textContent = "-----";
                }

            }
        }
    }

    if (e.target && e.target.matches("input.property-key")) {
        if (property_key_field.value.length > 0) {
            // enable fields
            property_value_field.disabled = false;

            // connect to geo
            geo_property_key.textContent = "and property " + property_key_field.value

        } else {
            // enable fields
            property_value_field.disabled = true;
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;

            // reset values
            property_value_field.value = "";
            with_feature_field.value = "";

            // connect to geo
            geo_property_key.textContent = "-----";

        }
    }

    if (e.target && e.target.matches("input.property-value")) {
        if (property_value_field.value.length > 0) {
            // enable fields
            to_field.disabled = false;

            // connect to geo
            geo_property_value.textContent = property_value_field.value;

        } else {
            // enable fields
            to_field.disabled = true;
            with_field.disabled = true;
            with_feature_field.disabled = true;

            // reset values
            with_field.value = "";
            with_feature_field.value = "";

            // connect to geo
            geo_property_value.textContent = "-----";

        }
    }

    if (e.target && e.target.matches("input.initial-rel-start-node-label")) {
        // show options
        initial_rel_end_node_div.querySelector("option[value='']").style.display = "block";

        // set default value
        // ToDo: value is not set to empty yet !
        initial_rel_end_node_field.value = "";
        initial_rel_end_node_label_field.value = "";

        if (initial_rel_start_node_label_field.value.length > 0) {
            // show fields
            initial_rel_end_node_label_div.style.display = "block";

            // enable fields
            initial_rel_end_node_field.disabled = false;
            initial_rel_end_node_label_field.disabled = false;

            // remove options
            initial_rel_end_node_div.querySelector("option[value='']").style.display = "none";
            initial_rel_end_node_field.value = "LABEL";

            // show and connect to geo
            //geo_initial_rel_start_node.style.display = "inline-block";
            geo_initial_rel_start_node_label.style.display = "inline-block";
            geo_initial_rel_start_node.textContent = "starting at node with " + initial_rel_start_node_field.options[initial_rel_start_node_field.selectedIndex].textContent;
            geo_initial_rel_start_node_label.textContent = initial_rel_start_node_label_field.value;
            geo_initial_rel_end_node.textContent = " ending at node with " + initial_rel_end_node_field.options[initial_rel_end_node_field.selectedIndex].textContent;
            geo_initial_rel_end_node_label.style.display = "inline-block";

            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                geo_initial_rel_start_node.textContent = " from current start node with " + initial_rel_start_node_field.options[initial_rel_start_node_field.selectedIndex].textContent;

                // hide field
                initial_rel_end_node_label_div.style.display = "none";
                geo_initial_rel_end_node_label.style.display = "none";

                // enable field
                with_field.disabled = false;
            }


        } else {
            // hide fields
            initial_rel_end_node_label_div.style.display = "none";

            // disable fields
            initial_rel_end_node_field.disabled = true;
            initial_rel_end_node_label_field.disabled = true;

            // connect to geo
            geo_initial_rel_start_node_label.textContent = "-----";

            if ((evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy")
                && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                    || from_field.options[from_field.selectedIndex].textContent === "relationship")) {
                // hide fields
                start_node_label_div.style.display = "none";
                start_node_prop_key_field.style.display = "none";
                end_node_label_div.style.display = "none";
                end_node_prop_key_field.style.display = "none";

                // hide geo fields
                geo_initial_rel_end_node_label.style.display = "none";
                geo_initial_rel_start_node_label.style.display = "none";

                // disable fields
                with_field.disabled = true;
                with_feature_field.disabled = true;
                start_node_field.disabled = true;
                end_node_field.disabled = true;

                // set default value
                with_field.value = "";
                with_feature_field.value = "";
                start_node_field.value = "";
                start_node_label_field.value = "";
                start_node_prop_key_field.value = "";
                end_node_field.value = "";
                end_node_label_field.value = "";
                end_node_prop_key_field.value = "";

                // set default value for geo
                geo_initial_rel_end_node.textContent = "-----";
                geo_initial_rel_end_node_label.textContent = "-----";
                geo_initial_rel_start_node.textContent = "-----";
                geo_initial_rel_start_node_label.textContent = "-----";
                geo_with.textContent = "-----";
                geo_with_feature.textContent = "-----";
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
                geo_start_node_prop_key.textContent = "-----";
                geo_end_node.textContent = "-----";
                geo_end_node_label.textContent = "-----";
                geo_end_node_prop_key.textContent = "-----";

                if ((evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy")
                    && from_field.options[from_field.selectedIndex].textContent === "relationship") {
                    // hide fields
                    start_node_div.style.display = "none";
                    end_node_div.style.display = "none";

                    // set default value
                    to_field.value = "";

                    // disable fields
                    to_field.disabled = true;
                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // enable fields
                with_field.disabled = true;
                with_feature_field.disabled = true;
                start_node_field.disabled = true;
                start_node_label_field.disabled = true;

                // set default value for fields
                with_field.value = "";
                with_feature_field.value = "";
                start_node_field.value = "";
                start_node_label_field.value = "";

                // set default value for geo fields
                geo_with.textContent = "-----";
                geo_with_feature.textContent = "-----";
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
            }

        }
    }

    if (e.target && e.target.matches("input.initial-rel-end-node-label")) {
        if (initial_rel_end_node_label_field.value.length > 0) {
            // enable field
            to_field.disabled = false;

            // connect to geo
            geo_initial_rel_end_node_label.textContent = initial_rel_end_node_label_field.value;

            if ((evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy")
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                with_field.disabled = false;
            }
        } else {
            // disable field
            to_field.disabled = true;

            // connect to geo
            geo_initial_rel_end_node_label.textContent = "-----";

            if ((evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    || evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy")
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // hide fields
                start_node_label_div.style.display = "none";
                start_node_prop_key_field.style.display = "none";
                end_node_label_div.style.display = "none";
                end_node_prop_key_field.style.display = "none";

                // disable fields
                with_field.disabled = true;
                with_feature_field.disabled = true;
                start_node_field.disabled = true;
                end_node_field.disabled = true;

                // set default value
                with_field.value = "";
                with_feature_field.value = "";
                start_node_field.value = "";
                start_node_label_field.value = "";
                start_node_prop_key_field.value = "";
                end_node_field.value = "";
                end_node_label_field.value = "";
                end_node_prop_key_field.value = "";

                // set default value for geo
                geo_with.textContent = "-----";
                geo_with_feature.textContent = "-----";
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
                geo_start_node_prop_key.textContent = "-----";
                geo_end_node.textContent = "-----";
                geo_end_node_label.textContent = "-----";
                geo_end_node_prop_key.textContent = "-----";

            }

        }
    }

    // handles field changes for feature text field
    if (e.target && e.target.matches("select.to")) {
        // disable fields
        // with_field.disabled = true;
        // with_feature_field.disabled = true;
        // rename_to_field.disabled = true;

        // hide fields
        start_node_div.style.display = "none";
        start_node_label_div.style.display = "none";
        end_node_div.style.display = "none";
        end_node_label_div.style.display = "none";

        // hide geo
        geo_start_node.style.display = "none";
        geo_start_node_label.style.display = "none";
        geo_end_node.style.display = "none";
        geo_end_node_label.style.display = "none";

        // set to default value
        geo_with.textContent = "-----";
        geo_with_feature.textContent = "-----";
        geo_start_node.textContent = "-----";
        geo_start_node_label.textContent = "-----";
        geo_end_node.textContent = "-----";
        geo_end_node_label.textContent = "-----";

        // set default value
        with_field.value = "";
        with_feature_field.value = "";
        start_node_field.value = "";
        start_node_label_field.value = "";
        end_node_field.value = "";
        end_node_label_field.value = "";

        if (e.target.options[e.target.selectedIndex].textContent === "node") {

            // hide fields
            start_node_div.style.display = "none";
            end_node_div.style.display = "none";

            // enable field
            with_field.disabled = false;
            with_feature_field.disabled = true;

            // connect to geo
            geo_to_of.textContent = "to " + e.target.options[e.target.selectedIndex].textContent;

            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "add" ||
                evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy") {
                // show options of to-field
                with_div.querySelector("option[value='LABEL']").style.display = "block";
                // remove options of to-field
                with_div.querySelector("option[value='TYPE']").style.display = "none";
            }
            // if evolution operation rename was selected change output in geo
            else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                geo_to_of.textContent = "of " + e.target.options[e.target.selectedIndex].textContent;
            } else if (
                evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                && (type_field.options[type_field.selectedIndex].textContent === "label"
                    || type_field.options[type_field.selectedIndex].textContent === "property")
            ) {
                geo_to_of.textContent = "from " + e.target.options[e.target.selectedIndex].textContent;
            } else {
                geo_to_of.textContent = "to " + e.target.options[e.target.selectedIndex].textContent;
            }

        } else if (e.target.options[e.target.selectedIndex].textContent === "relationship") {
            // hide fields
            start_node_div.style.display = "none";
            end_node_div.style.display = "none";

            // hide geo fields
            geo_start_node.style.display = "none";
            geo_end_node.style.display = "none";

            // enable field
            with_field.disabled = false;

            if (
                (
                    (
                        evo_op_field.options[evo_op_field.selectedIndex].textContent === "add"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    )
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                )
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // show fields
                start_node_div.style.display = "block";
                end_node_div.style.display = "block";

                // show geo fields
                geo_start_node.style.display = "inline-block";
                geo_end_node.style.display = "inline-block";

                // disable fields
                start_node_field.disabled = true;
                start_node_label_field.disabled = true;
                end_node_field.disabled = true;
                end_node_label_field.disabled = true;

                // connect to geo
                geo_to_of.textContent = "to " + e.target.options[e.target.selectedIndex].textContent;

                // show options of to-field
                with_div.querySelector("option[value='TYPE']").style.display = "block";
                // remove options of to-field
                with_div.querySelector("option[value='LABEL']").style.display = "none";

                if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                    geo_to_of.textContent = "of " + e.target.options[e.target.selectedIndex].textContent;
                } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                    && type_field.options[type_field.selectedIndex].textContent === "property") {
                    geo_to_of.textContent = "from " + e.target.options[e.target.selectedIndex].textContent;
                }

            } else {
                geo_to_of.textContent = "to " + e.target.options[e.target.selectedIndex].textContent;
            }

        } else {
            // disable field
            with_field.disabled = true;
            with_feature_field.disabled = true;
            rename_to_field.disabled = true;

            // set to field to default value
            with_field.value = "";
            with_feature_field.value = "";
            rename_to_field.value = "";
            start_node_field.value = "";
            end_node_field.value = "";

            // connect field content to geo field
            geo_to_of.textContent = "-----";
            geo_with.textContent = "-----";
            geo_with_feature.textContent = "-----";
            geo_rename_to.textContent = "-----";
            geo_start_node.textContent = "-----";
            geo_end_node.textContent = "-----";
        }
    }


    // handles field changes for with field
    if (e.target && e.target.matches("select.with")) {


        if (e.target.options[e.target.selectedIndex].textContent === "label" ||
            e.target.options[e.target.selectedIndex].textContent === "type") {
            // enable with field
            with_feature_field.disabled = false;

            // connect field content to geo field
            geo_with.textContent = "with " + e.target.options[e.target.selectedIndex].textContent;

        } else if (e.target.options[e.target.selectedIndex].textContent === "property") {
            // enable with field
            with_feature_field.disabled = false;

            // connect field content to geo field
            geo_with.textContent = "with " + e.target.options[e.target.selectedIndex].textContent;

        } else {
            // disable fields
            with_feature_field.disabled = true;
            split_at_field.disabled = true;
            rename_to_field.disabled = true;


            // set "empty" value for disabled field
            with_feature_field.value = "";
            rename_to_field.value = "";
            split_at_field.value = "";


            // connect field content to geo field
            geo_with.textContent = "-----";
            geo_with_feature.textContent = "-----";
            geo_rename_to.textContent = "-----";

            if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                    && (to_field.options[to_field.selectedIndex].textContent === "relationship"
                        || type_field.options[type_field.selectedIndex].textContent === "property"))
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                    && (type_field.options[type_field.selectedIndex].textContent === "node"
                        || type_field.options[type_field.selectedIndex].textContent === "relationship"))
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                    && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                        || (type_field.options[type_field.selectedIndex].textContent === "property"
                            && to_field.options[to_field.selectedIndex].textContent === "relationship")
                    )
                    || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                        && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                            || type_field.options[type_field.selectedIndex].textContent === "direction")
                    )
                )
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // hide fields
                start_node_label_div.style.display = "none";
                end_node_label_div.style.display = "none";

                // hide geo
                geo_start_node_label.style.display = "none";
                geo_end_node_label.style.display = "none";

                // disable fields
                start_node_field.disabled = true;
                // start_node_label_field.disabled = true;
                end_node_field.disabled = true;
                // end_node_label_field.disabled = true;

                // set "empty" values for disabled fields
                start_node_field.value = "";
                start_node_label_field.value = "";
                start_node_prop_key_field.value = "";
                end_node_field.value = "";
                end_node_label_field.value = "";
                end_node_prop_key_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
                geo_start_node_prop_key.textContent = "-----";
                geo_end_node.textContent = "-----";
                geo_end_node_label.textContent = "-----";
                geo_end_node_prop_key.textContent = "-----";

                if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                    && (type_field.options[type_field.selectedIndex].textContent === "node"
                        || type_field.options[type_field.selectedIndex].textContent === "relationship")) {

                    // disable fields
                    ingoing_rel_field.disabled = true;
                    outgoing_rel_field.disabled = true;

                    // set default value
                    ingoing_rel_field.value = "";
                    outgoing_rel_field.value = "";

                    // connect to geo
                    geo_ingoing_rel.textContent = "-----";
                    geo_outgoing_rel.textContent = "-----";
                    if (type_field.options[type_field.selectedIndex].textContent === "node") {
                        // connect to geo
                        geo_rename_to.textContent = "to relationship with type";
                    } else if (type_field.options[type_field.selectedIndex].textContent === "node") {
                        // connect to geo
                        geo_ingoing_rel.textContent = "to node with ingoing rel " + ingoing_rel_field.value;
                    }


                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // disable fields
                start_node_label_field.disabled = true;
                copy_with_rels_field.disabled = true;


                // set "empty" values for disabled fields
                start_node_label_field.value = "";
                copy_with_rels_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // set geo
                geo_start_node.textContent = "to relationship with type"
                geo_start_node_label.textContent = "-----";

                // default value for fields
                start_node_label_field.value = "";

                // disable field
                start_node_label_field.disabled = true;

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // disable fields
                copy_with_rels_field.disabled = true;
                start_node_label_field.disabled = true;

                // set default value
                copy_with_rels_field.value = "";
                start_node_label_field.value = "";

                // connect to geo
                geo_rename_to.textContent = "-----";
                geo_start_node_label.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "merge"
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && type_field.options[type_field.selectedIndex].textContent === "node")) {
                // hide fields
                //ToDo: Why is this hide not working - if hide here field can not be displayed anymore
                //start_node_label_field.style.display = "none";
                geo_start_node_label.style.display = "none";

                // disable fields
                start_node_field.disabled = true;
                start_node_label_field.disabled = true;

                // set default value
                start_node_field.value = "";
                start_node_label_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
            }
            // ToDo: else if split/ rename
        }
    }

    // handles field changes for with feature text field
    if (e.target && e.target.matches("input.with-feature")) {

        if (with_feature_field.value.length > 0) {
            // connect field content to geo field
            geo_with_feature.textContent = with_feature_field.value;
            //ToDO: GEO connection not yet working - only for first if statement - is move here correct or copy?
            if (
                (
                    (
                        evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                        && type_field.options[type_field.selectedIndex].textContent === "property"
                        && to_field.options[to_field.selectedIndex].textContent === "relationship"
                    )

                    || (
                        evo_op_field.options[evo_op_field.selectedIndex].textContent === "add"
                        && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                            || type_field.options[type_field.selectedIndex].textContent === "property")
                    )

                    || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                        && (type_field.options[type_field.selectedIndex].textContent === "property"
                            || type_field.options[type_field.selectedIndex].textContent === "direction"
                            || type_field.options[type_field.selectedIndex].textContent === "node"
                            || type_field.options[type_field.selectedIndex].textContent === "relationship")
                    )

                    || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                        && type_field.options[type_field.selectedIndex].textContent === "relationship")

                    || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "merge")
                )) {
                start_node_field.disabled = false;


            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete") {

                if (type_field.options[type_field.selectedIndex].textContent === "node") {
                    copy_with_rels_field.disabled = false;
                } else if (
                    type_field.options[type_field.selectedIndex].textContent === "relationship"
                    || (type_field.options[type_field.selectedIndex].textContent === "property"
                        && to_field.options[to_field.selectedIndex].textContent === "relationship")
                ) {
                    start_node_field.disabled = false;
                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy") {
                start_node_field.disabled = false;
                copy_with_rels_field.disabled = false;
                /*                to_field.disabled = false;
                                alert("with feature copy >0")*/

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename") {
                rename_to_field.disabled = false;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                split_at_field.disabled = false;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform") {
                /*                if (type_field.options[type_field.selectedIndex].textContent === "relationship") {
                                    start_node_field.disabled = false;
                                } else if (type_field.options[type_field.selectedIndex].textContent === "node") {
                                    start_node_label_field.disabled = false;
                                }*/
                start_node_field.disabled = false;
            } else {
                // connect field content to geo field
                // geo_with_feature.textContent = with_feature_field.value;

            }

        } else {
            // disable fields
            rename_to_field.disabled = true;
            split_at_field.disabled = true;


            // set empty value for disabled fields
            rename_to_field.value = "";
            split_at_field.value = "";

            // connect field content to geo field
            geo_with_feature.textContent = "-----";
            // set geo for rename to field if value is set empty
            geo_rename_to.textContent = "-----";
            geo_start_node.textContent = "-----";


            //ToDo: also for split and rename + check transform
            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // disable fields
                copy_with_rels_field.disabled = true;

                // set default value
                copy_with_rels_field.value = "";

                // connect to geo
                geo_rename_to.textContent = "-----";

            } else if (/*(evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship") ||*/
                (
                    (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                        || evo_op_field.options[evo_op_field.selectedIndex].textContent === "delete")
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                        || type_field.options[type_field.selectedIndex].textContent === "direction")
                )
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // hide fields
                start_node_label_div.style.display = "none";
                end_node_label_div.style.display = "none";

                // hide geo
                geo_start_node_label.style.display = "none";
                geo_end_node_label.style.display = "none";

                // disable fields
                start_node_field.disabled = true;
                end_node_field.disabled = true;

                // set "empty" values for disabled fields
                start_node_field.value = "";
                start_node_label_field.value = "";
                start_node_prop_key_field.value = "";
                end_node_field.value = "";
                end_node_label_field.value = "";
                end_node_prop_key_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";
                geo_start_node_prop_key.textContent = "-----";
                geo_end_node.textContent = "-----";
                geo_end_node_label.textContent = "-----";
                geo_end_node_prop_key.textContent = "-----";

                if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                    && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                    // disable fields
                    ingoing_rel_field.disabled = true;
                    outgoing_rel_field.disabled = true;

                    // set "empty" values for disabled fields
                    ingoing_rel_field.value = "";
                    outgoing_rel_field.value = "";

                    // connect to geo
                    geo_ingoing_rel.textContent = "-----";
                    geo_outgoing_rel.textContent = "-----";
                }

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // disable fields
                copy_with_rels_field.disabled = true;
                start_node_label_field.disabled = true;

                // set default value
                copy_with_rels_field.value = "";
                start_node_label_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "merge") {
                // disable fields
                start_node_field.disabled = true;
                start_node_label_field.disabled = true;

                // set "empty" values for disabled fields
                start_node_field.value = "";
                start_node_label_field.value = "";

                // connect to geo
                geo_start_node.textContent = "-----";
                geo_start_node_label.textContent = "-----";

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform") {
                if (type_field.options[type_field.selectedIndex].textContent === "relationship") {
                    start_node_field.disabled = true;
                } else if (type_field.options[type_field.selectedIndex].textContent === "node") {
                    start_node_label_field.disabled = true;

                    // set geo
                    geo_start_node.textContent = "to relationship with type"
                    geo_start_node_label.textContent = "-----";

                    // default value for fields
                    start_node_label_field.value = "";
                }
            }
        }
    }
    // handles field changes for evolution operation field
    if (e.target && e.target.matches("select.with-rels")) {
        if (e.target.options[e.target.selectedIndex].textContent === "---------") {
            // connect to geo
            // geo_rename_to.textContent = e.target.options[e.target.selectedIndex].textContent;
            geo_start_node.textContent = e.target.options[e.target.selectedIndex].textContent;

            // disable fields
            start_node_label_field.disabled = true;

            // set default value
            start_node_label_field.value = "";
        } else {
            // connect to geo
            // geo_rename_to.textContent = e.target.options[e.target.selectedIndex].textContent;
            geo_start_node.textContent = e.target.options[e.target.selectedIndex].textContent;

            // disable fields
            start_node_label_field.disabled = false;
        }
    }

    if (e.target && e.target.matches("input.start-node-label")) {

        if (start_node_label_field.value.length > 0) {
            // connect field content to geo field
            geo_start_node_label.textContent = start_node_label_field.value;

            //ToDO: only if label or type was selected otherwise other field enable necessary
            if (start_node_field.options[start_node_field.selectedIndex].textContent === "label"
                || start_node_field.options[start_node_field.selectedIndex].textContent === "property") {
                // enable field
                end_node_field.disabled = false;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "copy") {
                // set placholder attribute
                start_node_label_field.setAttribute("placeholder", "key1, key2...")

                // connect to geo
                geo_start_node_label.textContent = "and remove property key(s): " + start_node_label_field.value
            } else {
                end_node_field.disabled = true;
            }

        } else {
            // connect field content to geo field
            geo_start_node_label.textContent = "-----";
            geo_end_node.textContent = "-----";
            geo_end_node_label.textContent = "-----";

            // hide geo
            geo_end_node_label.style.display = "none";

            // disable field
            end_node_field.disabled = true;

            // hide fields
            end_node_label_div.style.display = "none";


            // set default value
            end_node_field.value = "";
            end_node_label_field.value = "";


            if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "type")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // disable field
                rename_to_field.disabled = true;

                // set default value
                rename_to_field.value = "";

                // reset geo
                geo_rename_to.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // disable field
                split_at_field.disabled = true;

                // set default value for field
                split_at_field.value = "";

                // set default value for geo
                geo_rename_to.textContent = "-----";
            }
        }

    }

    if (e.target && e.target.matches("select.end-node")) {
        // hide fields
        end_node_label_div.style.display = "none";
        end_node_prop_key_div.style.display = "none";

        // hide geo
        geo_end_node_prop_key.style.display = "none";

        if (e.target.options[e.target.selectedIndex].textContent === "label") {
            // show fields
            end_node_label_div.style.display = "block";

            // enable fields
            end_node_label_field.disabled = false;

            // show geo
            geo_end_node_label.style.display = "inline-block";

            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "move"
                && type_field.options[type_field.selectedIndex].textContent === "direction") {
                // connect field to geo field
                geo_end_node.textContent = "to end node with " + e.target.options[e.target.selectedIndex].textContent;
            } else {
                // connect field to geo field
                geo_end_node.textContent = "ending at node with " + e.target.options[e.target.selectedIndex].textContent;
            }


        } else if (e.target.options[e.target.selectedIndex].textContent === "label & property") {
            // show fields
            end_node_label_div.style.display = "block";
            end_node_prop_key_div.style.display = "block";

            // enable fields
            end_node_label_field.disabled = false;
            end_node_prop_key_field.disabled = true;

            // show geo
            geo_end_node_label.style.display = "inline-block";
            geo_end_node_prop_key.style.display = "inline-block";

            // connect field to geo field
            geo_end_node.textContent = e.target.options[e.target.selectedIndex].textContent;

        } else if (e.target.options[e.target.selectedIndex].textContent === "property") {
            // show fields
            end_node_prop_key_div.style.display = "block";

            // enable fields
            end_node_prop_key_field.disabled = false;

            // show geo
            geo_end_node_prop_key.style.display = "inline-block";

            // connect field to geo field
            geo_end_node.textContent = end_node_prop_key_field.value;

        } else {
            // hide fields
            end_node_label_div.style.display = "none";
            end_node_prop_key_div.style.display = "none";

            // set default value to fields
            end_node_label_field.value = "";
            end_node_prop_key_field.value = "";

            // show geo
            geo_end_node_label.style.display = "none";
            geo_end_node_prop_key.style.display = "none";

            // connect field to geo field
            geo_end_node.textContent = "-----";
            geo_end_node_label.textContent = "-----";
            geo_end_node_prop_key.textContent = "-----";

            if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "type")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // disable field
                rename_to_field.disabled = true;

                // set default value
                rename_to_field.value = "";

                // reset geo
                geo_rename_to.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                && (type_field.options[type_field.selectedIndex].textContent === "relationship"
                    || type_field.options[type_field.selectedIndex].textContent === "node")) {
                // disable fields
                ingoing_rel_field.disabled = true;
                outgoing_rel_field.disabled = true;

                // set default value
                ingoing_rel_field.value = "";
                outgoing_rel_field.value = "";

                // set default value for geo
                geo_ingoing_rel.textContent = "-----";
                geo_outgoing_rel.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // disable field
                split_at_field.disabled = true;

                // set default value for field
                split_at_field.value = "";

                // set default value for geo
                geo_rename_to.textContent = "-----";
            }

        }


    }

    if (e.target && e.target.matches("input.end-node-label")) {
        if (end_node_label_field.value.length > 0) {
            // connect field content to geo field
            geo_end_node_label.textContent = end_node_label_field.value;

            if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "type")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")) {
                rename_to_field.disabled = false;

            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform") {
                ingoing_rel_field.disabled = false;
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                split_at_field.disabled = false;
            }
        } else {
            // connect field content to geo field
            geo_start_node_label.textContent = "-----";
            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // disable fields
                ingoing_rel_field.disabled = true;
                outgoing_rel_field.disabled = true;

                // set default value
                ingoing_rel_field.value = "";
                outgoing_rel_field.value = "";

                // connect to geo
                geo_ingoing_rel.textContent = "-----";
                geo_outgoing_rel.textContent = "-----";
            } else if (
                (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "type")
                || (evo_op_field.options[evo_op_field.selectedIndex].textContent === "rename"
                    && type_field.options[type_field.selectedIndex].textContent === "property"
                    && to_field.options[to_field.selectedIndex].textContent === "relationship")
            ) {
                // disable field
                rename_to_field.disabled = true;

                // set default value for field
                rename_to_field.value = "";

                // set default value for geo
                geo_rename_to.textContent = "-----";
            } else if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "split"
                && type_field.options[type_field.selectedIndex].textContent === "relationship") {
                // disable field
                split_at_field.disabled = true;

                // set default value for field
                split_at_field.value = "";

                // set default value for geo
                geo_rename_to.textContent = "-----";
            }
        }
    }

    // handles field changes for ingoing rel field
    if (e.target && e.target.matches("input.ingoing-rel")) {
        if (ingoing_rel_field.value.length > 0) {
            outgoing_rel_field.disabled = false;
            if (evo_op_field.options[evo_op_field.selectedIndex].textContent === "transform"
                && type_field.options[type_field.selectedIndex].textContent === "node") {
                // connect to geo
                geo_ingoing_rel.textContent = ingoing_rel_field.value;
            } else {
                // connect to geo
                geo_ingoing_rel.textContent = "to node with ingoing rel " + ingoing_rel_field.value;
            }


        } else {
            outgoing_rel_field.disabled = true;

            // connect to geo
            geo_ingoing_rel.textContent = "-----";
        }
    }

    // handles field changes for outgoing rel field
    if (e.target && e.target.matches("input.outgoing-rel")) {
        if (ingoing_rel_field.value.length > 0) {
            // connect to geo
            geo_outgoing_rel.textContent = "and outgoing rel " + outgoing_rel_field.value;

        } else {
            // connect to geo
            geo_outgoing_rel.textContent = "-----";
        }
    }

    // handles field changes for rename to field
    if (e.target && e.target.matches("input.rename-to")) {

        if (rename_to_field.value.length > 0) {
            // connect field content to geo field
            geo_rename_to.textContent = "to " + rename_to_field.value;
        } else {
            // connect field content to geo field
            geo_rename_to.textContent = "-----";
        }
    }

    // handles field changes for rename to field
    if (e.target && e.target.matches("input.split-at")) {

        if (split_at_field.value.length > 0) {
            // connect field content to geo field
            geo_rename_to.textContent = "at " + split_at_field.value;
        } else {
            // connect field content to geo field
            geo_rename_to.textContent = "-----";
        }
    }


});




/*
-----------------------------------------------------------------------------------------
Reset Button
-----------------------------------------------------------------------------------------
 */

// get reset button by its id
let id_reset_button = document.getElementById("resetBtn");

// loop through all geo span tags inner html and set them to their default value of -----
function reset_geo() {
    let geo_elements = document.querySelectorAll('.geo-tag');
    let span_tag;
    for (span_tag = 0; span_tag < geo_elements.length; ++span_tag) {
        geo_elements[span_tag].textContent = '-----';
    }
}

// add click event listener for reset button
id_reset_button.addEventListener("click", function () {
    document.getElementById("id-evo-op-form").reset();
    reset_geo();
});

function parse_script_tag_data(elementID) {
    let output_data = JSON.parse(
        document.getElementById(elementID).textContent
    );
    return output_data
}


/*
-----------------------------------------------------------------------------------------
Parsing of data for scatter plot of
- initial schema
- latest schema
-----------------------------------------------------------------------------------------
 */

let dict1_json_data = parse_script_tag_data('dict1_initial_schema');
let dict2_json_data = parse_script_tag_data('dict2_new_schema');



// let labels = Object.keys(my_json_data);
let labels = Object.keys(dict1_json_data);


let node_count = [];
let rel_count = [];
let types = [];
let node_property_keys = [];
let rel_property_keys = [];
let relationships = [];
let node_dict = {};
let rel_dict = {};

let dict1_node_count = [];
let dict1_rel_count = [];
let dict1_node_property_keys = [];
let dict1_rel_property_keys = [];
let dict1_relationships = [];
let dict1_node_dict = {};
let dict1_rel_dict = {};

let dict2_node_count = [];
let dict2_rel_count = [];
let dict2_types = [];
let dict2_node_property_keys = [];
let dict2_rel_property_keys = [];
let dict2_relationships = [];
let dict2_node_dict = {};
let dict2_rel_dict = {};

// appends all count elements for all keys in my_json_data to new array called count
// function that loopes through JSON data to select specific items - defined in output_function
// result_array: information extracted from json_path
// output_function: fills result_array
function SelectValuesFromJSON(json_path, result_array, output_function) {

    do {
        if (json_path) {

            result_array.push([]);

            // iterate if length >1, add direction on position x and key at x, position y and key at y etc.
            if (Object.keys(json_path).length > 0) {
                // loop through relationship types where 1 or more keys are found
                let index_of_array = result_array.length - 1

                output_function(json_path, result_array, index_of_array);
            }

        } else {

            result_array.push([]);
        }
    } while (json_path > 0)
}

// select all keys which values are to be in result_array (for property keys)
function outputFunctionPropertyKeys(json_path, result_array, index_of_array) {
    Object.keys(json_path).forEach((items) => {
        // only adds number of relationship (=count) to string if direction is in
        result_array[index_of_array].push(items + " (" + json_path[items].type + ")")

    });
}


// select all keys which values are to be in result_array (for relationships)
function outputFunctionRelationships(json_path, result_array, index_of_array) {
    Object.keys(json_path).forEach((items) => {
        // only adds number of relationship (=count) to string if direction is in
        if (json_path[items].direction === "out") {
            result_array[index_of_array].push(items, json_path[items].direction);
        } else (
            result_array[index_of_array].push(items, json_path[items].count, json_path[items].direction)
        )
    });
}

function ParseJSONDataForDiagrams(json_data, node_dict, node_count, node_property_keys, relationships, rel_dict,
                                  rel_count, rel_property_keys, rel_node_labels) {
    Object.keys(json_data).forEach((key) => {
        switch (json_data[key].type) {
            case "node":
                node_dict[key] = json_data[key];
                node_count.push(node_dict[key].count);

                //select all desired information of json_data
                SelectValuesFromJSON(node_dict[key].properties, node_property_keys, outputFunctionPropertyKeys);
                SelectValuesFromJSON(node_dict[key].relationships, relationships, outputFunctionRelationships);

                break;
            case "relationship":
                rel_dict[key] = json_data[key];
                rel_count.push(rel_dict[key].count)

                //select all desired information of json_data
                SelectValuesFromJSON(rel_dict[key].properties, rel_property_keys, outputFunctionPropertyKeys);
                break;
        }
    });
}


ParseJSONDataForDiagrams(dict1_json_data, dict1_node_dict, dict1_node_count,
    dict1_node_property_keys, dict1_relationships, dict1_rel_dict,
    dict1_rel_count, dict1_rel_property_keys);

let dict1_node_labels = Object.keys(dict1_node_dict);
let dict1_rel_lables = Object.keys(dict1_rel_dict);

ParseJSONDataForDiagrams(dict2_json_data, dict2_node_dict, dict2_node_count,
    dict2_node_property_keys, dict2_relationships, dict2_rel_dict,
    dict2_rel_count, dict2_rel_property_keys);

let dict2_node_labels = Object.keys(dict2_node_dict);
let dict2_rel_lables = Object.keys(dict2_rel_dict);


console.log(`Node dict: ${node_dict}`);
console.log(dict1_json_data);
console.log(node_dict);
console.log(rel_dict);


// access current schema button
let currentSchemaButton = document.getElementById("current-schema-button");

// show information on mouseover
currentSchemaButton.addEventListener("mouseover", function () {
    document.getElementById('popup').style.display = 'block';
});

currentSchemaButton.addEventListener("mouseout", function () {
    document.getElementById('popup').style.display = 'none';
});



/*
-----------------------------------------------------------------------------------------
Scatter Plot Creation
-----------------------------------------------------------------------------------------
 */

function config_schema_diagram(dataset, labelXAxes, labelYAxes, schema_callbacks) {
    const config_schema_diagram = {
        type: 'line',
        fill: false,
        data: dataset,
        options: {
            responsive: true,
            elements: {
                bar: {
                    borderWidth: 2,
                }
            },
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: labelXAxes,
                    }
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: labelYAxes,
                    }
                }],
            },
            events: ['click'],
            legend: {
                display: true,
            },
            tooltips: {
                mode: 'index',
                callbacks: schema_callbacks,
            },

        }
    };

    return config_schema_diagram
}


const initial_and_latest_schema_callbacks = {
    label: function (tooltipItem, data) {
        return 'Count: ' + data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
    },
    beforeFooter: function (tooltipItems, data) {
        let number_of_entities = 0;
        let prop = dict1_node_property_keys;
        let prop_new = dict2_node_property_keys;
        let rel = dict1_relationships;
        let rel_new = dict2_relationships;

        tooltipItems.forEach(function (tooltipItem) {
            number_of_entities = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
            array_index = tooltipItem.index;
        });

        let data_to_return = [
            ['Initial schema of entity type'],
            ['Property key(s): ' + prop[array_index]],
            ['Relationship(s): ' + rel[array_index]],
            [' '],
            ['Latest schema of entity type'],
            ['Property key(s): ' + prop_new[array_index]],
            ['Relationship(s): ' + rel_new[array_index]]];
        return data_to_return;
    },
};


console.log(dict1_node_labels.length, dict1_node_labels)

// id_range_slider: String to set attributes may and value if lower than default value
// id_displayed_value_of_range_slider: String to set visible value of slider depending on value
// label_dict: Dictionary to check for length
function set_values_for_range(id_range_slider, id_displayed_value_of_range_slider, label_dict) {
    if (document.getElementById(id_range_slider).value > label_dict.length) {
        // set value and max if value > 15
        document.getElementById(id_range_slider).setAttribute("max", label_dict.length);
        document.getElementById(id_range_slider).setAttribute("value", label_dict.length);
        document.getElementById(id_displayed_value_of_range_slider).textContent = label_dict.length;
    } else {
        document.getElementById(id_range_slider).setAttribute("max", label_dict.length);
    }
}

if (Object.keys(dict1_json_data).length === 0) {
    set_values_for_range("range-datapoints", "value-of-range", dict2_node_labels)
} else {
    set_values_for_range("range-datapoints", "value-of-range", dict1_node_labels)
}

// if no initial schema use dict2 data
function data_initial_and_latest_labels() {
    if (Object.keys(dict1_json_data).length === 0) {
        console.log("dict1 is empty 0");
        let labels = dict2_node_labels.slice(0, document.getElementById("range-datapoints").value);
        return labels
    } else {
        let labels = dict1_node_labels.slice(0, document.getElementById("range-datapoints").value);
        console.log("dict1 > 0");
        return labels
    }
    return labels
}


const data_initial_and_latest = {
    labels: data_initial_and_latest_labels(),
    datasets: [
        {
            label: 'Initial db statistics',
            data: dict1_node_count,
            borderColor: "#28a745",
            backgroundColor: "#28a745",
            pointBackgroundColor: "#28a745",
            pointRadius: 4,
            fill: false,
            showLine: false,
            order: 0
        },
        {
            label: 'Latest db statistics',
            data: dict2_node_count,
            borderColor: "#0F52BA",
            backgroundColor: "#0F52BA",
            pointBackgroundColor: "#0F52BA",
            type: 'line',
            pointRadius: 4,
            fill: false,
            showLine: false,
            order: 1
        }
    ]
};

let config_initial_and_latest_schema = config_schema_diagram(data_initial_and_latest,
    'Name of Entities', 'Number of Entities', initial_and_latest_schema_callbacks)

const initial_and_new_schema_chart = new Chart("initial-and-latest-schema-chart", config_initial_and_latest_schema);


/*
-----------------------------------------------------------------------------------------
Animation of Range Bar
-----------------------------------------------------------------------------------------
 */

// https://www.youtube.com/watch?v=mIMauE-DodA
// gives range input tag its functionality

function dynamic_input_range(input_range_id, chart_name, label_dict, value_of_input_range_id) {
    document.getElementById(input_range_id).addEventListener("input", function () {
        // console.log(this.value)
        console.log(chart_name.data.labels)
        const labelsCopy = label_dict.slice(0, this.value);
        console.log(labelsCopy)
        chart_name.data.labels = labelsCopy;
        chart_name.update();

        // displays current value
        document.getElementById(value_of_input_range_id).textContent = this.value;
    });
}

if (Object.keys(dict1_json_data).length === 0) {
    dynamic_input_range("range-datapoints", initial_and_new_schema_chart, dict2_node_labels,
        "value-of-range");
} else {
    dynamic_input_range("range-datapoints", initial_and_new_schema_chart, dict1_node_labels,
        "value-of-range");
}

/*
-----------------------------------------------------------------------------------------
Relationship Schema Scatter Polt
-----------------------------------------------------------------------------------------
 */

const initial_and_latest_rel_schema_callbacks = {
    label: function (tooltipItem, data) {
        return 'Count: ' + data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
    },
    beforeFooter: function (tooltipItems, data) {
        let number_of_entities = 0;
        let prop = dict1_rel_property_keys;
        let prop_new = dict2_rel_property_keys;


        tooltipItems.forEach(function (tooltipItem) {
            number_of_entities = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
            array_index = tooltipItem.index;
        });

        let data_to_return = [
            ['Initial schema of entity type'],
            ['Property key(s): ' + prop[array_index]],
            [' '],
            ['Latest schema of entity type'],
            ['Property key(s): ' + prop_new[array_index]]];
        return data_to_return;
    },
};


//
console.log(dict1_node_labels.length, dict1_node_labels)


// ToDo make reusable!
function initial_schema_emtpy (){
    if (Object.keys(dict1_json_data).length === 0) {
        set_values_for_range("range-datapoints-rel", "value-of-range-rels", dict2_rel_lables)
    } else {
        set_values_for_range("range-datapoints-rel", "value-of-range-rels", dict1_rel_lables)
    }
}
initial_schema_emtpy();



function data_initial_and_latest_rel_labels() {
    if (Object.keys(dict1_json_data).length === 0) {
        console.log("dict1 is empty 0");
        let labels = dict2_rel_lables.slice(0, document.getElementById("range-datapoints-rel").value);
        return labels
    } else {
        let labels = dict1_rel_lables.slice(0, document.getElementById("range-datapoints-rel").value);
        console.log("dict1 > 0");
        return labels
    }
    return labels
}



const rel_data_initial_and_latest = {
    labels: data_initial_and_latest_rel_labels(),
    datasets: [
        {
            label: 'Initial db statistic',
            data: dict1_rel_count,
            borderColor: "#28a745",
            backgroundColor: "#28a745",
            pointBackgroundColor: "#28a745",
            pointRadius: 4,
            fill: false,
            showLine: false,
            order: 0
        },
        {
            label: 'Latest db statistic',
            data: dict2_rel_count,
            borderColor: "#0F52BA",
            backgroundColor: "#0F52BA",
            pointBackgroundColor: "#0F52BA",
            pointRadius: 4,
            type: 'line',
            fill: false,
            showLine: false,
            order: 1
        }
    ]
};

let config_initial_and_latest_rel_schema = config_schema_diagram(rel_data_initial_and_latest,
    'Name of Entities', 'Number of Entities', initial_and_latest_rel_schema_callbacks)

const initial_and_new_rel_schema_chart = new Chart("initial-and-latest-rel-schema-chart", config_initial_and_latest_rel_schema);

// https://www.youtube.com/watch?v=mIMauE-DodA
// gives range input tag its functionality

if (Object.keys(dict1_json_data).length === 0) {
    dynamic_input_range("range-datapoints-rel", initial_and_new_rel_schema_chart, dict2_rel_lables,
        "value-of-range-rels");
} else {
    dynamic_input_range("range-datapoints-rel", initial_and_new_rel_schema_chart, dict1_rel_lables,
        "value-of-range-rels");
}

//-----------------------------------------------------------------------------------
// Creation of diagram for evo ops over time
//-----------------------------------------------------------------------------------
let evo_op_add_data = parse_script_tag_data('evo_ops_over_time_add_data');
let evo_op_rename_data = parse_script_tag_data('evo_ops_over_time_rename_data');
let evo_op_delete_data = parse_script_tag_data('evo_ops_over_time_delete_data');
let evo_op_transform_data = parse_script_tag_data('evo_ops_over_time_transform_data');
let evo_op_copy_data = parse_script_tag_data('evo_ops_over_time_copy_data');
let evo_op_move_data = parse_script_tag_data('evo_ops_over_time_move_data');
let evo_op_split_data = parse_script_tag_data('evo_ops_over_time_split_data');
let evo_op_merge_data = parse_script_tag_data('evo_ops_over_time_merge_data');

function evo_op_labels(evo_op_data) {
    let evo_op_count = 1;
    let evo_ops_over_time_labels = [];
    evo_op_data.forEach(function (evo_op) {
        evo_ops_over_time_labels.push(evo_op_count++)
    });
    return evo_ops_over_time_labels
}

const evo_ops_over_time_data = {
    labels: evo_op_labels(evo_op_add_data),
    datasets: [
        {
            label: 'Add',
            data: evo_op_add_data,
            borderColor: "#1e8449",
            backgroundColor: "#1e8449",
            pointBackgroundColor: "#1e8449",
            pointRadius: 4,
            fill: false,
        },
        {
            label: 'Rename',
            data: evo_op_rename_data,
            borderColor: "#3498db",
            backgroundColor: "#3498db",
            pointBackgroundColor: "#3498db",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Delete',
            data: evo_op_delete_data,
            borderColor: "#ec7063",
            backgroundColor: "#ec7063",
            pointBackgroundColor: "#ec7063",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Transform',
            data: evo_op_transform_data,
            borderColor: "#eb984e",
            backgroundColor: "#eb984e",
            pointBackgroundColor: "#eb984e",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Copy',
            data: evo_op_copy_data,
            borderColor: "#0F52BA",
            backgroundColor: "#0F52BA",
            pointBackgroundColor: "#0F52BA",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Move',
            data: evo_op_move_data,
            borderColor: "#884ea0",
            backgroundColor: "#884ea0",
            pointBackgroundColor: "#884ea0",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Split',
            data: evo_op_split_data,
            borderColor: "#16a085",
            backgroundColor: "#16a085",
            pointBackgroundColor: "#16a085",
            pointRadius: 4,
            type: 'line',
            fill: false,
        },
        {
            label: 'Merge',
            data: evo_op_merge_data,
            borderColor: "#f7dc6f",
            backgroundColor: "#f7dc6f",
            pointBackgroundColor: "#f7dc6f",
            pointRadius: 4,
            type: 'line',
            fill: false,
        }
    ]
};


const evo_ops_over_time_callbacks = {
    label: function (tooltipItem, data) {
        return data.datasets[tooltipItem.datasetIndex].label + " " +
            data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
    }
};


let config_evo_ops_over_time = config_schema_diagram(evo_ops_over_time_data,
    'Transactions', 'Frequency', evo_ops_over_time_callbacks)

new Chart("evo-ops-over-time-chart", config_evo_ops_over_time);

