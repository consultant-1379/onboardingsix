from behave import given, then, when, step
from mock import MagicMock, mock, patch
from topologies.system_topologies.nrnsa_topology import NrnsaTopology
from common.nrnsa_cli import NRNSACli
from .mocked_data import MockedCli


@given('there are nodes with relationships')
def step_impl(context):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        MockedCli().mocked_enode_attributes + "\n",
        MockedCli().mocked_gnode_attributes + "\n"
    ])


@given('there are nodes with relationships and unknown plmnid')
def step_impl(context):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        MockedCli().mocked_enode_attributes + "\n",
        MockedCli().mocked_cli_unknown_plmnid + "\n",
        MockedCli().mocked_gnode_attributes_deprecated_enbplmnid + "\n"
    ])


@given('there are nodes with relationships and null plmnid')
def step_impl(context):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        MockedCli().mocked_enode_attributes + "\n",
        MockedCli().mocked_cli_null_plmnid + "\n",
        MockedCli().mocked_gnode_attributes_deprecated_enbplmnid + "\n"
    ])


@when('the script is executed')
@patch('common.nrnsa_export_utils.NRNSAExportUtils.start')
def step_impl(context, mock_export):
    NrnsaTopology().run()


@then('the NR-NSA topology should be created')
def step_impl(context):
    stdout = context.stdout_capture.getvalue()
    assert "NR-NSA Systems Topology has been processed successfully" in stdout


@given('there are nodes with no relationships')
def step_impl(context):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        MockedCli().mocked_enode_attributes_unrelated + "\n",
        MockedCli().mocked_gnode_attributes + "\n"
    ])


@when('the script is executed again')
def step_impl(context):
    NrnsaTopology().run()


@then('the NR-NSA topology should not be created')
def step_impl(context):
    stdout = context.stdout_capture.getvalue()
    assert "NR-NSA topology not created due to missing relationships" in stdout


""" Topology Exists but relationships do not
"""


@given('the NR-NSA topology exists')
def step_impl(context):
    pass


@when('there are no relationships')
@patch('common.nrnsa_export_utils.NRNSAExportUtils.start')
def step_impl(context, mock_export):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        "", "", ""
    ])
    NrnsaTopology().run()


@then('the topology should be deleted')
def step_impl(context):
    stdout = context.stdout_capture.getvalue()
    assert "NR-NSA topology not created due to missing relationships" in stdout
    assert "NR-NSA Systems Topology and Collections deleted successfully" in [
        entry.getMessage() for entry in context.log_capture.buffer]


""" User added collection
"""


@given('the topology exists')
def step_impl(context):
    pass


@when('the script is executed and a user added collection is present')
@patch('common.nrnsa_export_utils.NRNSAExportUtils.start')
def step_impl(context, mock_export):
    with patch(
            'common.collection_utils.CollectionUtils.get_custom_topology') as \
            patched_response:
        patched_response.return_value = {
            "id": "281474979201006",
            "name": "NR-NSA",
            "category": "Public",
            "parentId": None
        }
        NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
            MockedCli().mocked_enode_attributes + "\n",
            MockedCli().mocked_gnode_attributes + "\n"
        ])
        NrnsaTopology().run()


@then('the user added collection should be removed')
def step_impl(context):
    assert "NR-NSA script removed user added Collection 'My test " \
           "collection'" in [
               entry.getMessage() for entry in context.log_capture.buffer]


"""Scheduled updates
"""


@step('the topology exists')
def step_impl(context):
    pass


@step('there are relationships')
def step_impl(context):
    NRNSACli._get_nodes_attributes = MagicMock(side_effect=[
        MockedCli().mocked_enode_attributes + "\n",
        MockedCli().mocked_gnode_attributes + "\n"
    ])


@when('the script executes again')
@patch('common.nrnsa_export_utils.NRNSAExportUtils.start')
def step_impl(context, mock_export):
    with patch(
            'common.collection_utils.CollectionUtils.get_custom_topology') as \
            patched_response:
        patched_response.return_value = {
            "id": "281474979201007",
            "name": "NR-NSA",
            "category": "Public",
            "parentId": None
        }
        NrnsaTopology().run()


@then('it should update the topology')
def step_impl(context):
    assert "NR-NSA Systems Topology has been processed successfully" in \
           context.stdout_capture.getvalue()
    assert "NR-NSA script updated collection: 'LTE18dg2ERBS00154-NR-NSA'" in [
        entry.getMessage() for entry in context.log_capture.buffer]
