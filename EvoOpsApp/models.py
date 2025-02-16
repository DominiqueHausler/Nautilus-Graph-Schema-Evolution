'''
Here all models are defined, refering to the Cypher code. We use Neo4j Desktop to execute queries on a graph database.
All Cypher statements to perform evolution directly on the graph database are defined here. Additionally, the function
to connect to the database is defined in this file.
'''

import neo4j
from iteration_utilities import deepflatten
from django_neomodel import DjangoNode
from neo4j import GraphDatabase
from neomodel import StringProperty, UniqueIdProperty, IntegerProperty
from timeit import default_timer as timer
from datetime import timedelta


class User(DjangoNode):
    uuid = UniqueIdProperty(primary_key=True)
    title = StringProperty()
    released = IntegerProperty()

    class Meta:
        app_label = 'movies'


class Connection(object):

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()



class Schema(Connection):
    def __init__(self, uri, user, password):
        super().__init__(uri, user, password)
        # with self.driver.session() as session:
        #     # result = session.execute_read(_checking_for_apoc)
        #     schema = session.execute_read(_get_schema)
        #     # print(result)
        #     print(f'Schema: {schema}')

    def return_schema(self, database_name):
        with self.driver.session(database=database_name) as session:
        #with self.driver.session(database=database_name) as session:
            # result = session.execute_read(_checking_for_apoc)
            schema = session.execute_read(_get_schema)
            # print(result)
            print(f'Schema: {schema}')
            return schema

    def return_detailed_schema(self):
        with self.driver.session() as session:
            # result = session.execute_read(_checking_for_apoc)
            schema = session.execute_read(_get_detailed_schema)
            # print(result)
            print(f'Detailed schema: {schema}')
            return schema

    # def _checking_for_apoc(tx):
    #     # result = tx.run("RETURN apoc.version()")
    #     try:
    #         version_number = tx.run("RETURN apoc.version()")
    #         print("You are using version " + version_number.single()[0] + " of the APOC library.")
    #     except CypherSyntaxError:
    #         print("No APOC library found. Please install the APOC library for your database.")
    #     except TransactionError:
    #         print("No APOC library found.")


def _get_schema(tx):
    schema_data = tx.run("CALL apoc.meta.schema()").single()[0]
    print(schema_data)
    return schema_data


def _get_detailed_schema(tx):
    detailed_schema_data = tx.run(
        """
        CALL apoc.meta.schema() yield value
        UNWIND apoc.map.sortedProperties(value) as labelData
        WITH labelData[0] as label, labelData[1] as data
        UNWIND apoc.map.sortedProperties(data.properties) as property
        RETURN label, data.type, data.count as numberOfEntites, property[0] as property, property[1].type as type
        """).single()[0]
    print(detailed_schema_data)
    return detailed_schema_data


class AddNodeEntity(DjangoNode):

    def create_new_node_with_label_and_key(summary, label, key, value):
        start_neo4j_query = timer()
        records, summary, keys = summary.execute_query(
            "CREATE (a:" + label + ") "
                                   "SET a." + key + " = $property "
                                                    "RETURN a.message + ', from node ' + id(a) + ' with label(s) ' + labels(a) AS label",
            label=label, key=key, property=value,
        )
        end_neo4j_query = timer()
        # print summary of the results from the query
        result_print = "The query `{query}` returned {records_count} records in {time} ms. {nodes_created} node(s) " \
                       "with {labels} label(s) and {properties_set} properties added. {relationships_created} " \
                       "relationships added.".format(query=summary.query, records_count=len(records),
                                                     nodes_created=summary.counters.nodes_created,
                                                     labels=summary.counters.labels_added,
                                                     properties_set=summary.counters.properties_set,
                                                     relationships_created=summary.counters.relationships_created,
                                                     time=summary.result_available_after
                                                     )
        print(result_print)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return result_print, neo4j_query_time

    def create_new_node_with_label_x(summary, label, database_name):
        start_query = timer()
        records, summary, keys = summary.execute_query(
            "CREATE (a:" + label + ") "
                                   "RETURN a.message + ', from node ' + id(a) + ' with label(s) ' + labels(a) AS label",
            label=label, database_=database_name,
        )

        # print summary of the results from the query
        result_print = "The query `{query}` returned {records_count} records in {time} ms. {nodes_created} node(s) " \
                       "with {labels} label(s) added. ".format(query=summary.query, records_count=len(records),
                                                               nodes_created=summary.counters.nodes_created,
                                                               labels=summary.counters.labels_added,
                                                               properties_set=summary.counters.properties_set,
                                                               relationships_created=summary.counters.relationships_created,
                                                               time=summary.result_available_after
                                                               )
        print(result_print)

        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        print(f'Neo4j query time: {neo4j_query_time} ms')
        end_query = timer()
        query_time = timedelta(seconds=end_query - start_query)
        return records, neo4j_query_time, query_time


class AddRelEntity(DjangoNode):
    def create_rels_with_type_x(session, rel_type, start_node_label, end_node_label):
        records, summary, keys = session.execute_query(
            """
            MATCH (s:""" + start_node_label + """) 
            OPTIONAL MATCH (e:""" + end_node_label + """) 
            MERGE (s)-[:""" + rel_type + """]->(e)
            RETURN s, e
            """,
            rel_type=rel_type, start_node_label=start_node_label, end_node_label=end_node_label,
        )

        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time


class AddFeature(DjangoNode):
    # add operations for features

    # add one or more labels with overwrite semantics
    # old_label: string
    # list_of_new_labels: array
    # TODO: filter for node property as well???
    def add_labels_with_overwrite_semantics(summary, old_label, list_of_new_labels):
        records, summary, keys = summary.execute_query(
            "WITH $old_label AS old_label "
            "MATCH (a) "
            "WHERE apoc.label.exists(a, $old_label) "
            "CALL apoc.create.setLabels(a, $list_of_new_labels) "
            "YIELD node "
            "RETURN node ",
            old_label=old_label, list_of_new_labels=list_of_new_labels
        )
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} " \
                              "ms.".format(query=summary.query, records_count=len(records),
                                           time=summary.result_available_after)
        print(print_query_results)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time

    # add one or more labels with ignore semantics
    # old_label: string
    # list_of_new_labels: array
    # TODO: filter for node property as well???
    def add_labels_with_ignore_semantics(tx, old_label, list_of_new_labels):
        records, summary, keys = tx.execute_query(
            "WITH $old_label AS old_label "
            "MATCH (a) "
            "WHERE apoc.label.exists(a, $old_label) "
            "CALL apoc.create.addLabels(a, $list_of_new_labels) "
            "YIELD node "
            "RETURN node",
            old_label=old_label, list_of_new_labels=list_of_new_labels
        )
        # print summary of the results from the query
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} " \
                              "ms.".format(query=summary.query, records_count=len(records),
                                           time=summary.result_available_after)
        print(print_query_results)
        print_added_labels = "The label(s) " + str(list_of_new_labels) + " were added."
        print(print_added_labels)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # add type to relationship with overwrite semantics
    # label: string of node label relationship is attached to (undirected search for rel)
    # old_type: string
    # new_type: string
    def add_type_with_overwrite_semantics(tx, label, old_type, new_type):
        records, summary, keys = tx.execute_query(
            # TODO: make direction definable?
            "MATCH (n:" + label + ")-[rel:" + old_type + "]-() "
                                                         "CALL apoc.refactor.setType(rel, $new_type) "
                                                         "YIELD input, output "
                                                         "RETURN input, output ",
            label=label, old_type=old_type, new_type=new_type
        )

        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} " \
                              "ms.".format(query=summary.query, records_count=len(records),
                                           time=summary.result_available_after)
        print(print_query_results)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # add 1 to n properties to relationship with overwrite semantic
    # node_label: string
    # rel_type: string
    # list_of_new_keys: array
    # list_of_new_values: array
    def add_relationship_properties(summary, node_label, rel_type, end_node_label, list_of_new_keys,
                                    list_of_new_values):
        records, summary, keys = summary.execute_query(
            "MATCH(n:" + node_label + ")-[r:" + rel_type + "]-(n2:" + end_node_label + ") "
                                                                                       "CALL apoc.create.setRelProperties(r, $list_of_new_keys, $list_of_new_values) "
                                                                                       "YIELD rel "
                                                                                       "RETURN rel; ",
            node_label=node_label, rel_type=rel_type, end_node_label=end_node_label, list_of_new_keys=list_of_new_keys,
            list_of_new_values=list_of_new_values
        )

        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} " \
                              "ms.".format(query=summary.query, records_count=len(records),
                                           time=summary.result_available_after)
        print(print_query_results)

        print_added_relationship_properties = "The keys " + str(list_of_new_keys) + " and the values " + \
                                              str(list_of_new_values) + " were added to the relationships of type " \
                                              + rel_type + "."
        print(print_added_relationship_properties)

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # add 1 to n properties to relationship with overwrite semantic
    # node_label: string
    # list_of_new_keys: array
    # list_of_new_values: array
    def add_node_properties(summary, node_label, list_of_new_keys, list_of_new_values):
        records, summary, keys = summary.execute_query(
            "MATCH(n:" + node_label + ") "
                                      "CALL apoc.create.setProperties(n, $list_of_new_keys, $list_of_new_values) "
                                      "YIELD node "
                                      "RETURN node; ",
            node_label=node_label, list_of_new_keys=list_of_new_keys, list_of_new_values=list_of_new_values
        )

        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} " \
                              "ms.".format(query=summary.query, records_count=len(records),
                                           time=summary.result_available_after)
        print(print_query_results)
        print_added_node_properties = "The keys " + str(list_of_new_keys) + " and the values " + \
                                      str(list_of_new_values) + " were added to nodes labeled " + node_label + "."
        print(print_added_node_properties)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


class RenameFeature(DjangoNode):
    # renames the type of relationship
    # old_label: string
    # new_label: string
    def rename_label(tx, old_label, new_label, database_name):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + old_label + ") "
                                      "WITH collect(n) AS nodes "
                                      "CALL apoc.refactor.rename.label($old_label, $new_label, nodes) "
                                      "YIELD batches, total, timeTaken, committedOperations "
                                      "RETURN batches, total, timeTaken, committedOperations; ",
            old_label=old_label, new_label=new_label, database_=database_name,
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_renamed_labels = "The label " + old_label + " was renamed to " + new_label + "."
            print(print_renamed_labels)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')
        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # renames the type of relationship
    # node_label: string
    # old_type: string of the relationship to be renamed
    # new_type: string
    def rename_type(tx, node_label, end_node_label, old_type, new_type):
        records, summary, keys = tx.execute_query(
            "MATCH (n: " + node_label + ")-[rel:" + old_type + "]->(n2:" + end_node_label + ") "
                                                                                            "WITH collect(rel) AS rels "
                                                                                            "CALL apoc.refactor.rename.type($old_type, $new_type, rels)"
                                                                                            "YIELD batches, total, timeTaken, committedOperations "
                                                                                            "RETURN batches, total, timeTaken, committedOperations; ",
            node_label=node_label, old_type=old_type, end_node_label=end_node_label, new_type=new_type
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_renamed_type = "The type " + old_type + " was renamed to " + new_type + "."
            print(print_renamed_type)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # renames a property key from a node
    # node_label: string
    # old_key: string
    # new_key: string
    def rename_node_property(tx, node_label, old_key, new_key):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + node_label + ") "
                                       "WITH collect(n) AS nodes "
                                       "CALL apoc.refactor.rename.nodeProperty($old_key, $new_key, nodes)"
                                       "YIELD batches, total, timeTaken, committedOperations "
                                       "RETURN batches, total, timeTaken, committedOperations; ",
            node_label=node_label, old_key=old_key, new_key=new_key
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_renamed_property = "The property key " + old_key + " was renamed to " + new_key + "."
            print(print_renamed_property)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # renames a property key from a relationship
    # node_label: string
    # rel_type: string
    # old_key: string
    # new_key: string
    def rename_relationship_property(tx, start_node_label, rel_type, end_node_label, old_key, new_key):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + start_node_label + ")-[rel:" + rel_type + "]-(n2:" + end_node_label + ") "
                                                                                                "WITH collect(rel) AS rels "
                                                                                                "CALL apoc.refactor.rename.typeProperty($old_key, $new_key, rels) "
                                                                                                "YIELD batches, total, timeTaken, committedOperations "
                                                                                                "RETURN batches, total, timeTaken, committedOperations; ",
            start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label, old_key=old_key,
            new_key=new_key
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The property key " + old_key + " was renamed to " + new_key + "."
            print(print_query_results)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


def _large_delete(tx, node_label):
    tx.run(
        # # ":auto "
        ":auto MATCH (n:" + node_label + ")"
                                         "CALL { WITH n "
                                         "DETACH DELETE n "
                                         "} IN TRANSACTIONS OF 10000 ROWS;",
        # """
        # :auto
        # MATCH (n:""" + node_label + """)
        # CALL apoc.periodic.iterate(
        #     'MATCH (n:""" + node_label + """) return id(n) as id',
        #     'MATCH (n) WHERE id(n) = id DELETE n',
        #     {batchSize:10000})
        # YIELD batches, total
        # RETURN batches, total
        # """,
        # "MATCH (n:" + node_label + ") "
        #                            "DELETE n ",
        node_label=node_label
    )


class DeleteEntityType(DjangoNode):
    # deletes a node
    # node_label: string
    def delete_node(tx, node_label):
        result = tx.execute_query(_large_delete, node_label)
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query

        return result

    # deletes a node including its relationships
    # node_label: string
    def delete_node_with_associated_relationships(tx, node_label):
        records, summary, keys = tx.execute_query(
            """
            :auto
            MATCH (n:""" + node_label + """)
            CALL { WITH n
            DETACH DELETE n
            } IN TRANSACTIONS OF 10000 ROWS;
            """,
            node_label=node_label
        )

        # print summary of the results from the query
        if len(records) == 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_delete_node = "Nodes labeled " + node_label + " were deleted."
            print(print_delete_node)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        return records, summary, node_label

    # delete relationship
    # node_label: string
    # rel_type: string
    def delete_relationship(tx, start_node_label, rel_type, end_node_label):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + start_node_label + ")-[rel:" + rel_type + "]-(n2:" + end_node_label + ") "
                                                                                                "DELETE rel ",
            start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label,
        )

        # print summary of the results from the query
        if len(records) == 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_delete_relationship = "Relationships of type " + rel_type + " were deleted."
            print(print_delete_relationship)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


class RemoveFeature(DjangoNode):
    # deletes 1 to n label(s)
    # select_node_label: string
    # list_of_labels_to_remove: array
    def delete_labels(session, select_node_label, list_of_labels_to_remove):
        records, summary, keys = session.execute_query(
            "MATCH (n:" + select_node_label + ") "
                                              "WITH collect(n) AS nodes "
                                              "CALL apoc.create.removeLabels(nodes, $list_of_labels_to_remove) "
                                              "YIELD node "
                                              "RETURN node; ",
            select_node_label=select_node_label, list_of_labels_to_remove=list_of_labels_to_remove
        )

        print_query_results = "The query `{query}` returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)
        print_delete_labels = "Label " + str(list_of_labels_to_remove) + " were deleted from nodes labeled " + \
                              select_node_label + "."
        print(print_delete_labels)

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # deletes 1 to n property key(s) form node(s)
    # select_node_label: string
    # list_of_keys_to_remove: array
    def delete_node_property_keys(tx, select_node_label, list_of_keys_to_remove):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + select_node_label + ") "
                                              "WITH collect(n) AS nodes "
                                              "CALL apoc.create.removeProperties(nodes, $list_of_keys_to_remove) "
                                              "YIELD node "
                                              "RETURN node; ",
            select_node_label=select_node_label, list_of_keys_to_remove=list_of_keys_to_remove
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms." \
                .format(query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_delete_node_properties = "The property keys " + str(list_of_keys_to_remove) + \
                                           " were deleted from nodes labeled " + select_node_label + "."
            print(print_delete_node_properties)
        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # deletes 1 to n property key(s) form relationship(s)
    # select_node_label: string
    # select_rel_type: string
    # list_of_keys_to_remove: array
    def delete_relationship_property_keys(tx, select_rel_type, list_of_keys_to_remove):
        records, summary, keys = tx.execute_query(
            "MATCH (n)-[rel:" + select_rel_type + "]-(n2) "
                                                  "WITH collect(rel) AS rels "
                                                  "CALL apoc.create.removeRelProperties(rels, "
                                                  "$list_of_keys_to_remove)"
                                                  "YIELD rel "
                                                  "RETURN rel; ",
            select_rel_type=select_rel_type,
            list_of_keys_to_remove=list_of_keys_to_remove
        )
        # TODO: Auslagern und für alle Funktionen verfügbar machen!!!!
        # print summary of the results from the query
        if len(records) > 0:
            print_query_results = "The query `{query}` returned {records_count} records in {time} ms." \
                .format(query=summary.query, records_count=len(records), time=summary.result_available_after)
            print(print_query_results)
            print_delete_relationship_properties = "The property keys " + str(list_of_keys_to_remove) + \
                                                   " were deleted from rels of type " + select_rel_type + "."
            print(print_delete_relationship_properties)

        else:
            # TODO: color warning red!
            print('WARNING: Something went wrong. Check your query.')

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


class CopyEntityType(DjangoNode):
    # add a new node by using the CREATE command
    # tx: access database session - from database.connection
    # select_node_label: string
    # copy_with_rels: boolean - true: copyOperation with rels, false: copyOperation without rels,
    # props_to_skip: array with property keys not to be in copied entity - sting can be left empty for no props to be skipped
    # ToDo: make key and value available for arrays --> add multiple keys and values
    def copy_node_entity(tx, select_node_label, copy_with_rels, props_to_skip):
        records, summary, keys = tx.execute_query(
            # "MATCH (p:" + select_node_label + ") "
            # # "WHERE p." + select_property_key + " = $select_property_value"
            #                                   "WITH collect(p) AS nodesToCopy "
            #                                   "CALL apoc.refactor.cloneNodes(nodesToCopy, $copy_with_rels, $props_to_skip) "
            #                                   "YIELD input, output "
            #                                   "RETURN input, output; ",
            """
            CALL apoc.periodic.iterate("
                MATCH (p:""" + select_node_label + """) 
                WITH collect(p) AS nodesToCopy
                RETURN nodesToCopy
                ", "
                CALL apoc.refactor.cloneNodes(nodesToCopy, """ + copy_with_rels + """, $props_to_skip)
                YIELD output
                RETURN output
                ", {batchSize: 10000, parallel: true, params: {props_to_skip: $props_to_skip}}
            )
            """,
            select_node_label=select_node_label, copy_with_rels=copy_with_rels, props_to_skip=props_to_skip,
        )

        for record in records:
            print(record.data())
        # print summary of the results from the query
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)
        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


class CopyFeature(DjangoNode):
    # ToDo: add function - copy_selected_label
    def copy_all_labels(tx, select_node_label_of_node_to_copy_from, node_label_of_node_to_copy_to):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + select_node_label_of_node_to_copy_from + ") "
                                                                   "WITH labels(n) as labels "
                                                                   "MATCH (n2:" + node_label_of_node_to_copy_to + ") "
                                                                                                                  "CALL apoc.create.addLabels(n2, labels) "
                                                                                                                  "YIELD node "
                                                                                                                  "RETURN node",
            select_node_label_of_node_to_copy_from=select_node_label_of_node_to_copy_from,
            node_label_of_node_to_copy_to=node_label_of_node_to_copy_to,
            database_="neo4j"
        )

        # Loop through results and do something with them
        for record in records:
            print(record.data())  # obtain record as dict
        if len(records) == 0:
            print('No pattern found. Check your query.')
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time

    # function to copy all properties of a node to another node
    def copy_all_props_from_node_to_node(session, node_label_a, node_label_b):
        start_timer = timer()
        map_a, map_b, number_of_nodes_a, number_of_nodes_b = _get_property_maps(session, node_label_a, node_label_b)

        merged_dicts_with_unique_values = _collection_handling_for_full_outer_inclusive_of_maps(map_a, map_b,
                                                                                                number_of_nodes_a,
                                                                                                number_of_nodes_b)

        # ToDo: add Cypher query to overwrite old entity types (copy- overwrite m = old entities,
        # full outer inclusive - delete n, overwrite m)
        if type(merged_dicts_with_unique_values) == dict:
            print(f'one map in list {len([merged_dicts_with_unique_values]) == 1}')
            copy_test_overwrite_initial_nodes(session, [merged_dicts_with_unique_values], node_label_b)
        else:
            print(f'n maps in list {len([merged_dicts_with_unique_values]) == 1}')
            copy_test_overwrite_initial_nodes(session, merged_dicts_with_unique_values, node_label_b)

        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)

        return merged_dicts_with_unique_values

    # ToDo: single value arrays not yet working with rels
    def copy_all_props_from_node_to_rel(session, node_label_a, start_node_label_rel, rel_type, end_node_label_rel):
        start_timer = timer()
        map_a, map_b, number_of_nodes_a, number_of_rels_b = _get_property_maps_node_to_rel(session, node_label_a,
                                                                                           start_node_label_rel,
                                                                                           rel_type,
                                                                                           end_node_label_rel)

        merged_dicts_with_unique_values = _collection_handling_for_full_outer_inclusive_of_maps(map_a, map_b,
                                                                                                number_of_nodes_a,
                                                                                                number_of_rels_b)

        # ToDo: add Cypher query to overwrite old entity types (copy- overwrite m = old entities,
        # full outer inclusive - delete n, overwrite m)
        if type(merged_dicts_with_unique_values) == dict:
            copy_test_overwrite_initial_rels(session, [merged_dicts_with_unique_values], start_node_label_rel, rel_type,
                                             end_node_label_rel)
        else:
            copy_test_overwrite_initial_rels(session, merged_dicts_with_unique_values, start_node_label_rel, rel_type,
                                             end_node_label_rel)

        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)

        return merged_dicts_with_unique_values, neo4j_query_time

    def copy_all_props_from_rel_to_node(session, start_node_label_rel, rel_type, end_node_label_rel, node_label_b):
        start_timer = timer()
        map_b, map_a, number_of_rels_b, number_of_nodes_a = _get_property_maps_node_to_rel(session, node_label_b,
                                                                                           start_node_label_rel,
                                                                                           rel_type,
                                                                                           end_node_label_rel)

        merged_dicts_with_unique_values = _collection_handling_for_full_outer_inclusive_of_maps(map_a, map_b,
                                                                                                number_of_nodes_a,
                                                                                                number_of_rels_b)
        # ToDo: add Cypher query to overwrite old entity types (copy- overwrite m = old entities,
        # full outer inclusive - delete n, overwrite m)
        if type(merged_dicts_with_unique_values) == dict:
            copy_test_overwrite_initial_nodes(session, [merged_dicts_with_unique_values], node_label_b)
        else:
            copy_test_overwrite_initial_nodes(session, merged_dicts_with_unique_values, node_label_b)

        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)

        return merged_dicts_with_unique_values, neo4j_query_time

    # ToDo rename number_of_nodes to number_of_rels
    def copy_all_props_from_rel_to_rel(session, start_node_label_a, rel_type_a, end_node_label_a, start_node_label_b,
                                       rel_type_b, end_node_label_b):
        start_timer = timer()
        map_a, map_b, number_of_rels_a, number_of_rels_b = _get_property_maps_rel_to_rel(session, start_node_label_a,
                                                                                         rel_type_a, end_node_label_a,
                                                                                         start_node_label_b,
                                                                                         rel_type_b, end_node_label_b)

        merged_dicts_with_unique_values = _collection_handling_for_full_outer_inclusive_of_maps(map_a, map_b,
                                                                                                number_of_rels_a,
                                                                                                number_of_rels_b)

        # ToDo:
        if type(merged_dicts_with_unique_values) == dict:
            copy_test_overwrite_initial_rels(session, [merged_dicts_with_unique_values], start_node_label_b, rel_type_b,
                                             end_node_label_b)
        else:
            copy_test_overwrite_initial_rels(session, merged_dicts_with_unique_values, start_node_label_b, rel_type_b,
                                             end_node_label_b)

        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)

        return merged_dicts_with_unique_values, neo4j_query_time


class MoveEntityType(DjangoNode):

    # node_label_of_old_end_node: string - label of node where the pattern is attached to
    # node_label_of_nodes_to_move: string - label of the nodes that you want to move with all relations to the old
    # pattern (node_label_of_old_end_node)
    # node_label_of_new_end_node:  label of the new end node which is already in the database (otherwise this node needs to
    # be created beforehand)
    def move_subgraph(tx, label_of_old_end_node, label_of_nodes_to_move, label_of_new_end_node):
        # TODO: make rels selectable?
        # TODO: make extended filter better usable to access more options
        records, summary, keys = tx.execute_query(
            "MATCH (oldEndNode:" + label_of_old_end_node + ")-[r]-(n2:" + label_of_nodes_to_move + ") "
                                                                                                   "OPTIONAL MATCH (newEndNode:" + label_of_new_end_node + ") "
                                                                                                                                                           "WITH collect(n2) AS whitelistNodes, oldEndNode, newEndNode "
                                                                                                                                                           "CALL apoc.path.subgraphAll(oldEndNode, { minLevel: 0, whitelistNodes: whitelistNodes }) "
                                                                                                                                                           "YIELD nodes, relationships "
                                                                                                                                                           "CALL apoc.refactor.cloneSubgraph(nodes,[rel IN relationships], {standinNodes:[[oldEndNode, newEndNode]]}) "
                                                                                                                                                           "YIELD input, output, error "
                                                                                                                                                           "CALL{ "
                                                                                                                                                           "MATCH (oldEndNode:" + label_of_old_end_node + ")-[r]-(n2:" + label_of_nodes_to_move + ") "
                                                                                                                                                                                                                                                  "WITH collect(n2) AS oldPatternNodes "
                                                                                                                                                                                                                                                  "FOREACH(n IN range(0,SIZE(oldPatternNodes)-1)| FOREACH(n1 IN [oldPatternNodes[n]] | DETACH DELETE n1)) "
                                                                                                                                                                                                                                                  "} "
                                                                                                                                                                                                                                                  "RETURN input AS node_id, output AS node_properties, error; ",
            label_of_old_end_node=label_of_old_end_node, label_of_nodes_to_move=label_of_nodes_to_move,
            label_of_new_end_node=label_of_new_end_node,
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time

    # moves a relationship to a new, specified start and end node
    # start_node_label: string - select pattern of current rel
    # rel_type: string - select type of relationship to be moved
    # end_node_label: string - select end node of pattern
    # new_start_node_label: string - define new start node for selected relationship(s)
    # new_end_node_label: string - define new end node for selected relationship(s)
    def move_relationship(tx, start_node_label, rel_type, end_node_label, new_start_node_label, new_end_node_label):
        records, summary, keys = tx.execute_query(
            "CALL{ "
            "MATCH (oldStartNode:" + start_node_label + ")-[r:" + rel_type + "]-(oldEndNode:" + end_node_label + ") "
                                                                                                                 "OPTIONAL MATCH (newStartNode:" + new_start_node_label + ") "
                                                                                                                                                                          "WITH r AS relsToMove, newStartNode "
                                                                                                                                                                          "CALL apoc.refactor.to(relsToMove, newStartNode) "
                                                                                                                                                                          "YIELD input, output, error "
                                                                                                                                                                          "RETURN output as movedRels "
                                                                                                                                                                          "} "
                                                                                                                                                                          "MATCH (newEndNode:" + new_end_node_label + ") "
                                                                                                                                                                                                                      "CALL apoc.refactor.from(movedRels, newEndNode) "
                                                                                                                                                                                                                      "YIELD input, output, error "
                                                                                                                                                                                                                      "RETURN input, output, error ",
            start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label,
            new_start_node_label=new_start_node_label, new_end_node_label=new_end_node_label
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time


class MoveFeature(DjangoNode):
    # start_node_label: string - select start nodes of the pattern
    # rel_type: string - select the type of the relationship of which the direction will be changed
    # end_node_label: string - select the end node of the pattern
    def move_direction(tx, start_node_label, rel_type, end_node_label):
        records, summary, keys = tx.execute_query(
            "CALL{ "
            "MATCH (start:" + start_node_label + ")-[r:" + rel_type + "]->(end:" + end_node_label + ") "
                                                                                                    "WITH r AS rels, start, end "
                                                                                                    "CALL apoc.refactor.to(rels, start) "
                                                                                                    "YIELD input, output, error "
                                                                                                    "RETURN output AS relLooped, rels, end "
                                                                                                    "} "
                                                                                                    "CALL apoc.refactor.from(relLooped, end) "
                                                                                                    "YIELD input, output, error "
                                                                                                    "RETURN input, output, error ",
            start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label,
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time

    # moves defined labels from a specific node if this node is multi-labeled
    # select_node_label: string
    # labels_to_move: array
    # node_label_to_copy_to: string
    # TODO: removeLabels in do.when reinschieben wegen mindestens 1 label pro Knoten?
    def move_selected_labels(tx, select_node_label, labels_to_move, node_label_to_copy_to):
        records, summary, keys = tx.execute_query(
            """
            MATCH (n:""" + select_node_label + """)
            WITH labels(n) AS node_labels, collect(n) AS nodes
            WITH $labels_to_move AS labels_to_move, node_labels, nodes
            WHERE any(x IN labels_to_move WHERE x IN node_labels)
            CALL {
                MATCH (n:""" + node_label_to_copy_to + """) WITH collect(n) AS nodes
                CALL apoc.create.addLabels(nodes, $labels_to_move) 
                Yield node 
                RETURN node AS result
            }
            CALL apoc.create.removeLabels(nodes, $labels_to_move)
            Yield node
            RETURN node, labels_to_move
            """,
            select_node_label=select_node_label, labels_to_move=labels_to_move,
            node_label_to_copy_to=node_label_to_copy_to
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time

    def move_all_props_from_node_to_node(session, node_label_a, node_label_b):
        start_timer = timer()
        CopyFeature.copy_all_props_from_node_to_node(session, node_label_a, node_label_b)
        remove_all_props_from_nodes(session, node_label_a)
        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)
        return neo4j_query_time

    def move_all_props_from_node_to_rel(session, node_label_a, start_node_label_rel, rel_type, end_node_label_rel):
        start_timer = timer()
        CopyFeature.copy_all_props_from_node_to_rel(session, node_label_a, start_node_label_rel, rel_type,
                                                    end_node_label_rel)
        remove_all_props_from_nodes(session, node_label_a)
        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)
        return neo4j_query_time

    def move_all_props_from_rel_to_node(session, start_node_label_rel, rel_type, end_node_label_rel, node_label_b):
        start_timer = timer()
        CopyFeature.copy_all_props_from_rel_to_node(session, start_node_label_rel, rel_type, end_node_label_rel,
                                                    node_label_b)

        remove_all_props_from_rels(session, start_node_label_rel, rel_type, end_node_label_rel)
        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)
        return neo4j_query_time

    # ToDo: test if props are removed from correct entity
    def move_all_props_from_rel_to_rel(session, start_node_label_a, rel_type_a, end_node_label_a,
                                       start_node_label_b, rel_type_b, end_node_label_b):
        start_timer = timer()
        CopyFeature.copy_all_props_from_rel_to_rel(session, start_node_label_a, rel_type_a, end_node_label_a,
                                                   start_node_label_b, rel_type_b, end_node_label_b)

        remove_all_props_from_rels(session, start_node_label_a, rel_type_a, end_node_label_a)
        end_timer = timer()
        neo4j_query_time = (end_timer - start_timer)
        return neo4j_query_time


class SplitEntityType(DjangoNode):
    # node_label: string - of the node to be split
    # property_to_split_at: string - property key to be split at
    def split_node(tx, node_label, property_to_split_at):
        records, summary, keys = tx.execute_query(
            "CALL{ "
            "MATCH (n:" + node_label + ") "
                                       "CALL  apoc.refactor.cloneNodes([n], TRUE) "
                                       "YIELD error, output "
                                       "RETURN error, output, n "
                                       "} "
                                       "CALL { "
                                       "MATCH (n:" + node_label + ") "
                                                                  "WITH properties(n) AS map "
                                                                  "WITH keys(map) AS keys, [k IN KEYS(map) | map[k]] AS values "
                                                                  "WITH DISTINCT [x IN range(0,SIZE(keys)-1) "
                                                                  "WHERE keys[x] = $property_to_split_at] AS posKey, SIZE(keys) AS sizeKeys, keys, values "
                                                                  "WITH keys[..posKey[0]] AS keysNodeA,  keys[posKey[0]..] AS keysNodeB "
                                                                  "WITH collect(keysNodeA) AS keysA, collect(keysNodeB) AS keysB "
                                                                  "RETURN keysA, keysB "
                                                                  "} "
                                                                  "WITH collect(output) AS output, keysA, keysB, collect(n) AS initialNodes "
                                                                  "WITH [x IN range(0, size(keysA)-1)|apoc.map.removeKeys(output[x],keysA[x])] AS resultsA, "
                                                                  "[x IN range(0, size(keysB)-1)|apoc.map.removeKeys(output[x], keysB[x])] AS resultsB, "
                                                                  "output, initialNodes "
                                                                  "FOREACH(n IN range(0, SIZE(output)-1)| FOREACH (n1 IN [output[n]]| SET n1 = properties(resultsA[n]))) "
                                                                  "FOREACH(n IN range(0, SIZE(initialNodes)-1)| FOREACH (n1 IN [initialNodes[n]]| "
                                                                  "SET n1 = properties(resultsB[n]))) ",
            node_label=node_label, property_to_split_at=property_to_split_at, database="neo4j",
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time

    # start_node_label: string - of the start node of pattern
    # property_to_split_at: string - property key to be split at
    def split_relationship(tx, rel_type, start_node_label, end_node_label, property_to_split_at):
        records, summary, keys = tx.execute_query(
            """
               CALL{ 
                    MATCH (n:""" + start_node_label + """)-[r:""" + rel_type + """]->(:""" + end_node_label + """)
                    WITH collect(r) AS relsOfInitalNodes
                    RETURN DISTINCT relsOfInitalNodes
                }
                CALL{
                    MATCH (n:""" + start_node_label + """)
                    CALL  apoc.refactor.cloneNodes([n], TRUE)
                    YIELD error, output
                    RETURN error, output, n
                }
                CALL { 
                    MATCH (n:""" + start_node_label + """)-[r:""" + rel_type + """]->(m:""" + end_node_label + """)
                    WITH properties(r) AS map
                    WITH keys(map) AS keys, [k IN KEYS(map) | map[k]] AS values
                    WITH DISTINCT [x IN range(0,size(keys)-1) WHERE keys[x] = $property_to_split_at] AS posKey, size(keys) AS sizeKeys , keys, values
                    WITH keys[..posKey[0]] AS keysNodeA,  keys[posKey[0]..] AS keysNodeB
                    WITH collect(keysNodeA) AS keysA, collect(keysNodeB) AS keysB
                    RETURN keysA, keysB
                }
                MATCH (output)-[r2]->(m:""" + end_node_label + """)
                WITH collect(r2) as relsOfOutput, keysA, keysB, relsOfInitalNodes, collect(output) as output, collect(n) as initialNodes
                WITH [x IN range(0, size(keysA)-1)|apoc.map.removeKeys(relsOfOutput[x], keysA[x])] AS resultsA, [x IN range(0, size(keysB)-1)|apoc.map.removeKeys(relsOfInitalNodes[x], keysB[x])] AS resultsB, relsOfOutput, relsOfInitalNodes, output, initialNodes
                FOREACH(n IN range(0, size(relsOfOutput)-1)| FOREACH (n1 in [relsOfOutput[n]]| SET n1 = properties(resultsA[n])))
                FOREACH(n IN range(0, size(relsOfInitalNodes)-1)| FOREACH (n1 IN [relsOfInitalNodes[n]]| SET n1 = properties(resultsB[n])))

            """,
            rel_type=rel_type, start_node_label=start_node_label, end_node_label=end_node_label,
            property_to_split_at=property_to_split_at, database="neo4j",
        )
        neo4j_query_time = "{time}".format(time=summary.result_available_after)
        return records, neo4j_query_time


class TransformEntityType(DjangoNode):
    # transform a node to a relationship - all cases 1 to 4 are caught
    # start_node_label: string
    # middle_node_label: string
    # end_node_label: string
    # rel_type: string
    # ToDo: break if pattern has more than one rel between start and middle & middle and end node
    def transform_node_to_relationship(tx, start_node_label, middle_node_label, end_node_label, rel_type):
        _transform_node_to_relationship_general_direction(tx, start_node_label, middle_node_label, end_node_label,
                                                          rel_type)
        _transform_node_to_relationship_no_general_direction(tx, start_node_label, middle_node_label, end_node_label,
                                                             rel_type)

    # select_start_node_label: string
    # select_rel_type: string of relation to be transformed
    # select_end_node_label: string
    # new_labels: array of strings for labels of newly created node entity
    # ingoing_rel: string - type for left, ingoing relationship to new node entity
    # outgoing_rel: string - type for right, outgoing relationship to new node entity
    def transform_relationship_to_node(tx, select_start_node_label, select_rel_type, select_end_node_label, new_labels,
                                       ingoing_rel, outgoing_rel):
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + select_start_node_label + ")-[r:" + select_rel_type + "]-(n2:" + select_end_node_label + ") "
                                                                                                                   "WITH collect(r) AS rels "
                                                                                                                   "CALL apoc.refactor.extractNode(rels,[$new_labels],$ingoing_rel,$outgoing_rel) "
                                                                                                                   "YIELD input, output "
                                                                                                                   "RETURN input, output; ",
            select_start_node_label=select_start_node_label, select_rel_type=select_rel_type,
            select_end_node_label=select_end_node_label, new_labels=new_labels, ingoing_rel=ingoing_rel,
            outgoing_rel=outgoing_rel, database_="neo4j"
        )

        # Loop through results and do something with them
        for record in records:
            print(record.data())  # obtain record as dict
        if len(records) == 0:
            print('No pattern found. Check your query.')
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)

        neo4j_query_time = "{time}".format(time=summary.result_available_after)

        return records, neo4j_query_time


# transforms nodes with two in- or outgoing relationships
# start_node_label: string
# middle_node_label: string
# end_node_label: string
# rel_type: string
def _transform_node_to_relationship_no_general_direction(tx, start_node_label, middle_node_label, end_node_label,
                                                         rel_type):
    records, summary, keys = tx.execute_query(
        "MATCH (n:" + start_node_label + ")-[r]->(n2:" + middle_node_label + ")<-[r2]-(n3:" + end_node_label + ") "
                                                                                                               "OPTIONAL MATCH (n4:" + start_node_label + ")<-[r3]-(n5:" + middle_node_label + ")-[r4]->(n6:" + end_node_label + ") "
                                                                                                                                                                                                                                 "RETURN n2, n5",
        start_node_label=start_node_label, middle_node_label=middle_node_label, end_node_label=end_node_label,
        database_="neo4j"
    )

    if len(records) > 0:
        print("Pattern for workaround found. ")
        # TODO: Is it possible to shorten this code fragment?
        records, summary, keys = tx.execute_query(
            "CALL{ "
            "MATCH (n:" + start_node_label + ")-[r]->(n2:" + middle_node_label + ")<-[r2]-(n3:" + end_node_label + ") "
                                                                                                                   "WITH n AS startNodes, collect(n2) AS nodesToTransform, n3 AS endNodes, properties(n2) as props "
                                                                                                                   "CALL apoc.create.relationship(startNodes, $rel_type, props, endNodes) "
                                                                                                                   "YIELD rel "
                                                                                                                   "FOREACH (n IN range(0,SIZE(nodesToTransform)-1)| FOREACH (n1 IN [nodesToTransform[n]]| DETACH DELETE n1)) "
                                                                                                                   "RETURN startNodes, rel, endNodes"
                                                                                                                   "} "
                                                                                                                   "CALL{ "
                                                                                                                   "MATCH (n4:" + start_node_label + ")<-[r3]-(n5:" + middle_node_label + ")-[r4]->(n6:" + end_node_label + ") "
                                                                                                                                                                                                                            "WITH n4 AS startNodes2, collect(n5) AS nodesToTransform2, n6 AS endNodes2, properties(n5) as props2 "
                                                                                                                                                                                                                            "CALL apoc.create.relationship(startNodes2, $rel_type, props2, endNodes2) "
                                                                                                                                                                                                                            "YIELD rel "
                                                                                                                                                                                                                            "FOREACH (n IN range(0,SIZE(nodesToTransform2)-1)| FOREACH (n1 IN [nodesToTransform2[n]]| DETACH DELETE n1)) "
                                                                                                                                                                                                                            "RETURN startNodes2, rel AS rel2, endNodes2"
                                                                                                                                                                                                                            "} "
                                                                                                                                                                                                                            "RETURN startNodes, rel, endNodes, startNodes2, rel2, endNodes2",
            start_node_label=start_node_label, middle_node_label=middle_node_label, end_node_label=end_node_label,
            rel_type=rel_type, database_="neo4j"
        )

        # Loop through results and do something with them
        for record in records:
            print(record.data())  # obtain record as dict

            # Summary information
        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)

    else:
        print('No pattern for workaround found. ')

    neo4j_query_time = "{time}".format(time=summary.result_available_after)

    return records, neo4j_query_time


# transforms nodes with one in- and one outgoing relationship
# start_node_label: string
# middle_node_label: string
# end_node_label: string
# rel_type: string
def _transform_node_to_relationship_general_direction(tx, start_node_label, middle_node_label, end_node_label,
                                                      rel_type):
    records, summary, keys = tx.execute_query(
        "MATCH (n:" + start_node_label + ")-[r]->(n2:" + middle_node_label + ")-[r2]->(n3:" + end_node_label + ") "
                                                                                                               "OPTIONAL MATCH (n4:" + start_node_label + ")<-[r3]-(n5:" + middle_node_label + ")<-[r4]-(n6:" + end_node_label + ") "
                                                                                                                                                                                                                                 "RETURN n2, n5",
        start_node_label=start_node_label, middle_node_label=middle_node_label, end_node_label=end_node_label,
        database_="neo4j"
    )

    if len(records) > 0:
        print("Pattern for collapse node function found. ")
        records, summary, keys = tx.execute_query(
            "MATCH (n:" + start_node_label + ")-[r]-(n2:" + middle_node_label + ")-[r2]-(n3:" + end_node_label + ") "
            # "OPTIONAL MATCH (n4:" + start_node_label + ")<-[r3]-(n5:" + middle_node_label + ")<-[r4]-(n6:" + end_node_label + ") "
                                                                                                                 "WITH collect(n2) AS nodesToCollapse "
                                                                                                                 "CALL apoc.refactor.collapseNode(nodesToCollapse,$rel_type) "
                                                                                                                 "YIELD input, output, error "
                                                                                                                 "RETURN input, output, error",
            middle_node_label=middle_node_label, rel_type=rel_type, database_="neo4j"
        )

        # Loop through results and do something with them
        for record in records:
            print(record.data())  # obtain record as dict

        print_query_results = "The query `{query}` \nreturned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records), time=summary.result_available_after)
        print(print_query_results)

    else:
        print('No pattern for collapse nodes function found. ')

    neo4j_query_time = "{time}".format(time=summary.result_available_after)

    return records, neo4j_query_time


class MergeEntityTypes(DjangoNode):
    def full_outer_inclusive_merge_of_nodes(session, node_label_a, node_label_b):
        map_a, map_b, number_of_nodes_a, number_of_nodes_b = _get_property_maps(session, node_label_a, node_label_b)

        # res = combine_nodes_to_copy_or_join(number_of_nodes_a, map_a)
        res = _full_outer_inclusive_of_property_maps(number_of_nodes_a, map_a)
        # new_map_b = full_outer_inclusive_of_property_maps(number_of_nodes_b, map_b)

        temp, temp2 = _nodes_to_copy_merge_to(number_of_nodes_b, res, map_b, True)
        # temp = nodes_to_copy_merge_to(number_of_nodes_b, res, new_map_b)

        print(f'temp 2: {temp2}')

        # only for nx1, 1x1
        if number_of_nodes_a > number_of_nodes_b == 1:
            # if number_of_nodes_a > number_of_nodes_b or (number_of_nodes_a == 1 and number_of_nodes_a == number_of_nodes_b)
            merged_dicts_with_unique_values = _merge_dicts_with_unique_values(temp)
            _single_dict_with_single_value(merged_dicts_with_unique_values)

        elif number_of_nodes_a == number_of_nodes_b:
            if number_of_nodes_a == 1:
                merged_dicts_with_unique_values = _merge_dicts_with_unique_values(temp)
                for key, value in merged_dicts_with_unique_values.items():
                    if type(value) == list and len(value) == 1:
                        merged_dicts_with_unique_values[key] = value[0]
                    else:
                        break
                merged_dicts_with_unique_values = temp
            else:
                merged_dicts_with_unique_values = _list_with_single_value(temp2)
        else:
            merged_dicts_with_unique_values = _list_with_single_value(temp2)
        print(merged_dicts_with_unique_values)
        print(len(merged_dicts_with_unique_values))

        # copy_test_overwrite_initial_nodes_2(session, merged_dicts_with_unique_values, node_label_b, node_label_a)

        if type(merged_dicts_with_unique_values) == dict:
            print(f'one map in list {len([merged_dicts_with_unique_values]) == 1}')
            copy_test_overwrite_initial_nodes_2(session, [merged_dicts_with_unique_values], node_label_b, node_label_a)
        else:
            print(f'n maps in list {len([merged_dicts_with_unique_values]) == 1}')
            copy_test_overwrite_initial_nodes_2(session, merged_dicts_with_unique_values, node_label_b, node_label_a)
        return merged_dicts_with_unique_values

        return merged_dicts_with_unique_values

    def merge_relationships(self):
        records, summary, keys = self.execute_query(
            """
            """,
        )
        return records, summary, keys


def copy_node_props_to_node_with_collection_handling(tx, node_label_a, node_label_b):
    record = tx.execute_query(
        """
        CALL {
            Match (n:""" + node_label_a + """)
                WITH  collect(properties(n)) AS map_a
                RETURN map_a
            }
            CALL{
                MATCH (m:""" + node_label_b + """)
                WITH collect(properties(m)) AS map_b
                RETURN map_b
            }
            RETURN map_a, map_b
            """,
        database_="neo4j",
        node_label_a=node_label_a, node_label_b=node_label_b,
        result_transformer_=neo4j.Result.single,
    )
    map_a = record[0]
    map_b = record[1]
    # print(f'Map_A: {map_a}')
    # print(f'Map_B: {map_b}')
    # print(record)
    return map_a, map_b


def remove_all_props_from_nodes(tx, node_label):
    records, summary, keys = tx.execute_query(
        """
        MATCH (n:""" + node_label + """) 
        WITH collect(n) AS nodes
        FOREACH(n IN range(0, size(nodes)-1)| FOREACH (n1 in [nodes[n]]| SET n1 = {}))
        RETURN nodes
        """,
        node_label=node_label, database_="neo4j",
    )
    return records, summary, keys


def remove_all_props_from_rels(tx, start_node_label, rel_type, end_node_label):
    records, summary, keys = tx.execute_query(
        """
        MATCH (n:""" + start_node_label + """)-[r:""" + rel_type + """]->(n2:""" + end_node_label + """) 
        WITH collect(r) AS rels
        FOREACH(r IN range(0, size(rels)-1)| FOREACH (r1 in [rels[r]]| SET r1 = {}))
        """,
        start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label, database_="neo4j",
    )
    return records, summary, keys


def copy_node_props_to_rel_with_collection_handling(tx, node_label_a, start_node_label_rel, rel_type,
                                                    end_node_label_rel):
    record = tx.execute_query(
        """
        CALL {
            Match (n:""" + node_label_a + """)
                WITH  collect(properties(n)) AS map_a
                RETURN map_a
            }
            CALL{
                MATCH (m:""" + start_node_label_rel + """)-[r:""" + rel_type + """]->(m2:""" + end_node_label_rel + """)
                WITH collect(properties(r)) AS map_b
                RETURN map_b
            }
            RETURN map_a, map_b
            """,
        database_="neo4j",
        node_label_a=node_label_a, start_node_label_rel=start_node_label_rel, rel_type=rel_type,
        end_node_label_rel=end_node_label_rel,
        result_transformer_=neo4j.Result.single,
    )
    map_a = record[0]
    map_b = record[1]

    return map_a, map_b


def copy_rel_props_to_rel_with_collection_handling(tx, start_node_label_a, rel_type_a, end_node_label_a,
                                                   start_node_label_b, rel_type_b, end_node_label_b):
    record = tx.execute_query(
        """
        CALL {
            MATCH (n:""" + start_node_label_a + """)-[r:""" + rel_type_a + """]->(n2:""" + end_node_label_a + """)
                WITH  collect(properties(r)) AS map_a
                RETURN map_a
            }
            CALL{
                MATCH (m:""" + start_node_label_b + """)-[r2:""" + rel_type_b + """]->(m2:""" + end_node_label_b + """)
                WITH collect(properties(r2)) AS map_b
                RETURN map_b
            }
            RETURN map_a, map_b
            """,
        database_="neo4j",
        start_node_label_a=start_node_label_a, rel_type_a=rel_type_a, end_node_label_a=end_node_label_a,
        start_node_label_b=start_node_label_b, rel_type_b=rel_type_b, end_node_label_b=end_node_label_b,
        result_transformer_=neo4j.Result.single,
    )
    map_a = record[0]
    map_b = record[1]

    return map_a, map_b


def copy_node_props_to_node_get_nbr_of_entities(tx, node_label_a, node_label_b):
    record = tx.execute_query(
        """
        CALL {
            Match (n:""" + node_label_a + """)
                WITH  count(n) AS number_of_nodes_a
                RETURN number_of_nodes_a
            }
            CALL{
                match (m:""" + node_label_b + """)
                WITH count(m) AS number_of_nodes_b
                RETURN number_of_nodes_b
            }
            RETURN number_of_nodes_a, number_of_nodes_b
            """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        database_="neo4j",
        node_label_a=node_label_a, node_label_b=node_label_b,
        result_transformer_=neo4j.Result.single,

    )
    assert record is not None  # for typechecking and illustration
    number_of_nodes_a = record[0]
    number_of_nodes_b = record[1]
    assert isinstance(number_of_nodes_a, int)
    assert isinstance(number_of_nodes_b, int)
    return number_of_nodes_a, number_of_nodes_b


def copy_node_props_to_rel_get_nbr_of_entities(tx, node_label_a, start_node_label_b, rel_type_b, end_node_label_b):
    record = tx.execute_query(
        """
        CALL {
            Match (n:""" + node_label_a + """)
                WITH  count(n) AS number_of_nodes_a
                RETURN number_of_nodes_a
            }
            CALL{
                MATCH (m:""" + start_node_label_b + """)-[r2:""" + rel_type_b + """]->(m2:""" + end_node_label_b + """)
                WITH count(m) AS number_of_nodes_b
                RETURN number_of_nodes_b
            }
            RETURN number_of_nodes_a, number_of_nodes_b
            """,
        database_="neo4j",
        node_label_a=node_label_a, start_node_label_b=start_node_label_b, rel_type_b=rel_type_b,
        end_node_label_b=end_node_label_b,
        result_transformer_=neo4j.Result.single,

    )
    assert record is not None  # for typechecking and illustration
    number_of_nodes_a = record[0]
    number_of_nodes_b = record[1]
    assert isinstance(number_of_nodes_a, int)
    assert isinstance(number_of_nodes_b, int)
    return number_of_nodes_a, number_of_nodes_b


def copy_rel_props_to_rel_get_nbr_of_entities(tx, start_node_label_a, rel_type_a, end_node_label_a,
                                              start_node_label_b, rel_type_b, end_node_label_b):
    record = tx.execute_query(
        """
        CALL {
            MATCH (n:""" + start_node_label_a + """)-[r:""" + rel_type_a + """]->(n2:""" + end_node_label_a + """)
                WITH  count(n) AS number_of_nodes_a
                RETURN number_of_nodes_a
            }
            CALL{
                MATCH (m:""" + start_node_label_b + """)-[r2:""" + rel_type_b + """]->(m2:""" + end_node_label_b + """)
                WITH count(m) AS number_of_nodes_b
                RETURN number_of_nodes_b
            }
            RETURN number_of_nodes_a, number_of_nodes_b
            """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        database_="neo4j",
        start_node_label_a=start_node_label_a, rel_type_a=rel_type_a, end_node_label_a=end_node_label_a,
        start_node_label_b=start_node_label_b, rel_type_b=rel_type_b, end_node_label_b=end_node_label_b,
        result_transformer_=neo4j.Result.single,

    )
    assert record is not None  # for typechecking and illustration
    number_of_nodes_a = record[0]
    number_of_nodes_b = record[1]
    assert isinstance(number_of_nodes_a, int)
    assert isinstance(number_of_nodes_b, int)
    return number_of_nodes_a, number_of_nodes_b


# for copy properties
def copy_test_overwrite_initial_nodes_2(tx, list, node_label, node_to_delete_label):
    record = tx.execute_query(
        # // WITH [{prop1: 'value1', prop2: 'value2'}, {prop3: 'value3', prop4: 'value4'}, {prop5: 'value5'}, {prop6: 'value6'}] AS list
        """
        With $list AS list
        MATCH (n:""" + node_label + """) with collect(n) as nodes, list
        FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[x] ))
        WITH nodes, list
        CALL{
            MATCH (m:""" + node_to_delete_label + """)
            DETACH DELETE m
        }
        //RETURN nodes   
        """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        list=list, node_label=node_label, node_to_delete_label=node_to_delete_label, database_="neo4j",

        result_transformer_=neo4j.Result.single,

    )
    return record


def copy_test_overwrite_initial_nodes(tx, list, node_label):
    record = tx.execute_query(
        # // WITH [{prop1: 'value1', prop2: 'value2'}, {prop3: 'value3', prop4: 'value4'}, {prop5: 'value5'}, {prop6: 'value6'}] AS list
        """
        With $list AS list
        MATCH (n:""" + node_label + """)
        WITH size(list) = 1 AS list_size, list
        CALL apoc.do.when(
            true, 
            'MATCH (n:""" + node_label + """) with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[0])) RETURN nodes', 
            'MATCH (n:""" + node_label + """) with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[x])) RETURN nodes',
            {list:list}
        )
        YIELD value
        RETURN value.nodes AS nodes
        """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        list=list, node_label=node_label, database_="neo4j",

        result_transformer_=neo4j.Result.single,

    )
    return record


def copy_test_overwrite_initial_nodes_delete_old_nodes(tx, list, node_label, node_to_delete_label):
    record = tx.execute_query(
        # // WITH [{prop1: 'value1', prop2: 'value2'}, {prop3: 'value3', prop4: 'value4'}, {prop5: 'value5'}, {prop6: 'value6'}] AS list
        """
        With $list AS list
        MATCH (n:""" + node_label + """)
            WITH size(list) = 1 AS list_size, list
            CALL apoc.do.when(
                true, 
                'MATCH (n:""" + node_label + """) with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[0])) RETURN nodes', 
                'MATCH (n:""" + node_label + """) with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[x])) RETURN nodes',
                {list:list}
                )
            YIELD value
                
            MATCH (m:""" + node_to_delete_label + """)
            DETACH DELETE m
            // RETURN value.nodes AS nodes
            """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        list=list, node_label=node_label, node_to_delete_label=node_to_delete_label, database_="neo4j",
        result_transformer_=neo4j.Result.single,
    )

    return record


def copy_test_overwrite_initial_rels(tx, list, start_node_label, rel_type, end_node_label):
    record = tx.execute_query(
        # // WITH [{prop1: 'value1', prop2: 'value2'}, {prop3: 'value3', prop4: 'value4'}, {prop5: 'value5'}, {prop6: 'value6'}] AS list
        """
        With $list AS list
        MATCH (n:""" + start_node_label + """)-[r:""" + rel_type + """]->(n2:""" + end_node_label + """) 
            WITH collect(r) as rels, list
            FOREACH (x in range(0,size(rels)-1)| FOREACH (x1 in [rels[x]] |SET x1 = list[x]))
            // RETURN rels   
            """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        list=list, start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label,
        database_="neo4j",
        result_transformer_=neo4j.Result.single,
    )
    return record


def copy_test_overwrite_initial_rels_2(tx, list, start_node_label, rel_type, end_node_label):
    record = tx.execute_query(
        # // WITH [{prop1: 'value1', prop2: 'value2'}, {prop3: 'value3', prop4: 'value4'}, {prop5: 'value5'}, {prop6: 'value6'}] AS list
        """
        With $list AS list
        MATCH (n:""" + start_node_label + """)-[r:""" + rel_type + """] (n2:""" + end_node_label + """) 
            WITH size(list) = 1
            CALL apoc.do.when(
                true, 
                'MATCH (n)-[r] (n2) with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[0])) RETURN nodes', 
                'MATCH (n)-[r] (n2)  with collect(n) as nodes, list FOREACH (x in range(0,size(nodes)-1)| FOREACH (x1 in [nodes[x]] |SET x1 = list[x])) RETURN nodes',
                {n:n, r:r, n2:n2}
                )
            YIELD value
            RETURN value.nodes AS nodes  
            """,
        # optional routing parameter, as write is default
        # routing_=neo4j.RoutingControl.WRITE,  # or just "w",
        list=list, start_node_label=start_node_label, rel_type=rel_type, end_node_label=end_node_label,
        database_="neo4j",
        result_transformer_=neo4j.Result.single,
    )
    return record


def _collection_handling_for_full_outer_inclusive_of_maps(map_a, map_b, number_of_entities_a, number_of_entities_b):
    res = _full_outer_inclusive_of_property_maps(number_of_entities_a, map_a)

    temp, temp2 = _nodes_to_copy_merge_to(number_of_entities_b, res, map_b, True)

    print(f'temp 2: {temp2}')

    # only for nx1, 1x1
    if number_of_entities_a > number_of_entities_b == 1:
        # if number_of_nodes_a > number_of_nodes_b or (number_of_nodes_a == 1 and number_of_nodes_a == number_of_nodes_b)
        print(f'{number_of_entities_a} > {number_of_entities_b}')
        merged_dicts_with_unique_values = _merge_dicts_with_unique_values(temp)
        _single_dict_with_single_value(merged_dicts_with_unique_values)

    # nxn and n>1

    # nxm, 1xm, nxn while n>1
    elif number_of_entities_a == number_of_entities_b:
        if number_of_entities_a == 1:
            print(f'temp before single array {temp}')
            merged_dicts_with_unique_values = _merge_dicts_with_unique_values(temp)
            for key, value in merged_dicts_with_unique_values.items():
                if type(value) == list and len(value) == 1:
                    merged_dicts_with_unique_values[key] = value[0]
                else:
                    break
            merged_dicts_with_unique_values = temp
        else:
            merged_dicts_with_unique_values = _list_with_single_value(temp2)
    else:
        print(f'{number_of_entities_a} < {number_of_entities_b}')
        merged_dicts_with_unique_values = _list_with_single_value(temp2)
    print(f'merged_dicts_with_unique_values: {merged_dicts_with_unique_values}')
    return merged_dicts_with_unique_values


def _get_property_maps(session, node_label_a, node_label_b):
    map_a, map_b = copy_node_props_to_node_with_collection_handling(session, node_label_a, node_label_b)
    print(f'Map_A: {map_a}')
    print(f'Map_B: {map_b}')

    number_of_nodes_a, number_of_nodes_b = copy_node_props_to_node_get_nbr_of_entities(session, node_label_a,
                                                                                       node_label_b)
    print(print(f'number_of_nodes_a: {number_of_nodes_a}'))
    print(print(f'number_of_nodes_b: {number_of_nodes_b}'))
    return map_a, map_b, number_of_nodes_a, number_of_nodes_b


def _get_property_maps_node_to_rel(session, node_label_a, start_node_label_b,
                                   rel_type_b, end_node_label_b):
    map_a, map_b = copy_node_props_to_rel_with_collection_handling(session, node_label_a, start_node_label_b,
                                                                   rel_type_b, end_node_label_b)
    print(f'Map_A: {map_a}')
    print(f'Map_B: {map_b}')

    number_of_nodes_a, number_of_rels_b = copy_node_props_to_rel_get_nbr_of_entities(session, node_label_a,
                                                                                     start_node_label_b,
                                                                                     rel_type_b, end_node_label_b)
    print(print(f'number_of_rels_a: {number_of_nodes_a}'))
    print(print(f'number_of_rels_b: {number_of_rels_b}'))
    return map_a, map_b, number_of_nodes_a, number_of_rels_b


def _get_property_maps_rel_to_rel(session, start_node_label_a, rel_type_a, end_node_label_a, start_node_label_b,
                                  rel_type_b, end_node_label_b):
    map_a, map_b = copy_rel_props_to_rel_with_collection_handling(session, start_node_label_a, rel_type_a,
                                                                  end_node_label_a, start_node_label_b,
                                                                  rel_type_b, end_node_label_b)
    print(f'Map_A: {map_a}')
    print(f'Map_B: {map_b}')

    number_of_rels_a, number_of_rels_b = copy_rel_props_to_rel_get_nbr_of_entities(session, start_node_label_a,
                                                                                   rel_type_a,
                                                                                   end_node_label_a, start_node_label_b,
                                                                                   rel_type_b, end_node_label_b)
    print(print(f'number_of_rels_a: {number_of_rels_a}'))
    print(print(f'number_of_rels_b: {number_of_rels_b}'))
    return map_a, map_b, number_of_rels_a, number_of_rels_b


def _dictionary_keys(input, keys_dict):
    if type(input) == list:
        for item in input:
            for key, val in item.items():
                keys_dict.append(key)

    elif type(input) == dict:
        for key, value in input.items():
            keys_dict.append(key)
    else:
        pass

    return keys_dict


def _retrieve_duplicate_keys(key_list_a, key_list_b, list_to_search):
    for key in key_list_a:
        if key in key_list_b:
            print(f'key in shorter_key_list: {key}')
        else:
            for item in list_to_search:
                for element in item.items():
                    if element[0] == key:
                        # https://www.geeksforgeeks.org/python-remove-key-from-dictionary-list/
                        # removes key of longer_list
                        list_to_search = list(
                            map(lambda d: {k: v for k, v in d.items() if k != element[0]}, list_to_search))
            # if all keys are removed - empty dict will be created
            if len(list_to_search) == 0:
                list_to_search = {}
    return list_to_search


def _retrieve_unique_keys(key_list_a, key_list_b, list_to_search):
    for key in key_list_a:
        if key in key_list_b:
            for item in list_to_search:
                for element in item.items():
                    if element[0] == key:
                        # https://www.geeksforgeeks.org/python-remove-key-from-dictionary-list/
                        # removes key of longer_list
                        list_to_search = list(
                            map(lambda d: {k: v for k, v in d.items() if k != element[0]}, list_to_search))
            # if all keys are removed - empty dict will be created
            if len(list_to_search) == 0:
                list_to_search = {}
        else:
            print(f'key NOT in list: {key}')
    return list_to_search


def _keep_duplicate_or_unique_keys_only(keys_dict_a, keys_dict_b, list_a, list_b, duplicates):
    if len(keys_dict_a) > len(keys_dict_b):
        longer_key_list = keys_dict_a
        shorter_key_list = keys_dict_b
        longer_list = list_a
        shorter_list = list_b
    else:
        longer_key_list = keys_dict_b
        shorter_key_list = keys_dict_a
        longer_list = list_b
        shorter_list = list_a
    print(f'shorter list A: {shorter_list}')
    print(f'longer list A: {longer_list}')
    if duplicates:
        longer_list = _retrieve_duplicate_keys(longer_key_list, shorter_key_list, longer_list)

        shorter_list = _retrieve_duplicate_keys(shorter_key_list, longer_key_list, shorter_list)

    else:
        longer_list = _retrieve_unique_keys(longer_key_list, shorter_key_list, longer_list)
        shorter_list = _retrieve_unique_keys(shorter_key_list, longer_key_list, shorter_list)

    print(f'Longer list C: {longer_list}')
    print(f'Shorter list C: {shorter_list}')

    return longer_list, shorter_list


def _mergeDictionary(dict_1, dict_2):
    dict_3 = {**dict_1, **dict_2}
    for key, value in dict_3.items():
        # if type(value) == list:
        #     print(f'List value: {value}')
        if key in dict_1 and key in dict_2:
            dict_3[key] = [value, dict_1[key]]

    return dict_3


def _full_outer_inclusive_of_property_maps(number_of_nodes, property_maps):
    result_dict = {}
    result_dict_2 = {}
    # nodes n to copy from - combine all values of duplicate property keys (to keep arrays)
    # if n nodes
    if number_of_nodes > 1:
        # n nodes
        for i, item in enumerate(property_maps):
            fist_dict = i
            second_dict = i + 1
            max = number_of_nodes
            if number_of_nodes == 2:
                merged_dicts = _mergeDictionary(property_maps[0], property_maps[1])
                result_dict = _merge_dicts_with_unique_values(merged_dicts)
            elif number_of_nodes > 2:

                print("----------------------------------")
                if second_dict != max:
                    merged_dicts = _mergeDictionary(property_maps[fist_dict], property_maps[second_dict])
                    merged_dicts = _merge_dicts_with_unique_values(merged_dicts)
                    result_dict.update(merged_dicts)
                    if len(result_dict) > 0:
                        merged_dicts_2 = _mergeDictionary(result_dict, result_dict_2)
                        merged_dicts_2 = _merge_dicts_with_unique_values(merged_dicts_2)
                        result_dict_2.update(merged_dicts_2)
                else:
                    break
        result_dict.update(result_dict_2)
    # if 1 node
    elif number_of_nodes == 1:
        for idx in property_maps:
            # items() to extract item
            for key, val in idx.items():
                # setdefault performs task of setting empty list value as default
                result_dict[key] = val
    # TODo: if 0 nodes
    else:
        result_dict = property_maps
        print(f'number of nodes = 0')

    # printing result
    print("The constructed dictionary : " + str(result_dict))
    return result_dict


def _combine_nodes_to_copy_or_join(number_of_nodes_a, map_a):
    res = {}
    # nodes n to copy from - combine all values of duplicate property keys (to keep arrays)
    # if n nodes
    if number_of_nodes_a > 1:
        # n nodes
        for i, item in enumerate(map_a):
            fist_dict = i
            second_dict = i + 1
            max = number_of_nodes_a
            if number_of_nodes_a == 2:
                merged_dicts = _mergeDictionary(map_a[fist_dict], map_a[second_dict])
                res = _merge_dicts_with_unique_values(merged_dicts)
            elif number_of_nodes_a > 2:
                if second_dict != max:
                    merged_dicts = _mergeDictionary(map_a[fist_dict], map_a[second_dict])
                    merged_dicts = _merge_dicts_with_unique_values(merged_dicts)
                    res.update(merged_dicts)
                    print(f'merged_dict_unique: {res}')
                else:
                    break
                print(f'merged_dict_unique: {res}')
                # res = dict(ChainMap(*map_a))
                # print(f'res number of nodes >2 {res}')
            # res = res.append(merged_dicts)
            # res.update(item)
    # if 1 node
    elif number_of_nodes_a == 1:
        for idx in map_a:
            # items() to extract item
            for key, val in idx.items():
                # setdefault performs task of setting empty list value as default
                res[key] = val
    # TODo: if 0 nodes
    else:
        res = map_a
        print(f'number of nodes = 0')

    # printing result
    print("The constructed dictionary : " + str(res))
    return res


def _nodes_to_copy_merge_to(number_of_nodes, res, map, unique_values):
    temp = {}
    temp2 = []
    # maps of nodes to copy to
    # if m nodes
    if number_of_nodes > 1:
        print(f' number_of_nodes = {number_of_nodes}, res= map_a {res}, map_b {map}')
        for i, item in enumerate(map):
            fist_dict = i
            second_dict = i + 1
            max = number_of_nodes
            if number_of_nodes == 2:
                # merged_dicts = mergeDictionary(map[fist_dict], map[second_dict])
                merged_dicts = _mergeDictionary(res, map[i])
                if unique_values:
                    merged_dicts = _merge_dicts_with_unique_values(merged_dicts)
                else:
                    pass
                temp2.append(merged_dicts)
                print(f'merged_dict_unique: {temp2}')
            elif number_of_nodes > 2:
                print(f'TEST')
                # if second_dict != max:
                merged_dicts = _mergeDictionary(res, map[i])
                print(f'merged_dicts A: {i}: {merged_dicts}')
                if unique_values:
                    merged_dicts = _merge_dicts_with_unique_values(merged_dicts)
                else:
                    pass
                print(f'merged_dicts B: {merged_dicts}')
                temp2.append(merged_dicts)
                print(f'merged_dict_unique C: {type(temp2)}, {len(temp2)}, {temp2}')

                # else:
                # break
            print(f'merged_dict_unique: {res}')
    # if number_of_nodes_b == 2:
    #     for j in enumerate(map_b):
    #         dict_3 = mergeDictionary(res[0], j[1])
    #         temp.update(dict_3)
    #     print("nodes b 2 or more")
    # if 1 node
    elif number_of_nodes == 1:
        dict_3 = _mergeDictionary(res, map[0])
        temp.update(dict_3)
        print("nodes b = 1")
    # ToDo: if 0 nodes
    else:
        print("nodes b = 0")

    print(f'temp {temp}')
    print(f'temp2 {temp2}')
    return temp, temp2


def _merge_maps_keeping_all_values(number_of_nodes, res, map):
    temp = {}
    temp2 = []
    # maps of nodes to copy to
    # if m nodes
    if number_of_nodes > 1:
        print(f' number_of_nodes = {number_of_nodes}, res= map_a {res}, map_b {map}')
        for i, item in enumerate(map):
            fist_dict = i
            second_dict = i + 1
            max = number_of_nodes
            if number_of_nodes == 2:
                # merged_dicts = mergeDictionary(map[fist_dict], map[second_dict])
                merged_dicts = _mergeDictionary(res, map[i])
                # merged_dicts = merge_dicts_with_unique_values(merged_dicts)
                temp2.append(merged_dicts)
                print(f'merged_dict_unique: {temp2}')
            elif number_of_nodes > 2:
                print(f'TEST')
                # if second_dict != max:
                merged_dicts = _mergeDictionary(res, map[i])
                print(f'merged_dicts A: {i}: {merged_dicts}')
                # ToDo: Warum bei C1, C2 zweimal Lufthansa
                # merged_dicts = merge_dicts_with_unique_values(merged_dicts) -->1x1 see below: dicts are only merged keeping all values!!!
                print(f'merged_dicts B: {merged_dicts}')
                temp2.append(merged_dicts)
                print(f'merged_dict_unique C: {type(temp2)}, {len(temp2)}, {temp2}')

                # else:
                # break
            print(f'merged_dict_unique: {res}')
    # if number_of_nodes_b == 2:
    #     for j in enumerate(map_b):
    #         dict_3 = mergeDictionary(res[0], j[1])
    #         temp.update(dict_3)
    #     print("nodes b 2 or more")
    # if 1 node
    elif number_of_nodes == 1:
        dict_3 = _mergeDictionary(res, map[0])
        temp.update(dict_3)
        print("nodes b = 1")
    # ToDo: if 0 nodes
    else:
        print("nodes b = 0")

    print(f'temp {temp}')
    print(f'temp2 {temp2}')
    return temp, temp2


# temp = nodes_to_copy_merge_to(number_of_nodes_b, res, map_b)

# finds nested values
# https: // stackoverflow.com / questions / 24180879 / python - check - if -a - list - is -nested - or - not
def _is_nested_list(l):
    try:
        next(x for x in l if isinstance(x, list))
    except StopIteration:
        return False
    return True


# ToDo: turn unique_values into list?
def _unique_values_or_duplicates(list):
    unique_values = set()
    duplicates = []
    differences = set()
    differences_list = []

    for x in list:
        if x in unique_values:
            duplicates.append(x)
        else:
            unique_values.add(x)
            differences.add(x)

        # removes duplicates from differences dict
        for duplicate in duplicates:
            if duplicate in differences:
                differences.remove(x)
            else:
                pass

    # handles if dicts are empty
    if len(differences) == 0:
        print(f'-----length O ------')
        differences = []
    elif len(unique_values) == 0:
        unique_values = []
    else:
        pass

    # turns dict into list
    for item in differences:
        differences_list.append(item)

    print(f'!!! unique_values {unique_values}, duplicates {duplicates}, Differences: {differences_list}')

    return unique_values, duplicates, differences_list


def _duplicates_of_nested_lists(dictionary, duplicates_or_unique_values):
    # searches for duplicates in nested lists of array
    print(f'duplicates_or_unique_values {duplicates_or_unique_values}')
    for key, value in dictionary.items():
        if type(value) == list:
            print(f'{key}: {value}')
            if _is_nested_list(value):
                # list is searched for nested objects
                # new_list = [item for sublist in value for item in sublist]
                new_list = list(deepflatten(value, depth=1, types=None, ignore=str))
                # new list is created with unique values only
                unique_values, duplicates, differences = _unique_values_or_duplicates(new_list)
                if duplicates_or_unique_values == "differences":
                    dups_or_unique_values = differences
                    # dictionary[key] = duplicates
                elif duplicates_or_unique_values == "all_values":
                    dups_or_unique_values = unique_values
                    # dictionary[key] = unique_values
                else:
                    dups_or_unique_values = duplicates
                    # dictionary[key] = differences

                # dictionary[key] = duplicates
                dictionary[key] = dups_or_unique_values

                print(f'Duplicates {duplicates}, Unique_values {unique_values}, Differences {differences}')
            else:
                unique_values, duplicates, differences = _unique_values_or_duplicates(value)

                if duplicates_or_unique_values == "differences":
                    dups_or_unique_values = differences
                    # dictionary[key] = duplicates
                elif duplicates_or_unique_values == "all_values":
                    dups_or_unique_values = unique_values
                    # dictionary[key] = unique_values
                else:
                    dups_or_unique_values = duplicates
                    # dictionary[key] = differences

                # dictionary[key] = duplicates
                dictionary[key] = dups_or_unique_values

                print(f'Duplicates {duplicates}, Unique_values {unique_values}, Differences {differences}')
                # print(new_list)
    # print(f'temp with duplicates only: {dictionary}')
    return dictionary


# maps_with_duplicates = duplicates_of_nested_lists(temp)
# print(f'maps_with_duplicates: {maps_with_duplicates}')

def _merge_dicts_with_unique_values(dictionary):
    # combines all values to keys and leaves all unique values in lists
    for key, value in dictionary.items():
        if type(value) == list:
            if _is_nested_list(value):
                # list is searched for nested objects
                # new_list = [item for sublist in value for item in sublist]
                new_list = list(deepflatten(value, depth=1, types=None, ignore=str))
                # new list is created with unique values only
                new_list_unique_values_only = list(set(new_list))
                # sets new list with unique values to key
                dictionary[key] = new_list_unique_values_only
            else:
                # new list is created with unique values only
                new_list_unique_values_only = list(set(value))
                # sets new list with unique values to key
                dictionary[key] = new_list_unique_values_only
                # if len(new_list_unique_values_only) == 1:
                #     print(f' list has only 1 value {new_list_unique_values_only[0]}')
                #     dictionary[key] = new_list_unique_values_only[0]
                # else:
                #     break
                print(new_list_unique_values_only)

    # print(f'temp with unique values only: {dictionary}')
    return dictionary


# merged_dicts_with_unique_values = merge_dicts_with_unique_values(temp)
# print(f'merged_dicts_with_unique_values: {merged_dicts_with_unique_values}')

def _single_dict_with_single_value(dictionary):
    # for key, value in dictionary.items():
    #     if type(value) == list and len(value) == 1:
    #         # value = list(flatten(value))
    #         print(f'value with lenght 1 found: {value}')
    # print(f'value with lenght 1 found: {value}')
    # overwrites key of single value lists with the value it contained
    single_item = next(iter(dictionary))
    print(f'value with lenght 1 found: {single_item}, {dictionary[single_item]}')
    for item in dictionary[single_item]:
        # for item in dictionary:
        # print(f'Item: {item}')
        dictionary[single_item] = item
    print(f'value with lenght 1 found: {single_item}, {dictionary[single_item]}')
    return dictionary


def _list_with_single_value(list_with_dicts):
    for item in list_with_dicts:
        # print(f'Items of temp2: {item}')
        single_item = next(iter(item))
        # print(f'single_items of item of temp2: {single_item}, {item[single_item]}')
        for key, value in item.items():
            # print(f'key, value of item: {key}, {value}')
            if type(value) == list:
                # print("list value")
                if len(value) == 1:
                    item[key] = value[0]
                    # print(f'list has lenght 1, {single_item}')
    return list_with_dicts


def _single_value_or_empty_list_values(dictionary):
    # stores keys of empty list values
    keys_to_delete = []
    # searches for keys with list with single values or empty lists
    for key, value in dictionary.items():
        # single value lists
        if type(value) == list and len(value) == 1:
            dictionary[key] = value[0]
            # print(f'value with length 1 found: {key}: {value[0]}')
        # keys of empty lists
        elif type(value) == list and len(value) == 0:
            keys_to_delete.append(key)
            # print(f'value with length 0 found: {keys_to_delete}')
        else:
            pass

    # deletes all keys with empty lists
    for key in keys_to_delete:
        del dictionary[key]
    # print(f'value with length 0 deleted: {result}')
    return dictionary
