'''
Here the template for the evolution form (Evolution Application) is created including all its components.
This includes
- all evolution operations
- all fields of the evolution form
A helper is used to create multiple identical forms.

All fields are set here. The field animation is acquired via JavaScript and CSS.
'''

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django.forms import formset_factory

# https://docs.djangoproject.com/en/2.2/ref/forms/fields/
# https://docs.djangoproject.com/en/2.2/topics/forms/


from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

TOTAL_FORM_COUNT = 'TOTAL_FORMS'
INITIAL_FORM_COUNT = 'INITIAL_FORMS'
MIN_NUM_FORM_COUNT = 'MIN_NUM_FORMS'
MAX_NUM_FORM_COUNT = 'MAX_NUM_FORMS'
ORDERING_FIELD_NAME = 'ORDER'
DELETION_FIELD_NAME = 'DELETE'

data = {
    'form-TOTAL_FORMS': '1',
    'form-INITIAL_FORMS': '0',
    'form-MAX_NUM_FORMS': '5',
    'form-0-title': '',
    'form-0-pub_date': '',
}


class DbConnectionForm(forms.Form):
    uri = forms.CharField(label="URI", max_length=100,
                          widget=forms.TextInput(attrs={'class': 'form-control',
                                                        'pattern': 'bolt:\/\/[A-za-z0-9]*:{1}[0-9]{4}',
                                                        'value': 'bolt://localhost:7687',
                                                        'placeholder': 'bolt://localhost:7687'}), required=True)
    user = forms.CharField(label="User", max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'value': 'neo4j',
                                                         'placeholder': 'neo4j'}),
                           required=True)
    database = forms.CharField(label="Database Name", max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'value': 'neo4j',
                                                             'placeholder': 'neo4j'}),
                               required=True)
    password = forms.CharField(label="Password", max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'id': 'password',
                                                             'type': 'password', 'data-toggle': 'password',
                                                             'placeholder': 'Password'}), required=True)
    save_connection = forms.BooleanField(required=False)


class EvoOpsForm(forms.Form):
    ADD = "ADD"
    RENAME = "RENAME"
    DELETE = "DELETE"
    TRANSFORM = "TRANSFORM"
    COPY = "COPY"
    MOVE = "MOVE"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    ENTITY_TYPE = "ENTITY_TYPE"
    FEATURE = "FEATURE"
    NODE = "NODE"
    RELATIONSHIP = "RELATIONSHIP"
    INNER_JOIN = "INNER_JOIN"
    FULL_OUTER_INCLUSIVE = "FULL_OUTER_INCLUSIVE"
    FULL_OUTER_EXCLUSIVE = "FULL_OUTER_EXCLUSIVE"
    RIGHT_JOIN = "RIGHT_JOIN"
    LEFT_JOIN = "LEFT_JOIN"
    ALL = "ALL"
    SELECTED = "SELECTED"
    LABEL = "LABEL"
    OVERWRITE_LABEL = "OVERWRITE_LABEL"
    ADDITONAL_LABEL = "ADDITONAL_LABEL"
    ALL_LABELS = "ALL_LABELS"
    SELECTED_LABEL = "SELECTED_LABEL"
    TYPE = "TYPE"
    PROPERTY = "PROPERTY"
    ALL_PROPERTIES = "ALL_PROPERTIES"
    SELECTED_PROPERTY = "SELECTED_PROPERTY"
    DIRECTION = "DIRECTION"
    LABEL_AND_PROPERTY = "LABEL_AND_PROPERTY"
    WITH_RELATIONSHIPS = "TRUE"
    WITHOUT_RELATIONSHIPS = "FALSE"

    EVO_OPS_CHOICES = [
        (
            "Single-type",
            (
                (ADD, "add"),
                (RENAME, "rename"),
                (DELETE, "delete"),
                (TRANSFORM, "transform"),
            ),
        ),
        (
            "Multi-type",
            (
                (COPY, "copy"),
                (MOVE, "move"),
                (SPLIT, "split"),
                (MERGE, "merge"),
            ),
        ),
    ]

    TYPE_CHOICES = [
        (
            "Entity Type",
            (
                (NODE, "node"),
                (RELATIONSHIP, "relationship"),
            ),
        ),
        (
            "Feature",
            (
                (LABEL, "label"),
                # (OVERWRITE_LABEL, "label(s) by overwriting"),
                # (ADDITONAL_LABEL, "additional label(s)"),
                # (ALL_LABELS, "all labels"),
                # (SELECTED_LABEL, "selected label(s)"),
                (TYPE, "type"),
                (PROPERTY, "property"),
                # (ALL_PROPERTIES, "all properties"),
                # (SELECTED_PROPERTY, "selected propertie(s)"),
                (DIRECTION, "direction"),
            ),
        ),
    ]

    ENTITY_TYPE_CHOICES = (
        (NODE, "node"),
        (RELATIONSHIP, "relationship"),
    )

    FEATURE_CHOICES = (
        (LABEL, "label"),
        # (ALL_LABELS, "all labels"),
        # (SELECTED_LABEL, "selected label(s)"),
        (TYPE, "type"),
        # (PROPERTY, "property"),
        # (ALL_PROPERTIES, "all properties"),
        # (SELECTED_PROPERTY, "selected propertie(s)"),
    )

    JOIN_OPTIONS_CHOICES = (
        # (INNER_JOIN, "inner join"),
        (FULL_OUTER_INCLUSIVE, "full outer inclusive"),
        # (FULL_OUTER_EXCLUSIVE, "full outer exclusive"),
        # (RIGHT_JOIN, "right join"),
        # (LEFT_JOIN, "left join"),
    )

    INITIAL_REL_START_END_NODE_CHOICE = (
        (LABEL, "label"),
    )

    START_END_NODE_CHOICE = (
        (LABEL, "label"),
        # (LABEL_AND_PROPERTY, "label & property"),
        # (PROPERTY, "property"),
    )

    COPY_WITH_RELS_CHOICE = (
        (WITH_RELATIONSHIPS, "with relationships"),
        (WITHOUT_RELATIONSHIPS, "without relationships"),
    )

    evo_op = forms.ChoiceField(label="Operation", required=False, initial='---------',
                               choices=BLANK_CHOICE_DASH + list(EVO_OPS_CHOICES),
                               widget=forms.Select(attrs={'class': 'form-control evo-op'}))
    join_options = forms.ChoiceField(label="Join Options", required=False,
                                     choices=BLANK_CHOICE_DASH + list(JOIN_OPTIONS_CHOICES),
                                     initial=BLANK_CHOICE_DASH, widget=forms.Select(
            attrs={'class': 'form-control evo-op-form join-options'}))
    type = forms.ChoiceField(label="Type", required=False, choices=BLANK_CHOICE_DASH + list(TYPE_CHOICES),
                             initial=BLANK_CHOICE_DASH, widget=forms.Select(
            attrs={'class': 'form-control evo-op-form type'}))
    from_field = forms.ChoiceField(label="Entity type", required=False, initial='---------',
                                   choices=BLANK_CHOICE_DASH + list(ENTITY_TYPE_CHOICES),
                                   disabled=False, widget=forms.Select(
            attrs={'class': 'form-control evo-op-form from-entity-type'}))
    feature_text_field = forms.CharField(required=False, disabled=False, max_length=100,
                                         initial='',
                                         widget=forms.TextInput(
                                             attrs={'class': 'form-control evo-op-form feature-text'}))
    property_key_field = forms.CharField(max_length=100, required=False, disabled=False,
                                         widget=forms.TextInput(
                                             attrs={'class': 'form-control evo-op-form property-key',
                                                    'placeholder': 'key'}))
    property_value_field = forms.CharField(max_length=100, required=False, disabled=False,
                                           widget=forms.TextInput(
                                               attrs={'class': 'form-control evo-op-form property-value',
                                                      'placeholder': 'value1, value2...'}))
    initial_rel_start_node_field = forms.ChoiceField(required=False, label="Start node", initial='---------',
                                                     choices=BLANK_CHOICE_DASH + list(
                                                         INITIAL_REL_START_END_NODE_CHOICE),
                                                     widget=forms.Select(attrs={
                                                         'class': 'form-control evo-op-form initial-rel-start-node'}))
    initial_rel_start_node_label_field = forms.CharField(required=False, disabled=False, label="with label",
                                                         max_length=100,
                                                         initial='',
                                                         widget=forms.TextInput(
                                                             attrs={
                                                                 'class': 'form-control evo-op-form initial-rel-start-node-label',
                                                                 'placeholder': 'label'}))
    initial_rel_end_node_field = forms.ChoiceField(required=False, label="End node", initial='---------',
                                                   choices=BLANK_CHOICE_DASH + list(INITIAL_REL_START_END_NODE_CHOICE),
                                                   widget=forms.Select(attrs={
                                                       'class': 'form-control evo-op-form initial-rel-end-node'}))
    initial_rel_end_node_label_field = forms.CharField(required=False, disabled=False, label="with label",
                                                       max_length=100,
                                                       initial='',
                                                       widget=forms.TextInput(
                                                           attrs={
                                                               'class': 'form-control evo-op-form initial-rel-end-node-label',
                                                               'placeholder': 'label'}))

    to_field = forms.ChoiceField(label="To", required=False, disabled=False, initial='---------',
                                 choices=BLANK_CHOICE_DASH + list(ENTITY_TYPE_CHOICES),
                                 widget=forms.Select(attrs={'class': 'form-control evo-op-form to'}))
    with_field = forms.ChoiceField(label="With", required=False, disabled=False, initial='---------',
                                   choices=BLANK_CHOICE_DASH + list(FEATURE_CHOICES),
                                   widget=forms.Select(attrs={'class': 'form-control evo-op-form with'}))

    with_feature_text_field = forms.CharField(disabled=False, max_length=100, required=False, initial='',
                                              widget=forms.TextInput(
                                                  attrs={'class': 'form-control evo-op-form with-feature'}))

    copy_with_rels_field = forms.ChoiceField(required=False, label="with relationships", initial='---------',
                                             choices=BLANK_CHOICE_DASH + list(COPY_WITH_RELS_CHOICE),
                                             widget=forms.Select(attrs={'class': 'form-control evo-op-form with-rels'}))

    start_node_field = forms.ChoiceField(required=False, label="Start node", initial='---------',
                                         choices=BLANK_CHOICE_DASH + list(START_END_NODE_CHOICE),
                                         widget=forms.Select(attrs={'class': 'form-control evo-op-form start-node'}))
    start_node_label_field = forms.CharField(required=False, disabled=False, label="with label", max_length=100,
                                             initial='',
                                             widget=forms.TextInput(
                                                 attrs={'class': 'form-control evo-op-form start-node-label'}))
    start_node_property_key_field = forms.CharField(required=False, disabled=False, label="property key",
                                                    max_length=100, widget=forms.TextInput(
            attrs={'class': 'form-control evo-op-form',
                   'placeholder': 'property key'}))
    # start_node_property_value_field = forms.CharField(required=False, disabled=False, label="and value",
    #                                                   max_length=100, widget=forms.TextInput(
    #         attrs={'class': 'form-control evo-op-form start-node-prop-key',
    #                'placeholder': 'property value'}))
    end_node_field = forms.ChoiceField(required=False, label="End node", initial='---------',
                                       choices=BLANK_CHOICE_DASH + list(START_END_NODE_CHOICE),
                                       widget=forms.Select(attrs={'class': 'form-control evo-op-form end-node'}))
    end_node_label_field = forms.CharField(required=False, disabled=False, label="with label", max_length=100,
                                           initial='',
                                           widget=forms.TextInput(
                                               attrs={'class': 'form-control evo-op-form end-node-label'}))
    end_node_property_key_field = forms.CharField(required=False, disabled=False, label="property key", max_length=100,
                                                  widget=forms.TextInput(
                                                      attrs={'class': 'form-control evo-op-form show end-node-prop-key',
                                                             'placeholder': 'property key'}))
    # end_node_property_value_field = forms.CharField(required=False, disabled=False, label="and value", max_length=100,
    #                                                 widget=forms.TextInput(
    #                                                     attrs={'class': 'form-control evo-op-form show',
    #                                                            'placeholder': 'property value'}))
    split_at_field = forms.CharField(required=False, disabled=False, label="at property key", max_length=100,
                                     widget=forms.TextInput(attrs={'class': 'form-control evo-op-form split-at',
                                                                   'placeholder': 'property key'}))
    rename_to_field = forms.CharField(required=False, disabled=False, label="Rename to", max_length=100,
                                      initial='', widget=forms.TextInput(attrs={
            'class': 'form-control evo-op-form rename-to'}))
    ingoing_rel_field = forms.CharField(required=False, disabled=False, label="Ingoing Type", max_length=100,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control evo-op-form show ingoing-rel',
                                                   'placeholder': 'type of ingoing rel'}))
    outgoing_rel_field = forms.CharField(required=False, disabled=False, label="Outgoing Type", max_length=100,
                                         widget=forms.TextInput(
                                             attrs={'class': 'form-control evo-op-form show outgoing-rel',
                                                    'placeholder': 'type of outgoing rel'}))

    def __init__(self, *args, **kwargs):
        super(EvoOpsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'id-evo-op-form'


EvoOpsFormSet = formset_factory(EvoOpsForm, extra=1)


# ToDo: use this helper for empty form and make new helper for first form with + Button!
class ExampleFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.form_id = 'id-key-value-form'
        self.form_method = 'post'
        self.layout = Layout(
            Row(
                Column('property_key_field', css_class="col-md-3"),
                Column(FieldWithButtons('property_value_field',
                                        StrictButton("-", css_class="btn value-key-button btn-outline-danger "
                                                                    "data-formset-remove-form2"),
                                        input_size="input-group"), css_class="col-md-3"),
                css_class="input-group"
            )
        )
