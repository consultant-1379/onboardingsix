Feature: Executing NR-NSA

    Scenario: All conditions are valid
        Given there are nodes with relationships
        When the script is executed
        Then the NR-NSA topology should be created

    Scenario: Nodes having unknown pLMNId created using deprecated eNBPlmnId
        Given there are nodes with relationships and unknown plmnid
        When the script is executed
        Then the NR-NSA topology should be created

    Scenario: Nodes having null pLMNId created using deprecated eNBPlmnId
        Given there are nodes with relationships and null plmnid
        When the script is executed
        Then the NR-NSA topology should be created

    Scenario: Nodes exist, but relationships do not
        Given there are nodes with no relationships
        When the script is executed again
        Then the NR-NSA topology should not be created

    Scenario: Topology Exists but relationships do not
        Given the NR-NSA topology exists
        When there are no relationships
        Then the topology should be deleted

    Scenario: User added collection in the Topology
        Given the Topology exists
        When the script is executed and a user added collection is present
        Then the user added collection should be removed

    Scenario: Scheduled update of the Topology
        Given the topology exists
        And there are relationships
        When the script executes again
        Then it should update the Topology