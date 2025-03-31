import pytest
from unittest.mock import patch, MagicMock, mock_open
from ..src.round import Round
from ..src.utils.node import Node
from ..src.utils.data_objects import TurnData, RoundData

@pytest.fixture
def mock_nodes():
    node_a = MagicMock(spec=Node)
    node_a.name = "node-a"
    node_a.ip = "1.1.1.1"

    node_b = MagicMock(spec=Node)
    node_b.name = "node-b"
    node_b.ip = "2.2.2.2"

    return node_a, node_b

@patch("marcopolo.src.round.time.sleep", return_value=None)
@patch("marcopolo.src.round.pathfinder")
@patch("marcopolo.src.round.open", new_callable=mock_open)
@patch("marcopolo.src.round.TurnFactory")
def test_round_execute_success(mock_turn_factory, mock_open_file, mock_pathfinder, mock_sleep, mock_nodes):
    node_a, node_b = mock_nodes

    ca_names = ["mock-ca"]
    ca_endpoints = ["http://mock-endpoint.com"]
    ip_address = "3.3.3.3"

    # Mock a successful TurnData object
    mock_turn = MagicMock()
    mock_turn_data = TurnData(
        ca_name="mock-ca",
        ca_endpoint="http://mock-endpoint.com",
        node_a_name="node-a",
        node_a_ip="1.1.1.1",
        node_b_name="node-b",
        node_b_ip="2.2.2.2",
        start_time=None
    )
    mock_turn.execute.return_value = mock_turn_data
    mock_turn_factory.create.return_value = mock_turn

    round_instance = Round(ca_names, ca_endpoints, ip_address, node_a, node_b)
    round_data = round_instance.execute()

    # Assert pathfinder was called twice
    assert mock_pathfinder.call_count == 2

    # Assert file write occurred
    mock_open_file.assert_called_once()
    mock_open_file().write.assert_called_once_with("node-a, node-b:\n")

    # Assert TurnFactory used correctly
    mock_turn_factory.create.assert_called_once_with("mock-ca", "http://mock-endpoint.com", node_a, node_b)
    mock_turn.execute.assert_called_once()

    # Assert round data is populated
    assert isinstance(round_data, RoundData)
    assert round_data.node_a_name == "node-a"
    assert len(round_data.turns) == 1
    assert round_data.turns[0].ca_name == "mock-ca"
