from datetime import datetime as datetime
import ipaddress
import time
from pydantic import IPvAnyAddress
import pytest
from unittest.mock import patch, MagicMock, mock_open
from marcopolo.attacks.round import Round
from marcopolo.attacks.node import Node
from marcopolo.utils.data_objects import CertAuth, ListenPoloData, SayMarcoData, TurnData, RoundData

@pytest.fixture
def mock_nodes():
    node_a = MagicMock(spec=Node)
    node_a.name = "node-a"
    node_a.ip = "1.1.1.1"

    node_b = MagicMock(spec=Node)
    node_b.name = "node-b"
    node_b.ip = "2.2.2.2"

    return node_a, node_b

@pytest.fixture
def mock_cas():
    ca_a = MagicMock(spec=CertAuth)
    ca_a.name = "mock-ca-a"
    ca_a.url = "http://mock-ca-a.com"

    ca_b = MagicMock(spec=CertAuth)
    ca_b.name = "mock-ca-b"
    ca_b.url = "http://mock-ca-b.com"

    return [ca_a, ca_b]
@patch("marcopolo.src.round.time.sleep", return_value=None)
@patch("marcopolo.src.round.pathfinder")
# @patch("marcopolo.src.round.open", new_callable=mock_open)
@patch("marcopolo.src.round.TurnFactory")
def test_round_execute_success(mock_turn_factory, mock_open_file, mock_pathfinder, mock_nodes, mock_cas):
    mock_node_a, mock_node_b = mock_nodes
    mock_ca_a, mock_ca_b = mock_cas  # Unpack the mock CAS here


    # Mock two successful TurnData objects
    mock_turn = MagicMock()
    mock_turn_data_1 = TurnData(
        ca=mock_ca_a,
        node_a=mock_node_a,
        node_b=mock_node_b,
        start_time=datetime.now(),
        end_time=datetime.now(),
        say_marco_data=SayMarcoData(
            token="mock-token",
            num_tries=1,
            failed=False,
            error_message=None
        ),
        listen_polo_data=ListenPoloData(
            token="mock-token",
            node_a=mock_node_a,
            node_b=mock_node_b,
            node_a_perspectives=[ipaddress.ip_address("1.1.1.1")],
            node_b_perspectives=[ipaddress.ip_address("2.2.2.2")],
            error_message=None,
            failed=False
        ),
        error=None
    )
    mock_turn_data_2 = TurnData(
        ca=mock_ca_b,
        node_a=mock_node_a,
        node_b=mock_node_b,
        start_time=datetime.now(),
        end_time=datetime.now(),
        say_marco_data=SayMarcoData(
            token="mock-token-2",
            num_tries=1,
            failed=False,
            error_message=None
        ),
        listen_polo_data=ListenPoloData(
            token="mock-token-2",
            node_a=mock_node_a,
            node_b=mock_node_b,
            node_a_perspectives=[ipaddress.ip_address("3.3.3.3")],
            node_b_perspectives=[ipaddress.ip_address("4.4.4.4")],
            error_message=None,
            failed=False
        ),
        error=None
    )
    bgp_prefix= "1.2.3.4/32"

    mock_turn.execute.side_effect = [mock_turn_data_1, mock_turn_data_2]
    mock_turn_factory.create.return_value = mock_turn

    round_instance = Round(cas=[mock_ca_a, mock_ca_b], bgp_prefix=bgp_prefix, node_a=mock_node_a, node_b=mock_node_b)
    round_data = round_instance.execute()

    # Assert pathfinder was called once
    assert mock_pathfinder.call_count == 1

    # Assert TurnFactory used correctly
    mock_turn_factory.create.assert_called_once_with("mock-ca", "http://mock-endpoint.com", mock_node_a, mock_node_b)
    mock_turn.execute.assert_called_once()

    # Assert round data is populated
    assert isinstance(round_data, RoundData)
    assert round_data.node_a.name == mock_node_a.name
    assert round_data.node_b.name == mock_node_b.name
    assert len(round_data.turns) == 2
    assert round_data.turns[0].ca == mock_ca_a
    assert round_data.turns[1].ca == mock_ca_b
