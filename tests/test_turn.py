import datetime
import ipaddress
from pydantic import HttpUrl, IPvAnyAddress
import pytest
from unittest.mock import patch, MagicMock

import requests

from marcopolo.utils.data_objects import CertAuth
from marcopolo.attacks.turn import TurnFactory
from requests.exceptions import HTTPError
from marcopolo.attacks.node import Node, NodeRequestError, NodeResponseError
# Throughout this file, there are a lot of things to be patched. This includes:
#   The MPIC_API_KEY environment variable
#   The requests.get() function for listen_polo()
#   The requests.post() function for say_marco()
#
#

# Fixtures for reusable test data
@pytest.fixture
def mock_nodes() -> tuple[Node, Node]:
    mock_node_a = Node(name="mock_node_a", ip=ipaddress.ip_address("1.2.3.4"))
    mock_node_b = Node(name="mock_node_b", ip=ipaddress.ip_address("5.6.7.8"))
    return mock_node_a, mock_node_b

@pytest.fixture
def mock_token()->str:
    return "mock_token"

# Applies patch mocking the mpic api key env var
@pytest.fixture
def patch_mpic_api_key_env_var():
    with patch("marcopolo.src.turn.os.environ", {"MPIC_API_KEY": "mock-api-key"}):
        yield

@pytest.fixture
def patch_time_sleep():
    with patch("time.sleep", return_value=None):
        yield

# Helper function to generate expected requests
def generate_expected_request(ca, mock_token, node_a, node_b):
    base_requests = {
        "om": {
            "url": ca.endpoint,
            "headers": {
                "Content-Type": "application/json",
                "x-api-key": "mock-api-key"
            },
            "json": {
                "orchestration_parameters": {
                    "perspective_count": 13,
                    "max_attempts": 1
                },
                "check_type": "dcv",
                "domain_or_ip_target": "subdomain.arins.pretend-crypto-wallet.com",
                "dcv_check_parameters": {
                    "validation_method": "http-generic",
                    "validation_details": {
                        "http_token_path": mock_token,
                        "challenge_value": "test"
                    }
                }
            },
        },
        "ggp": {
            "url": ca.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "token": mock_token,
                "node_a": node_a.name,
                "node_b": node_b.name,
            },
        },
        "ggf": {
            "url": ca.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "token": mock_token,
                "node_a": node_a.name,
                "node_b": node_b.name,
            },
        },
        "cf": {
            "url": ca.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "method": "acme/http-01",
                "kaHash": "TfPD9o_Mg7J-nULJBDGnJJnxeHXIGlmbVmyYiblpZwM=",
                "token": mock_token,
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "accessToken": "YTrWJscsDU2BJNF_AUaXjg==",
            },
        },
    }
    return base_requests.get(ca.name)

#################### Test Request Generation for each CA ##a##################
#   Patching required: load_config() and the MPIC_API_KEY environment variable
#   Mocking required: Nodes, token

@pytest.mark.parametrize("ca", [
    (CertAuth(name="ggp", endpoint=HttpUrl("http://mock-ggp-url.com"))),
    (CertAuth(name="ggf", endpoint=HttpUrl("http://mock-ggf-url.com"))),
    (CertAuth(name="cf", endpoint=HttpUrl("https://mock-cf-url.com"))),
    (CertAuth(name="om", endpoint=HttpUrl("https://mock-om-url.com")))
])
class TestSample:

    @staticmethod
    def test_valid_http_request_generation(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        # Arrange
        node_a, node_b = mock_nodes
        turn = TurnFactory.create(ca, node_a, node_b)
        expected_request = generate_expected_request(ca, mock_token, node_a, node_b)


        # Act
        actual_request = turn.generate_request(mock_token)
        # Assert
        assert actual_request == expected_request, f"Generated request does not match for CA: {ca}"


#################### Test Say Marco ####################
#@patch ('turn.http_logger.info', return_value=None)
@pytest.mark.usefixtures('patch_time_sleep',            # for retry
                         'patch_mpic_api_key_env_var',   # for MPIC
                         )
@pytest.mark.parametrize("ca", [
    (CertAuth(name="ggp", endpoint=HttpUrl("http://mock-ggp-url.com"))),
    (CertAuth(name="ggf", endpoint=HttpUrl("http://mock-ggf-url.com"))),
    (CertAuth(name="cf", endpoint=HttpUrl("https://mock-cf-url.com"))),
    (CertAuth(name="om", endpoint=HttpUrl("https://mock-om-url.com")))
])
class TestSayMarco:

    @staticmethod
    def test_say_marco_success(mock_nodes, ca):
        """
        Test `say_marco` with a successful HTTP response.
        """
        node_a, node_b = mock_nodes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        
        with patch("requests.post", return_value=mock_response) as mock_post:
            turn = TurnFactory.create(ca, node_a, node_b)
            say_marco_data = turn.say_marco()

            # Ensure a token is generated
            assert isinstance(say_marco_data.token, str)
            assert len(say_marco_data.token) == 21  # Length of the token
            assert say_marco_data.num_tries == 1  # Assuming first attempt is successful
            assert say_marco_data.failed is False  # Ensure the request was successful
            assert say_marco_data.error_message is None  # Ensure no error message is present

            # Verify the POST request is made
            mock_post.assert_called_once()

    @staticmethod
    def test_say_marco_retry(mock_nodes, ca):
        """
        Test `say_marco` retries when the HTTP request fails.
        """
        node_a, node_b = mock_nodes
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError
        mock_response.text = ""
        with patch("requests.post", return_value=mock_response) as mock_post:
            turn = TurnFactory.create(ca, node_a, node_b)
            
            say_marco_data = turn.say_marco()
            
            assert say_marco_data.error_message is not None  # Ensure an error message is present
            assert say_marco_data.num_tries == 5  # Ensure it retried the maximum number of times
            assert say_marco_data.failed is True  # Ensure the request failed
            

            # Verify the POST request was retried 5 times
            assert mock_post.call_count == 5

########################### Test TurnFactory ###########################

class TestTurnFactory:
    @staticmethod
    @pytest.mark.parametrize("ca, subclass", [
        (CertAuth(name="ggp", endpoint=HttpUrl("http://mock-ggp-url.com")), "GGPTurn"),
        (CertAuth(name="ggf", endpoint=HttpUrl("http://mock-ggf-url.com")), "GGFTurn"),
        (CertAuth(name="cf", endpoint=HttpUrl("http://mock-cf-url.com")), "CFTurn"),
        (CertAuth(name="om", endpoint=HttpUrl("http://mock-om-url.com")), "OMTurn"),
        (CertAuth(name="le", endpoint=HttpUrl("http://mock-le-url.com")), "LETurn"),
    ])
    def test_turn_factory_creates_correct_subclass(mock_nodes, ca, subclass):
        """
        Test that TurnFactory returns the correct subclass based on CA name.
        """

        node_a, node_b = mock_nodes
        turn = TurnFactory.create(ca, node_a, node_b)

        # Assert the returned object is an instance of the expected subclass
        assert turn.__class__.__name__ == subclass

    @staticmethod
    def test_turn_factory_unknown_ca(mock_nodes):
        """
        Test TurnFactory raises an error for unknown CA names.
        """
        node_a, node_b = mock_nodes

        with pytest.raises(ValueError, match="Unknown certificate authority: unknown"):
            TurnFactory.create(CertAuth(name="unknown", endpoint=HttpUrl("http://unknown-url.com")), node_a, node_b)
 
#################### Test Listen Polo ####################

@pytest.mark.parametrize("ca", [
    (CertAuth(name="ggp", endpoint=HttpUrl("http://mock-ggp-url.com"))),
    (CertAuth(name="ggf", endpoint=HttpUrl("http://mock-ggf-url.com"))),
    (CertAuth(name="cf", endpoint=HttpUrl("https://mock-cf-url.com"))),
    (CertAuth(name="om", endpoint=HttpUrl("https://mock-om-url.com")))
])
class TestListenPolo: 

    @staticmethod
    def test_listen_polo_success(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        """
        Test `listen_polo` with successful HTTP responses.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {"ip_addresses": ["1.1.1.1", "2.2.2.2"]}

        mock_response_b = MagicMock()
        mock_response_b.status_code = 200
        mock_response_b.json.return_value = {"ip_addresses": ["3.3.3.3"]}

        with patch("requests.get", side_effect=[mock_response_a, mock_response_b]) as mock_get:
            turn = TurnFactory.create(ca, node_a, node_b)
            result = turn.listen_polo(mock_token)

            # Assert IPs are returned correctly
            assert result.node_a_perspectives == [ipaddress.ip_address("1.1.1.1"), ipaddress.ip_address("2.2.2.2")]
            assert result.node_b_perspectives == [ipaddress.ip_address("3.3.3.3")]

            # Verify GET requests are made to both nodes
            assert mock_get.call_count == 2
    
    @staticmethod
    def test_listen_polo_failure_node_a_request_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        """
        Test `listen_polo` when the request to node A fails.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 500
        mock_response_a.raise_for_status.side_effect = HTTPError()
        
        for side_effect in [None, ConnectionError, requests.Timeout]:
            mock_response_a.side_effect = side_effect
            with patch("requests.get", side_effect=[mock_response_a] ) as mock_get:
                turn = TurnFactory.create(ca, node_a, node_b)

                # Call listen_polo and capture the result
                result = turn.listen_polo(mock_token)

                # Assert that the result is a ListenPoloData object with expected values
                assert result.token == mock_token
                assert result.node_a == node_a
                assert result.node_b == node_b
                assert result.node_a_perspectives == []
                assert result.node_b_perspectives == []
                assert result.failed is True
                assert result.error_message is not None
                assert mock_get.call_count == 1

    @staticmethod
    def test_listen_polo_failure_node_b_request_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        """
        Test `listen_polo` when the request to node B fails.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {"ip_addresses": ["1.1.1.1", "2.2.2.2"]}

        mock_response_b = MagicMock()
        mock_response_b.status_code = 500
        mock_response_b.raise_for_status.side_effect = HTTPError()

        for error in [None, ConnectionError, requests.Timeout]:
            mock_response_b.side_effect = error
            with patch("requests.get", side_effect=[mock_response_a, mock_response_b]) as mock_get:
                turn = TurnFactory.create(ca, node_a, node_b)

                # Call listen_polo and capture the result
                result = turn.listen_polo(mock_token)

                # Assert that the result is a ListenPoloData object with expected values
                assert result.token == mock_token
                assert result.node_a == node_a
                assert result.node_b == node_b
                assert result.node_a_perspectives == []
                assert result.node_b_perspectives == []
                assert result.failed is True
                assert result.error_message is not None
                assert mock_get.call_count == 2
    @staticmethod
    def test_listen_polo_failure_node_a_key_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        """
        Test `listen_polo` when the response from node A does not contain 'ip_addresses'.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {}

        with patch("requests.get", side_effect=[mock_response_a]) as mock_get:
            turn = TurnFactory.create(ca, node_a, node_b)

            # Call listen_polo and capture the result
            result = turn.listen_polo(mock_token)

            # Assert that the result is a ListenPoloData object with expected values
            assert result.token == mock_token
            assert result.node_a == node_a
            assert result.node_b == node_b
            assert result.node_a_perspectives == []
            assert result.node_b_perspectives == []
            assert result.failed is True
            assert result.error_message == f"'ip_addresses' field missing in response from {node_a.name}"

            assert mock_get.call_count == 1

    @staticmethod
    def test_listen_polo_failure_node_b_key_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        """
        Test `listen_polo` when the response from node B does not contain 'ip_addresses'.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {"ip_addresses": ["1.1.1.1", "2.2.2.2"]}

        mock_response_b = MagicMock()
        mock_response_b.status_code = 200
        mock_response_b.json.return_value = {}

        with patch("requests.get", side_effect=[mock_response_a, mock_response_b]) as mock_get:
            turn = TurnFactory.create(ca, node_a, node_b)

            # Call listen_polo and capture the result
            result = turn.listen_polo(mock_token)

            # Assert that the result is a ListenPoloData object with expected values
            assert result.token == mock_token
            assert result.node_a == node_a
            assert result.node_b == node_b
            assert result.node_a_perspectives == []
            assert result.node_b_perspectives == []
            assert result.failed is True
            assert result.error_message == f"'ip_addresses' field missing in response from {node_b.name}"

            assert mock_get.call_count == 2

##################### Test Execute #########################

@pytest.mark.parametrize("ca", [
    (CertAuth(name="ggp", endpoint=HttpUrl("http://mock-ggp-url.com"))),
    (CertAuth(name="ggf", endpoint=HttpUrl("http://mock-ggf-url.com"))),
    (CertAuth(name="cf", endpoint=HttpUrl("https://mock-cf-url.com"))),
    (CertAuth(name="om", endpoint=HttpUrl("https://mock-om-url.com")))
])
class TestExecute:

    @staticmethod
    def test_execute_failure_say_marco(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca):
        node_a, node_b = mock_nodes

        # Create a mock failed SayMarcoData object
        failed_say_marco_data = MagicMock()
        failed_say_marco_data.token = None
        failed_say_marco_data.num_tries = 5
        failed_say_marco_data.failed = True
        failed_say_marco_data.error_message = "Mocked failure"

        with patch("marcopolo.src.turn.Turn.say_marco", return_value=failed_say_marco_data) as mock_say_marco:
            from marcopolo.attacks.turn import TurnFactory
            turn = TurnFactory.create(ca, node_a, node_b)
            result = turn.execute()
            assert result.ca.name == ca.name
            assert result.ca.endpoint == ca.endpoint
            assert result.node_a.name == node_a.name  # Fixed attribute access
            assert result.node_a.ip == node_a.ip      # Fixed attribute access
            assert result.node_b.name == node_b.name  # Fixed attribute access
            assert result.node_b.ip == node_b.ip      # Fixed attribute access
            assert isinstance(result.start_time, datetime.datetime)
            assert isinstance(result.end_time, datetime.datetime)
            assert result.say_marco_data and result.say_marco_data.failed is True  # Fixed attribute access
            assert result.listen_polo_data is None
        


        


