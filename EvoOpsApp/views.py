import os
import json
from json import JSONDecodeError
from timeit import default_timer as timer
from datetime import timedelta


import dictdiffer

from django.contrib import messages

from .models import AddNodeEntity, AddRelEntity, AddFeature, RenameFeature, DeleteEntityType, RemoveFeature, \
    TransformEntityType, CopyEntityType, \
    CopyFeature, SplitEntityType, MoveEntityType, MoveFeature, MergeEntityTypes, Connection, Schema
from django.shortcuts import render
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import mimetypes
from .forms import DbConnectionForm, EvoOpsForm, EvoOpsFormSet, ExampleFormSetHelper

from django.http import HttpResponse, HttpResponseRedirect

from .forms import DbConnectionForm


def index(request):
    return render(request, 'home.html')


def nautilus(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form_db_connection = DbConnectionForm(request.POST)
        form_evo_ops = EvoOpsForm(request.POST)
        formset_evo_ops = EvoOpsFormSet(request.POST)

        helper = ExampleFormSetHelper()

        # use this syntax to get geo information
        # iterate over geo ids and use geo-evo-op1, geo-type1 ..., geo-evo-op2, geo-type2 etc.
        searchWord = request.POST.get('search', '')
        print(searchWord)
        if 'submit-button' in request.POST:
            start_submitt_button_pressed = timer()
            # check whether it's valid:
            # if form_db_connection.is_valid() and formset_evo_ops.is_valid() and formset_property_value_key.is_valid():
            if form_db_connection.is_valid() and formset_evo_ops.is_valid():
                history = []
                uri = form_db_connection.cleaned_data.get("uri")
                user = form_db_connection.cleaned_data.get("user")
                database_name = form_db_connection.cleaned_data.get("database")
                password = form_db_connection.cleaned_data.get("password")
                save_connection = form_db_connection.cleaned_data.get("save_connection")

                start_db_connection = timer()
                # database_name = 'bloom'
                session = Connection(uri, user, password).driver

                end_db_connection = timer()

                if save_connection is False:
                    form_db_connection = DbConnectionForm()
                else:
                    pass

                start_for_loop = timer()
                # get data of all form fields
                for form_evo_ops in formset_evo_ops:
                    start_form_variables = timer()
                    # get the data from all necessary form fields
                    evo_op = form_evo_ops.cleaned_data.get("evo_op")
                    join_options = form_evo_ops.cleaned_data.get("join_options")
                    type = form_evo_ops.cleaned_data.get("type")
                    # entity_type = form_evo_ops.cleaned_data.get("entity_type")
                    # feature = form_evo_ops.cleaned_data.get("feature")
                    from_field = form_evo_ops.cleaned_data.get("from_field")

                    feature_text_field = form_evo_ops.cleaned_data.get("feature_text_field")
                    property_key_field = form_evo_ops.cleaned_data.get("property_key_field")
                    property_value_field = form_evo_ops.cleaned_data.get("property_value_field")
                    initial_rel_start_node_field = form_evo_ops.cleaned_data.get("initial_rel_start_node_field")
                    initial_rel_start_node_label_field = form_evo_ops.cleaned_data.get(
                        "initial_rel_start_node_label_field")
                    initial_rel_end_node_field = form_evo_ops.cleaned_data.get(
                        "initial_rel_end_node_field")
                    initial_rel_end_node_label_field = form_evo_ops.cleaned_data.get(
                        "initial_rel_end_node_label_field")
                    with_feature_text_field = form_evo_ops.cleaned_data.get("with_feature_text_field")
                    copy_with_rels_field = form_evo_ops.cleaned_data.get("copy_with_rels_field")
                    with_field = form_evo_ops.cleaned_data.get("with_field")
                    to_field = form_evo_ops.cleaned_data.get("to_field")
                    rename_to_text_field = form_evo_ops.cleaned_data.get("rename_to_field")
                    split_at_field = form_evo_ops.cleaned_data.get("split_at_field")

                    start_node_field = form_evo_ops.cleaned_data.get("start_node_field")
                    start_node_label_field = form_evo_ops.cleaned_data.get("start_node_label_field")
                    end_node_field = form_evo_ops.cleaned_data.get("end_node_field")
                    end_node_label_field = form_evo_ops.cleaned_data.get("end_node_label_field")

                    ingoing_rel_field = form_evo_ops.cleaned_data.get("ingoing_rel_field")
                    outgoing_rel_field = form_evo_ops.cleaned_data.get("outgoing_rel_field")
                    end_form_variables = timer()
                    print(evo_op, type)

                    # ----------------------------------------------------------------------
                    # ADD
                    # ----------------------------------------------------------------------
                    if evo_op == form_evo_ops.ADD and type == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()

                        # with session.session(database="bloom") as session:
                        print(f'Database name: {database_name}')
                        records, neo4j_query_time, query_time = AddNodeEntity.create_new_node_with_label_x(
                            session, with_feature_text_field, database_name)
                        # records, neo4j_query_time, query_time = session.execute_write(
                        #     AddNodeEntity.create_new_node_with_label_x, with_feature_text_field)
                        print(f'Records ADD NODE: {records}')

                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + form_evo_ops.LABEL + " " + with_feature_text_field
                        history.append(geo)
                        print("Use function here for add node with label X")
                        print(records, history)
                        # return records

                    elif evo_op == form_evo_ops.ADD and type == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records, neo4j_query_time = AddRelEntity.create_rels_with_type_x(session,
                                                                                         with_feature_text_field,
                                                                                         start_node_label_field,
                                                                                         end_node_label_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + form_evo_ops.TYPE + " " + with_feature_text_field + \
                              " to start node with " + form_evo_ops.LABEL + " " + start_node_label_field + \
                              " and end node with " + form_evo_ops.LABEL + " " + end_node_label_field
                        history.append(geo)
                        print("Use function here for add node with label X")
                        print(records, history)

                    elif evo_op == form_evo_ops.ADD and type == form_evo_ops.LABEL and \
                            to_field == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        # ToDo: make difference between add with ignore vs overwrite!!
                        records, neo4j_query_time = AddFeature.add_labels_with_ignore_semantics(session,
                                                                                                with_feature_text_field,
                                                                                                feature_text_field.split(
                                                                                                    ", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " " + feature_text_field + " to " + to_field + " with " \
                              + with_field + " " + with_feature_text_field
                        history.append(geo)
                        print("Use function here for add label x to node with label y")
                        print(records, history)

                    elif evo_op == form_evo_ops.ADD and type == form_evo_ops.PROPERTY and \
                            to_field == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = AddFeature.add_node_properties(session, with_feature_text_field,
                                                                                   feature_text_field.split(", "),
                                                                                   property_value_field.split(", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with key(s) " + feature_text_field + " and value(s) " + \
                              property_value_field + " to " + to_field + " with " \
                              + with_field + " " + with_feature_text_field
                        history.append(geo)
                        print("Use function here for add node property x to node with label y")
                        print(records)

                    elif evo_op == form_evo_ops.ADD and type == form_evo_ops.PROPERTY and \
                            to_field == form_evo_ops.RELATIONSHIP and with_field == form_evo_ops.TYPE:
                        start_neo4j = timer()
                        records, neo4j_query_time = AddFeature.add_relationship_properties(session,
                                                                                           start_node_label_field,
                                                                                           with_feature_text_field,
                                                                                           end_node_label_field,
                                                                                           feature_text_field.split(
                                                                                               ", "),
                                                                                           property_value_field.split(
                                                                                               ", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with key(s) " + feature_text_field + " and value(s) " + \
                              property_value_field + " to " + to_field + " with " \
                              + with_field + " " + with_feature_text_field + " starting at node with label " + \
                              start_node_label_field + " ending at node with label " + end_node_label_field
                        history.append(geo)
                        print("Use function here for add rel property x to relationship with type y")
                        print(records)
                    # ----------------------------------------------------------------------
                    # RENAME
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.RENAME and type == form_evo_ops.LABEL and to_field == form_evo_ops.NODE \
                            and with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = RenameFeature.rename_label(session, with_feature_text_field,
                                                                               rename_to_text_field, database_name)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " " + feature_text_field + " of " + to_field + " with " \
                              + with_field + " " + with_feature_text_field + " to " + rename_to_text_field
                        history.append(geo)
                        print("Rename label from x to y")
                        print(records)

                    elif evo_op == form_evo_ops.RENAME and type == form_evo_ops.TYPE:
                        start_neo4j = timer()
                        records, neo4j_query_time = RenameFeature.rename_type(session, start_node_label_field,
                                                                              end_node_label_field,
                                                                              feature_text_field, rename_to_text_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " " + feature_text_field + " starting at node with label " + \
                              start_node_label_field + " ending at node with label " + end_node_label_field + \
                              " to " + rename_to_text_field
                        history.append(geo)
                        print("Rename label from x to y")
                        print(records)

                    elif evo_op == form_evo_ops.RENAME and type == form_evo_ops.PROPERTY and to_field == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = RenameFeature.rename_node_property(session, with_feature_text_field,
                                                                                       feature_text_field,
                                                                                       rename_to_text_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " key " + feature_text_field + " of " + to_field + " with " \
                              + with_field + " " + with_feature_text_field + " to " + rename_to_text_field
                        history.append(geo)

                    elif evo_op == form_evo_ops.RENAME and type == form_evo_ops.PROPERTY and to_field == form_evo_ops.RELATIONSHIP and \
                            with_field == form_evo_ops.TYPE:
                        start_neo4j = timer()
                        records, neo4j_query_time = RenameFeature.rename_relationship_property(session,
                                                                                               start_node_label_field,
                                                                                               with_feature_text_field,
                                                                                               end_node_label_field,
                                                                                               feature_text_field,
                                                                                               rename_to_text_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " key " + feature_text_field + " of " + to_field + " with " + \
                              with_field + " " + with_feature_text_field + " starting at node with " + start_node_field + \
                              " " + start_node_label_field + " ending at node with " + end_node_field + " " + \
                              end_node_label_field + " to " + rename_to_text_field
                        history.append(geo)
                    # ----------------------------------------------------------------------
                    # DELETE
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL and \
                            copy_with_rels_field == form_evo_ops.WITHOUT_RELATIONSHIPS:
                        start_neo4j = timer()
                        # TODO: add an option if one wants to delete a node with rels. Through Error - Message.
                        # records = DeleteEntityType.delete_node(session, with_feature_text_field)
                        with session.session(database="neo4j") as session:
                            session.run(
                                "MATCH (n:" + with_feature_text_field + ") "
                                                                        "WHERE NOT (n)-[]-() "
                                                                        "CALL { WITH n "
                                                                        "DELETE n "
                                                                        "} IN TRANSACTIONS OF 10000 ROWS;",
                                with_feature_text_field=with_feature_text_field
                            )
                        end_neo4j = timer()
                        neo4j_query_time = " "
                        geo = evo_op + " " + type + " " + feature_text_field + "with " + with_field + " " + \
                              with_feature_text_field + " without relationships"
                        history.append(geo)
                        print("Delete node with label X without rels.")
                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.NODE and \
                            with_field == form_evo_ops.LABEL \
                            and copy_with_rels_field == form_evo_ops.WITH_RELATIONSHIPS:
                        # TODO: add an option if one wants to delete a node with rels. Through Error - Message.
                        # records = DeleteEntityType.delete_node_with_associated_relationships(session,
                        # with_feature_text_field)
                        start_neo4j = timer()
                        with session.session(database="neo4j") as session:
                            session.run(
                                "MATCH (n:" + with_feature_text_field + ")"
                                                                        "CALL { WITH n "
                                                                        "DETACH DELETE n "
                                                                        "} IN TRANSACTIONS OF 10000 ROWS;",
                                with_feature_text_field=with_feature_text_field
                            )
                        neo4j_query_time = " "
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " " + feature_text_field + "with " + with_field + " " + \
                              with_feature_text_field + " with relationships"
                        history.append(geo)
                        print("Delete node with label X with rels.")

                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.RELATIONSHIP and \
                            with_field == form_evo_ops.TYPE:
                        start_neo4j = timer()
                        # TODO: add an option if one wants to delete a node with rels. Through Error - Message.
                        records, neo4j_query_time = DeleteEntityType.delete_relationship(session,
                                                                                         start_node_label_field,
                                                                                         with_feature_text_field,
                                                                                         end_node_label_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + with_field + " " + feature_text_field + \
                              with_feature_text_field + " starting at node with label " + start_node_label_field + " " + \
                              " ending at node with label " + end_node_label_field
                        history.append(geo)
                        print("Delete rel with type X.")

                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.LABEL and \
                            to_field == form_evo_ops.NODE and with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = RemoveFeature.delete_labels(session, with_feature_text_field,
                                                                                feature_text_field.split(", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " " + feature_text_field + " of " + to_field + " with " + \
                              with_field + " " + with_feature_text_field
                        history.append(geo)
                        print("Delete label of node with label x")
                        print(records)

                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.PROPERTY and \
                            to_field == form_evo_ops.NODE and with_field == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = RemoveFeature.delete_node_property_keys(session,
                                                                                            with_feature_text_field,
                                                                                            feature_text_field.split(
                                                                                                ", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " key(s) " + feature_text_field + " of " + to_field + " with " + \
                              with_field + " " + with_feature_text_field
                        history.append(geo)
                        print("Delete property of node with label x")
                        print(records)

                    elif evo_op == form_evo_ops.DELETE and type == form_evo_ops.PROPERTY \
                            and to_field == form_evo_ops.RELATIONSHIP and with_field == form_evo_ops.TYPE:
                        start_neo4j = timer()
                        records, neo4j_query_time = RemoveFeature.delete_relationship_property_keys(session,
                                                                                                    with_feature_text_field,
                                                                                                    feature_text_field.split(
                                                                                                        ", "))
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " key(s) " + feature_text_field + " of " + to_field + " with " + \
                              with_field + " " + with_feature_text_field + " starting at node with " + \
                              start_node_field + " " + start_node_label_field + " ending at node with " + \
                              end_node_field + " " + end_node_label_field
                        history.append(geo)
                        print("Delete property of rel with type x")
                    # ----------------------------------------------------------------------
                    # TRANSFORM
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.TRANSFORM and type == form_evo_ops.NODE:
                        records = TransformEntityType.transform_node_to_relationship(session, start_node_label_field,
                                                                                     with_feature_text_field,
                                                                                     end_node_label_field,
                                                                                     ingoing_rel_field)
                        geo = evo_op + " " + type + " with " + with_feature_text_field + " starting at node with label " + \
                              start_node_label_field + " ending at node with label " + end_node_label_field + \
                              " to relationship with type " + ingoing_rel_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.TRANSFORM and type == form_evo_ops.RELATIONSHIP:
                        records = TransformEntityType.transform_relationship_to_node(session, start_node_label_field,
                                                                                     with_feature_text_field,
                                                                                     end_node_label_field,
                                                                                     with_feature_text_field,
                                                                                     ingoing_rel_field,
                                                                                     outgoing_rel_field)
                        geo = evo_op + " " + type + with_field + " " + with_feature_text_field + \
                              " to node with label " + with_feature_text_field + ", ingoing relationship with type " + \
                              ingoing_rel_field + " and outgoing realationship with type " + outgoing_rel_field
                        history.append(geo)
                    # ----------------------------------------------------------------------
                    # COPY
                    # ----------------------------------------------------------------------
                    # function for copy function
                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.NODE and with_field == form_evo_ops.LABEL:

                        # print(copy_with_rels_field)
                        if copy_with_rels_field:
                            copy_with_rels_field_geo = "with relationships"
                        else:
                            copy_with_rels_field_geo = "without relationships"
                        print(copy_with_rels_field, copy_with_rels_field_geo)
                        start_neo4j = timer()
                        if len(start_node_label_field) == 0:
                            records, neo4j_query_time = CopyEntityType.copy_node_entity(session,
                                                                                        with_feature_text_field,
                                                                                        copy_with_rels_field,
                                                                                        [start_node_label_field])
                        else:
                            records, neo4j_query_time = CopyEntityType.copy_node_entity(session,
                                                                                        with_feature_text_field,
                                                                                        copy_with_rels_field,
                                                                                        start_node_label_field.split(
                                                                                            ", "))

                        if len(start_node_label_field) == 0:
                            start_node_label_field = "None"
                        else:
                            pass
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + with_field + " " + with_feature_text_field + " " + \
                              copy_with_rels_field_geo + " and skip property key(s) " + start_node_label_field
                        history.append(geo)
                        print(records)
                        print("Copy node with label X with/ without rels, skip props Y")

                    # elif evo_op == form_evo_ops.COPY and type == form_evo_ops.NODE \
                    #         and with_field == form_evo_ops.PROPERTY:
                    #     pass
                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = CopyFeature.copy_all_labels(session, feature_text_field,
                                                                                with_feature_text_field)
                        end_neo4j = timer()
                        geo = evo_op + " all " + type + "(s) of node with " + type + " " + \
                              feature_text_field + " to " + to_field + " with " + \
                              with_field + " " + with_feature_text_field
                        history.append(geo)

                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.NODE and to_field == form_evo_ops.NODE:
                        print(start_node_label_field)
                        # records = CopyFeature.copy_all_node_properties_to_node(session, feature_text_field,
                        #                                                        property_key_field,
                        #                                                        property_value_field,
                        #                                                        with_feature_text_field)
                        start_neo4j = timer()
                        records = CopyFeature.copy_all_props_from_node_to_node(session, feature_text_field,
                                                                               with_feature_text_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " all PROPERTIES from " + from_field + " with label " + feature_text_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field

                        history.append(geo)
                        print(records)
                        print("Copy props of node to node")
                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.NODE and to_field == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records = CopyFeature.copy_all_props_from_node_to_rel(session, feature_text_field,
                                                                              start_node_label_field,
                                                                              with_feature_text_field,
                                                                              end_node_label_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " from " + from_field + " with label " + feature_text_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field + \
                              " starting at node with " + start_node_field + " " + start_node_label_field + \
                              " ending at node with " + end_node_field + " " + end_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.RELATIONSHIP and to_field == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records = CopyFeature.copy_all_props_from_rel_to_rel(session,
                                                                             initial_rel_start_node_label_field,
                                                                             feature_text_field,
                                                                             initial_rel_end_node_label_field,
                                                                             start_node_label_field,
                                                                             with_feature_text_field,
                                                                             end_node_label_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " from " + from_field + " with type " + feature_text_field + \
                              " and start node with " + initial_rel_start_node_field + " " + \
                              initial_rel_start_node_label_field + " and end node with " + \
                              initial_rel_end_node_field + initial_rel_end_node_label_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field + \
                              " and start node with " + start_node_field + " " + start_node_label_field + \
                              " and end node with " + end_node_field + " " + end_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.COPY and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.RELATIONSHIP and to_field == form_evo_ops.NODE:
                        start_neo4j = timer()
                        records = CopyFeature.copy_all_props_from_rel_to_node(session,
                                                                              initial_rel_start_node_label_field,
                                                                              feature_text_field,
                                                                              initial_rel_end_node_label_field,
                                                                              with_feature_text_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " from " + from_field + " with type " + feature_text_field + \
                              " starting at node with " + initial_rel_start_node_field + " " + \
                              initial_rel_start_node_label_field + " ending node with " + \
                              initial_rel_end_node_field + " " + initial_rel_end_node_label_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field
                        history.append(geo)
                    # ----------------------------------------------------------------------
                    # MOVE
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.NODE:
                        start_neo4j = timer()
                        records, neo4j_query_time = MoveEntityType.move_subgraph(session,
                                                                                 initial_rel_start_node_label_field,
                                                                                 with_feature_text_field,
                                                                                 start_node_label_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + with_field + " " + with_feature_text_field + " from start node with label " + \
                              initial_rel_start_node_label_field + \
                              " to new start node with label " + start_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records, neo4j_query_time = MoveEntityType.move_relationship(session,
                                                                                     initial_rel_start_node_label_field,
                                                                                     with_feature_text_field,
                                                                                     initial_rel_end_node_label_field,
                                                                                     start_node_label_field,
                                                                                     end_node_label_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + with_field + " " + with_feature_text_field + " starting at node with label " + \
                              initial_rel_start_node_label_field + " ending at node with label " + initial_rel_end_node_label_field + \
                              " to new start node with label " + start_node_label_field + " ending at node with label " + \
                              end_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.LABEL:
                        start_neo4j = timer()
                        records, neo4j_query_time = MoveFeature.move_selected_labels(session,
                                                                                     feature_text_field.split(", ")[0],
                                                                                     list(feature_text_field.split(
                                                                                         ", ")),
                                                                                     with_feature_text_field)
                        end_neo4j = timer()
                        print(f'Labels to Move {list(feature_text_field)}')
                        geo = evo_op + " " + type + " " + feature_text_field + " of node with label " + \
                              feature_text_field + \
                              " to node with label " + with_feature_text_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.NODE and to_field == form_evo_ops.NODE:
                        start_neo4j = timer()
                        records = MoveFeature.move_all_props_from_node_to_node(session, feature_text_field,
                                                                               with_feature_text_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " all PROPERTIES from " + from_field + " with label " + feature_text_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.NODE and to_field == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records = MoveFeature.move_all_props_from_node_to_rel(session, feature_text_field,
                                                                              start_node_label_field,
                                                                              with_feature_text_field,
                                                                              end_node_label_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " all properties from " + from_field + " with label " + feature_text_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field + \
                              " starting at node with " + start_node_field + " " + start_node_label_field + \
                              " ending at node with " + end_node_field + " " + end_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.RELATIONSHIP and to_field == form_evo_ops.NODE:
                        start_neo4j = timer()
                        records = MoveFeature.move_all_props_from_rel_to_node(session,
                                                                              initial_rel_start_node_label_field,
                                                                              feature_text_field,
                                                                              initial_rel_end_node_label_field,
                                                                              with_feature_text_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " all properties from " + from_field + " with type " + feature_text_field + \
                              " starting at node with " + initial_rel_start_node_field + " " + \
                              initial_rel_start_node_label_field + " ending node with " + \
                              initial_rel_end_node_field + " " + initial_rel_end_node_label_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.PROPERTY \
                            and from_field == form_evo_ops.RELATIONSHIP and to_field == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records = MoveFeature.move_all_props_from_rel_to_rel(session,
                                                                             initial_rel_start_node_label_field,
                                                                             feature_text_field,
                                                                             initial_rel_end_node_label_field,
                                                                             start_node_label_field,
                                                                             with_feature_text_field,
                                                                             end_node_label_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " from " + from_field + " with type " + feature_text_field + \
                              " and start node with " + initial_rel_start_node_field + " " + \
                              initial_rel_start_node_label_field + " and end node with " + \
                              initial_rel_end_node_field + initial_rel_end_node_label_field + \
                              " to " + to_field + " with " + with_field + " " + with_feature_text_field + \
                              " and start node with " + start_node_field + " " + start_node_label_field + \
                              " and end node with " + end_node_field + " " + end_node_label_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.MOVE and type == form_evo_ops.DIRECTION:
                        start_neo4j = timer()
                        records, neo4j_query_time = MoveFeature.move_direction(session, start_node_label_field,
                                                                               with_feature_text_field,
                                                                               end_node_label_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " of relationship with type " + with_feature_text_field + \
                              " from start node with label " + start_node_label_field + " to end node with label " + \
                              end_node_label_field
                        history.append(geo)
                    # ----------------------------------------------------------------------
                    # SPLIT
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.SPLIT and type == form_evo_ops.NODE:
                        print(with_feature_text_field, split_at_field)
                        start_neo4j = timer()
                        records, neo4j_query_time = SplitEntityType.split_node(session, with_feature_text_field,
                                                                               split_at_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + " with " + with_field + " " + with_feature_text_field + \
                              " at property key " + split_at_field
                        history.append(geo)
                    elif evo_op == form_evo_ops.SPLIT and type == form_evo_ops.RELATIONSHIP:
                        start_neo4j = timer()
                        records, neo4j_query_time = SplitEntityType.split_relationship(session, with_feature_text_field,
                                                                                       start_node_label_field,
                                                                                       end_node_label_field,
                                                                                       split_at_field)
                        end_neo4j = timer()
                        geo = evo_op + " " + type + with_field + " " + with_feature_text_field + \
                              " starting at node with label " + start_node_label_field + \
                              " ending at node with label " + end_node_label_field + " at property key " + \
                              split_at_field
                        history.append(geo)
                    # ----------------------------------------------------------------------
                    # MERGE
                    # ----------------------------------------------------------------------
                    elif evo_op == form_evo_ops.MERGE and join_options == form_evo_ops.FULL_OUTER_INCLUSIVE \
                            and type == form_evo_ops.NODE:
                        start_neo4j = timer()
                        records = MergeEntityTypes.full_outer_inclusive_merge_of_nodes(session, with_feature_text_field,
                                                                                       start_node_label_field)
                        # ToDo: add neo4j_query_time
                        end_neo4j = timer()
                        geo = evo_op + " all properties of " + type + " with " + with_field + " " + \
                              with_feature_text_field + " and node with label " + \
                              start_node_label_field
                        history.append(geo)

                records = uri
                # session.close()

                # wirte all geo to txt file
                # ToDo: make strings of dropdown menus toLower()
                with open('geo.txt', 'a') as f:
                    f.write('\n'.join(history))
                    # used so that new line will be used if file is not empty when append is triggered
                    f.write('\n----------------------------------------------------------')
                    f.write('\n')

                with open('geo.txt', 'r') as fr:
                    whole_geo = fr.readlines()
                    # fr.close()

                formset_evo_ops = EvoOpsFormSet()

                start_schema_info_timer = timer()
                start_schema_after_evo_timer = timer()
                keys, schema_entity_types, schema_nbr_of_entity_types, schema_prop_keys, schema_relationships, data = get_schema_data(
                    uri, user, password, database_name)
                json_data = data

                with open('latest_schema.txt', 'w') as convert_file:
                    convert_file.write(json.dumps(json_data))
                end_schema_after_evo_timer = timer()

                start_schema_chart_timer = timer()
                # ToDo: use json_schema data and do not call get_schema again!!!

                # node_labels, node_schema_prop_keys, node_schema_relationships, rel_schema_node_key, rel_types, \
                #     rel_schema_prop_keys, rel_schema_direction, rel_schema_associated_labels, \
                #     data = get_schema_for_db_schema_table(uri, user, password)
                node_labels, node_schema_prop_keys, node_schema_relationships, rel_schema_node_key, rel_types, \
                    rel_schema_prop_keys, rel_schema_direction, rel_schema_associated_labels, \
                    data = get_schema_for_db_schema_table(json_data)
                end_schema_chart_timer = timer()

                start_schema_table_timer = timer()
                zipped_segments_nodes = zip(node_labels, node_schema_prop_keys, node_schema_relationships)
                zipped_segments_rels = zip(rel_schema_node_key, rel_types, rel_schema_prop_keys, rel_schema_direction,
                                           rel_schema_associated_labels)
                end_schema_table_timer = timer()
                end_schema_info_timer = timer()

                # https://www.geeksforgeeks.org/how-to-read-dictionary-from-file-in-python/
                # reading the data from the file (called current_schema)
                with open('current_schema.txt') as json_file:
                    data = json_file.read()

                result_add, result_rename, result_delete, result_transform, result_copy, result_move, result_split, \
                    result_merge = datasets_for_evo_ops_over_time()
                print(f'resutl array rename B {result_rename}')

                print(f'Data given to compare_dicts {data}')
                current_schema_json_data, compared_json_data, dict1_initial_schema, dict2_new_schema = \
                    compare_dicts_for_diagram(data, json_data)

                print(f'result array rename C {result_rename}')
                end_submit_button = timer()
                variables_time = timedelta(seconds=end_form_variables - start_form_variables)
                connection_time = timedelta(seconds=end_db_connection - start_db_connection)
                neo4j_execution_time = timedelta(seconds=end_neo4j - start_neo4j)
                schema_info_time = timedelta(seconds=end_schema_info_timer - start_schema_info_timer)
                schema_chart_time = timedelta(seconds=end_schema_chart_timer - start_schema_chart_timer)
                schema_table_time = timedelta(seconds=end_schema_table_timer - start_schema_table_timer)
                schema_after_evo_op_time = timedelta(seconds=end_schema_after_evo_timer - start_schema_after_evo_timer)
                total_time_taken = timedelta(seconds=end_submit_button - start_submitt_button_pressed)
                print(f'Connecting time: {connection_time}')
                print(f'Neo4j query time: {neo4j_query_time}ms')
                print(f'Neo4j execution time: {neo4j_execution_time}')
                print(f'Total time taken: {total_time_taken}')
                with open('timestemps.txt', 'a') as f:
                    f.write('\n'.join(history) + '\n')
                    f.write('Get variables: ' + str(variables_time) + '\n')
                    f.write('Connection time: ' + str(connection_time) + '\n')
                    f.write('Get schema info time: ' + str(schema_info_time) + ": schema after evo op - " +
                            str(schema_after_evo_op_time) + ", table: " + str(schema_table_time) + ", diagram: " + str(
                        schema_chart_time) + '\n')
                    f.write('Neo4j query time: ' + str(neo4j_query_time) + '\n')
                    # f.write('Neo4j models.py time: ' + str(query_time) + '\n')
                    f.write('Neo4j execution time: ' + str(neo4j_execution_time) + '\n')
                    f.write('Total execution time: ' + str(total_time_taken))
                    # used so that new line will be used if file is not empty when append is triggered
                    f.write('\n----------------------------------------------------------')
                    f.write('\n')

                return render(request, "nautilus.html",
                              {"form_db_connection": form_db_connection, "form_evo_ops": form_evo_ops,
                               "formset_evo_ops": formset_evo_ops, 'helper': helper,
                               'history': history, 'whole_geo': whole_geo,
                               'zipped_segments_nodes': zipped_segments_nodes,
                               'zipped_segments_rels': zipped_segments_rels,
                               "json_data": json_data,
                               'compared_json_data': compared_json_data,
                               "dict1_initial_schema": dict1_initial_schema, "dict2_new_schema": dict2_new_schema,
                               "result_add": result_add, "result_rename": result_rename,
                               "result_delete": result_delete,
                               "result_transform": result_transform, "result_copy": result_copy,
                               "result_move": result_move, "result_split": result_split, "result_merge": result_merge
                               })

        # handles what to do if current schema button is pressed
        if 'current-schema-button' in request.POST:
            # check whether it's valid:
            start_current_schema_button = timer()
            if form_db_connection.is_valid():

                uri = form_db_connection.cleaned_data.get("uri")
                user = form_db_connection.cleaned_data.get("user")
                password = form_db_connection.cleaned_data.get("password")
                database_name = form_db_connection.cleaned_data.get("database")
                save_connection = form_db_connection.cleaned_data.get("save_connection")

                if save_connection is False:
                    form_db_connection = DbConnectionForm()
                else:
                    pass

                keys, schema_entity_types, schema_nbr_of_entity_types, schema_prop_keys, schema_relationships, data = get_schema_data(
                    uri, user, password, database_name)
                current_schema_json_data = {key: value for key, value in sorted(data.items())}
                # ToDo: attention: this contains rels and node schema!!!
                #  while dict1 only contains the schema of nodes!!!!
                dict1_initial_schema = current_schema_json_data

                # writes data of current schema to file named current_schema.txt
                with open('current_schema.txt', 'w') as convert_file:
                    convert_file.write(json.dumps(current_schema_json_data))


                # ------------------------------------------------------------------------------
                # ------------------------------------------------------------------------------
                # HIER WEITERMACHEN
                # ------------------------------------------------------------------------------
                # ------------------------------------------------------------------------------
                # ToDo: add compared option if initial schema button is pressed later on
                # basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # try:
                #     # get the size of file
                #     file_size = os.path.getsize(basedir + '/' + 'latest_schema.txt')
                #
                #     # if file size is 0, it is empty
                #     if file_size == 0:
                #         print("File is empty")
                #         pass
                #     else:
                #         with open('current_schema.txt') as json_file:
                #             data = json_file.read()
                #
                #         with open('latest_schema.txt') as json_file:
                #             json_data = json_file.read()
                #
                #         print(f' data given to compare_dicts {data}')
                #         print(f' json_data given to compare_dicts {isinstance(json_data, (str, dict))}, {isinstance(data, (str))}')
                #         current_schema_json_data, compared_json_data, dict1_initial_schema, dict2_new_schema = \
                #             compare_dicts_for_diagram(data, json_data)
                #
                # # if file does not exist, then exception occurs
                # except FileNotFoundError as e:
                #     print("File NOT found")

                # if json_data.keys() > 0:
                #     current_schema_json_data, compared_json_data, dict1_initial_schema, dict2_new_schema = \
                #         compare_dicts_for_diagram(data, json_data)
                end_current_schema_button = timer()
                return render(request, "nautilus.html", {"form_db_connection": form_db_connection,
                                                         "form_evo_ops": form_evo_ops,
                                                         "formset_evo_ops": formset_evo_ops,
                                                         'current_schema_json_data': current_schema_json_data,
                                                         'dict1_initial_schema': dict1_initial_schema
                                                         # 'current_schema_zipped_segments': current_schema_zipped_segments
                                                         })
                # return JsonResponse(current_schema_json_data)
        else:
            print(form_evo_ops.errors.as_json())

            # return render(request, "nautilus.html", {'errors': form_evo_ops.errors.as_json()})




    # if a GET (or any other method) we'll create a blank form
    else:
        form_db_connection = DbConnectionForm()
        form_evo_ops = EvoOpsForm()
        formset_evo_ops = EvoOpsFormSet()
        helper = ExampleFormSetHelper()

    return render(request, "nautilus.html", {"form_db_connection": form_db_connection, "form_evo_ops": form_evo_ops,
                                             "formset_evo_ops": formset_evo_ops, 'helper': helper,
                                             })


def get_schema_data(uri, user, password, database_name):
    # get all schema information after evolution operations have been executed
    schema_class = Schema(uri, user, password)
    data = schema_class.return_schema(database_name)
    keys = list(data.keys())

    schema_entity_types = []
    schema_prop_keys = []
    schema_nbr_of_entity_types = []
    schema_relationships = []
    node_dictionary = {}
    relationship_dictionary = {}

    for item, element in data.items():

        for i in element:

            match i:
                case "type":
                    schema_entity_types.append(element[i])
                    match element[i]:
                        case "node":
                            node_dictionary[item] = element
                        case "relationship":
                            relationship_dictionary[item] = element
                case "properties":
                    schema_prop_keys.append(list(element[i].keys()))
                    for j in element[i]:
                        match j:
                            case "type":
                                pass
                case "count":
                    schema_nbr_of_entity_types.append(element[i])
                case "relationships":
                    schema_relationships.append(list(element[i].keys()))
                    for j in element[i]:
                        for h in element[i][j]:
                            match h:
                                case "count":
                                    pass
                                case "direction":
                                    pass
                                case "properties":
                                    pass

    return keys, schema_entity_types, schema_nbr_of_entity_types, schema_prop_keys, schema_relationships, data


def get_schema_for_db_schema_table(data):
    keys = list(data.keys())
    print(f' Keys: {keys}')
    schema_labels_and_types = []
    node_schema_prop_keys = []
    node_schema_relationships = []
    node_dictionary = {}

    rel_schema_node_key = []
    rel_schema_type = []
    rel_schema_prop_keys = []
    rel_schema_direction = []
    rel_schema_associated_labels = []
    relationship_dictionary = {}

    for item, element in data.items():

        for i in element:

            match i:
                case "type":
                    match element[i]:
                        case "node":
                            node_dictionary[item] = element
                        case "relationship":
                            relationship_dictionary[item] = element

    print(f'Node dict: {node_dictionary}')
    print(f'Rel dict: {relationship_dictionary}')

    for item, element in node_dictionary.items():
        print(f'{item}')
        schema_labels_and_types.append(item)
        for i in element:

            match i:
                case "properties":
                    node_schema_prop_keys.append(list(element[i].keys()))
                    for j in element[i]:
                        match j:
                            case "type":
                                pass
                case "relationships":
                    node_schema_relationships.append(list(element[i].keys()))

                    for j in element[i]:
                        schema_labels_and_types.append(j)
                        rel_schema_node_key.append(item)
                        rel_schema_type.append(j)
                        for h in element[i][j]:
                            match h:
                                case "count":
                                    pass
                                case "direction":
                                    if type(element[i][j][h]) == str:
                                        rel_schema_direction.append(element[i][j][h])
                                    else:
                                        pass
                                case "labels":
                                    if type(element[i][j][h]) == str or type(element[i][j][h]) == list:
                                        rel_schema_associated_labels.append(element[i][j][h])
                                    else:
                                        pass
                                case "properties":

                                    rel_schema_prop_keys.append(list(element[i][j][h].keys()))


    print(f'Node dict property keys: {node_schema_prop_keys}')
    print(f'Node dict rels: {node_schema_relationships}')

    print(f'Rels direction: {rel_schema_direction}')
    print(f'Rels assoc. labels: {rel_schema_associated_labels}')
    print(f'Rels prop keys: {rel_schema_prop_keys}')
    print(f'Labels and Types: {schema_labels_and_types}')

    return node_dictionary.keys(), node_schema_prop_keys, node_schema_relationships, rel_schema_node_key, rel_schema_type, \
        rel_schema_prop_keys, rel_schema_direction, rel_schema_associated_labels, data


def find_dict_differences(array, dict1, dict2):
    added_items = []
    removed_items = []
    labels_add_entity_type = []
    labels_remove_entity_type = []
    labels_add_feature = []
    labels_remove_feature = []

    for element in array:
        match element[0]:
            case "add":
                differentiate_between_feature_and_entity_type(element, added_items, labels_add_entity_type,
                                                              labels_add_feature)
            case "remove":
                differentiate_between_feature_and_entity_type(element, removed_items, labels_remove_entity_type,
                                                              labels_remove_feature)

    update_and_compare_dictionaries(labels_add_entity_type, dict1, dict2, added_items)
    update_and_compare_dictionaries(labels_remove_entity_type, dict1, dict2, removed_items)
    sorted_dict1 = {key: value for key, value in sorted(dict1.items())}
    sorted_dict2 = {key: value for key, value in sorted(dict2.items())}

    return sorted_dict1, sorted_dict2


def differentiate_between_feature_and_entity_type(element, entity_type_items, entity_type_labels, feature_labels):
    if len(element[1]) == 0:
        print(f'Remove entity type: {element[1]}')
        for item in element[2]:
            item[1]["count"] = 0
            entity_type_items.append([item[0], item[1]])
            entity_type_labels.append(item[0])
    else:
        label = element[1].split(".")
        feature_labels.append(label[0])
        match element[1].split(".")[1]:
            case "properties":
                for i in element[2]:
                    print(f'Removed property key(s): {i[0]}')
            case "relationships":
                print(f'Relationship removed: {element[2]}')


def compare_dicts_for_diagram(data, json_data):
    try:
        current_schema_json_data = json.loads(data)
        compared_json_data = list(dictdiffer.diff(current_schema_json_data, json_data))
        dict1_initial_schema, dict2_new_schema = find_dict_differences(compared_json_data,
                                                                       current_schema_json_data, json_data)
        print(f'Dict1: {dict1_initial_schema}')
        print(f'Dict2: {dict2_new_schema}')
    except JSONDecodeError:
        current_schema_json_data = {}
        compared_json_data = []
        dict1_initial_schema = {}
        dict2_new_schema = json_data
    return current_schema_json_data, compared_json_data, dict1_initial_schema, dict2_new_schema


def update_and_compare_dictionaries(array, dict1, dict2, added_items):
    for element in array:
        if element not in dict1.keys():
            dict1.update(added_items)
        elif element not in dict2.keys():
            dict2.update(added_items)
    return dict1, dict2


def datasets_for_evo_ops_over_time():
    # Using readlines() to generate output for whole history of geo
    file1 = open('geo.txt', 'r')
    geo_lines = file1.readlines()

    result_array = [[]]
    # Strips the newline character
    for line in geo_lines:
        block_end = '----------------------------------------------------------'

        if block_end not in line:
            result_array[len(result_array) - 1].append(line.strip().split(" ")[0])
        else:
            result_array.append([])

    print(f'Result array B {result_array}')

    # count evo ops for each array in result_array
    result_add = []
    result_rename = []
    result_delete = []
    result_transform = []
    result_copy = []
    result_move = []
    result_split = []
    result_merge = []

    for item in result_array:
        # set all counter to 0 for each item in result_array
        # aim: count evo ops per block/ transaction
        count_add = 0
        count_rename = 0
        count_delete = 0
        count_transform = 0
        count_copy = 0
        count_move = 0
        count_split = 0
        count_merge = 0

        for evo_op in item:
            match evo_op:
                case "ADD":
                    count_add += 1
                case "RENAME":
                    count_rename += 1
                case "DELETE":
                    count_delete += 1
                case "TRANSFORM":
                    count_transform += 1
                case "COPY":
                    count_copy += 1
                case "MOVE":
                    count_move += 1
                case "SPLIT":
                    count_split += 1
                case "MERGE":
                    count_merge += 1

        # add the count for each item to the list for each evolution operation
        result_add.append(count_add)
        result_rename.append(count_rename)
        result_delete.append(count_delete)
        result_transform.append(count_transform)
        result_copy.append(count_copy)
        result_move.append(count_move)
        result_split.append(count_split)
        result_merge.append(count_merge)
    print(f'result array rename {result_rename}')

    return result_add, result_rename, result_delete, result_transform, result_copy, result_move, result_split, \
        result_merge


# see video: https://www.youtube.com/watch?v=y7eDZMSPN-8
def download_history(request):
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'geo.txt'
    filepath = basedir + '/' + filename
    history_file = filepath
    filename = os.path.basename(history_file)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(history_file, 'rb'), chunk_size),
                                     content_type=mimetypes.guess_type(history_file)[0])
    response['Content-Length'] = os.path.getsize(history_file)
    response['Content-Disposition'] = "Attachment;filename=%s" % filename
    return response


def delete_history(request):
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'geo.txt'
    filepath = basedir + '/' + filename
    history_file = filepath
    filename = os.path.basename(history_file)

    open(filename, 'w').close()

    messages.info(request, 'Your history was deleted!')
    return HttpResponseRedirect('/elaine2/')


def documentation(request):
    return render(request, 'documentation.html')
