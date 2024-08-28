Feature: System Defined Standard Collections

    Scenario Outline: The system contains <nodes>
        Given there are <nodes> in the system and <key> is passed
        When  <collection name> collection doesnt exist
        Then  <collection name> collection should be created
        When  <collection name> collection does exist
        Then  <collection name> collection should be updated

        Examples: Collections
            | collection name | nodes         | key      |
            | LTE-RadioNode   | RadioNodes    | radioLTE |
            | NR-RadioNode    | NR-RadioNodes | radioNR  |
            | LTE-ERBS        | ERBS Nodes    | erbs     |

    Scenario Outline: The System does not contain <nodes>
        Given the system does not contain <nodes> and <key> is passed
        When <collection name> collection does not exist
        Then the script should not create the <collection name> collection
        When <collection_name> collection does exist and no nodes
        Then <collection name> collection should be deleted

        Examples: Collections
            | collection name | nodes         | key      |
            | LTE-RadioNode   | RadioNodes    | radioLTE |
            | NR-RadioNode    | NR-RadioNodes | radioNR  |
            | LTE-ERBS        | ERBS Nodes    | erbs     |

    Scenario Outline: A user created <collection name> collection exists
        Given <nodes> are in the system and a collection with the name <collection name> exists and <key> is passed
        When the script attempts to create the system defined <collection name> collection
        Then the non system created collection <collection name> should be deleted
        And  <collection name> collection should be created
        Then the <collection name> should be updated

        Examples: Collections
            | collection name | nodes         | key      |
            | LTE-RadioNode   | RadioNodes    | radioLTE |
            | NR-RadioNode    | NR-RadioNodes | radioNR  |
            | LTE-ERBS        | ERBS Nodes    | erbs     |
