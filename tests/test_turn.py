import pytest
from unittest.mock import patch, MagicMock
from turn import TurnFactory
from requests.exceptions import HTTPError
from utils.node import Node, NodeRequestError, NodeResponseError
# Throughout this file, there are a lot of things to be patched. This includes:
#   The MPIC_API_KEY environment variable
#   The requests.get() function for listen_polo()
#   The requests.post() function for say_marco()
#
#

# Fixtures for reusable test data
@pytest.fixture
def mock_nodes():
    mock_node_a = Node(name="mock_node_a", ip="1.2.3.4")
    mock_node_b = Node(name="mock_node_b", ip="5.6.7.8")
    return mock_node_a, mock_node_b

@pytest.fixture
def mock_token():
    return "mock_token"

# Applies patch mocking the mpic api key env var
@pytest.fixture
def patch_mpic_api_key_env_var():
    with patch("turn.os.environ", {"MPIC_API_KEY": "mock-api-key"}):
        yield

@pytest.fixture
def patch_time_sleep():
    with patch("time.sleep", return_value=None):
        yield

# Helper function to generate expected requests
def generate_expected_request(ca_name, endpoint, mock_token, node_a, node_b):
    base_requests = {
        "om": {
            "url": endpoint,
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
            "url": endpoint,
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
            "url": endpoint,
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
            "url": endpoint,
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
    return base_requests.get(ca_name, None)

#################### Test Request Generation for each CA ##a##################
#   Patching required: load_config() and the MPIC_API_KEY environment variable
#   Mocking required: Nodes, token


@pytest.mark.parametrize("ca_name, endpoint", [
    ("ggp", "http://mock-ggp-url.com"),
    ("ggf", "http://mock-ggf-url.com"),
    ("cf", "https://mock-cf-url.com"),
    ("om", "https://mock-om-url.com")
])
class TestSample:

    @staticmethod
    def test_valid_http_request_generation(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
        # Arrange
        node_a, node_b = mock_nodes
        turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)
        expected_request = generate_expected_request(ca_name, endpoint, mock_token, node_a, node_b)


        # Act
        actual_request = turn.generate_request(mock_token)
        # Assert
        assert actual_request == expected_request, f"Generated request does not match for CA: {ca_name}"


#################### Test Say Marco ####################
#@patch ('turn.http_logger.info', return_value=None)
@pytest.mark.usefixtures('patch_time_sleep',            # for retry
                         'patch_mpic_api_key_env_var',   # for MPIC
                         )
@pytest.mark.parametrize("ca_name, endpoint", [
        ("ggp", "http://mock-ggp-url.com"),
        ("ggf", "http://mock-ggf-url.com"),
        ("cf", "https://mock-cf-url.com"),
        ("om", "https://mock-om-url.com")
])
class TestSayMarco:

    @staticmethod
    def test_say_marco_success(mock_nodes, ca_name, endpoint):
        """
        Test `say_marco` with a successful HTTP response.
        """
        node_a, node_b = mock_nodes
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch("requests.post", return_value=mock_response) as mock_post:
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)
            token, attempt_num = turn.say_marco()
 
            # Ensure a token is generated
            assert token is not None
            assert len(token) == 21  # Length of the token
            assert isinstance(token, str)
            assert attempt_num == 0 

            # Verify the POST request is made
            mock_post.assert_called_once()

    @staticmethod
    def test_say_marco_retry(mock_nodes, ca_name, endpoint):
        """
        Test `say_marco` retries when the HTTP request fails.
        """
        node_a, node_b = mock_nodes
        mock_response = MagicMock()
        mock_response.status_code = 500
        with patch("requests.post", return_value=mock_response) as mock_post:
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)
            
            with pytest.raises(Exception):  # Replace SomeExpectedException with the actual exception
                turn.say_marco()

            # Verify the POST request was retried 5 times
            assert mock_post.call_count == 5

########################### Test TurnFactory ###########################

class TestTurnFactory:
    @staticmethod
    @pytest.mark.parametrize("ca_name, endpoint, subclass", [
        ("ggp", "http://mock-ggp-url.com", "GGPTurn"),
        ("ggf", "http://mock-ggf-url.com", "GGFTurn"),
        ("cf", "http://mock-cf-url.com","CFTurn"),
        ("om", "http://mock-om-url.com", "OMTurn"),
        ("le", "http://mock-le-url.com", "LETurn"),
    ])
    def test_turn_factory_creates_correct_subclass(mock_nodes, ca_name, endpoint, subclass):
        """
        Test that TurnFactory returns the correct subclass based on CA name.
        """
        from turn import TurnFactory
        node_a, node_b = mock_nodes
        turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)

        # Assert the returned object is an instance of the expected subclass
        assert turn.__class__.__name__ == subclass

    @staticmethod
    def test_turn_factory_unknown_ca(mock_nodes):
        """
        Test TurnFactory raises an error for unknown CA names.
        """
        from turn import TurnFactory
        node_a, node_b = mock_nodes

        with pytest.raises(ValueError, match="Unknown certificate authority: unknown"):
            TurnFactory.create("unknown", "unknown", node_a, node_b)
 
#################### Test Listen Polo ####################

@pytest.mark.parametrize("ca_name, endpoint", [
    ("ggp", "http://mock-ggp-url.com"),
    ("ggf", "http://mock-ggf-url.com"),
    ("cf", "https://mock-cf-url.com"),
    ("om", "https://mock-om-url.com")
])
class TestListenPolo: 

    @staticmethod
    def test_listen_polo_success(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
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
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)
            ips_a, ips_b = turn.listen_polo(mock_token)

            # Assert IPs are returned correctly
            assert ips_a == ["1.1.1.1", "2.2.2.2"]
            assert ips_b == ["3.3.3.3"]

            # Verify GET requests are made to both nodes
            assert mock_get.call_count == 2
    
    @staticmethod
    def test_listen_polo_failure_node_a_request_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
        """
        Test `listen_polo` when the request to node A fails.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 500
        mock_response_a.raise_for_status.side_effect = HTTPError

        mock_response_b = MagicMock()
        mock_response_b.status_code = 200
        mock_response_b.json.return_value = {"ip_addresses": ["3.3.3.3"]}

        with patch("requests.get", side_effect=[mock_response_a]) as mock_get:
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)

            # Assert exception is raised for the first node
            with pytest.raises(NodeRequestError) as excinfo:
                turn.listen_polo(mock_token)

            assert mock_get.call_count == 1

    @staticmethod
    def test_listen_polo_failure_node_b_request_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
        """
        Test `listen_polo` when the request to node B fails.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {"ip_addresses": ["1.1.1.1", "2.2.2.2"]}

        mock_response_b = MagicMock()
        mock_response_b.status_code = 500
        mock_response_b.raise_for_status.side_effect = HTTPError

        # 'side_effect' allows us to return different values for each call
        with patch("requests.get", side_effect=[mock_response_a, mock_response_b]) as mock_get:
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)

            # Assert exception is raised for the second node
            with pytest.raises(NodeRequestError) as excinfo:
                turn.listen_polo(mock_token)

            assert mock_get.call_count == 2
 
    @staticmethod
    def test_listen_polo_failure_node_a_key_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
        """
        Test `listen_polo` when the response from node A does not contain 'ip_addresses'.
        """
        node_a, node_b = mock_nodes
        mock_response_a = MagicMock()
        mock_response_a.status_code = 200
        mock_response_a.json.return_value = {}

        with patch("requests.get", side_effect=[mock_response_a]) as mock_get:
            turn = TurnFactory.create(ca_name, endpoint,  node_a, node_b)

            # Assert exception is raised for the first node
            with pytest.raises(NodeResponseError) as excinfo:
                turn.listen_polo(mock_token)

            assert mock_get.call_count == 1

    @staticmethod
    def test_listen_polo_failure_node_b_key_error(patch_mpic_api_key_env_var, mock_nodes, mock_token, ca_name, endpoint):
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
            turn = TurnFactory.create(ca_name, endpoint, node_a, node_b)

            # Assert exception is raised for the second node
            with pytest.raises(NodeResponseError) as excinfo:
                turn.listen_polo(mock_token)

            assert mock_get.call_count == 2

###############################################


