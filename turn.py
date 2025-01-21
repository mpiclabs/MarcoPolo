#
# Author: Ari Brown
# 
# A Turn object represents a single turn of Marco-Polo, unique to the certificate authority 
# and node pair. It has a lifecycle consisting of one say_marco and one listen_polo, at which 
# point it has fulfilled its function and should not be reused. It is associated with a single
# token, which is used to identify any communications associated with that turn (most 
# importantly VP requests). 
# 
# say_marco-- triggers a certificate request and saves the secret generated, to use in listen_polo.
#             
# listen_polo-- takes in that token and returns the distribution of VP's between the two nodes. 
# 
# Under the hood, Turn is actually a base class, with a subclass for each certificate authority
# to allow for different implementations (ex. different HTTP cert requests).
# TurnFactory takes the CA and node pair, and initializes the appropriate subclass with the node
# pair, returning the result. If a new CA needs to be accomodated, two modifications are necessary: 
# 1) a subclass needs to be created that results in the same behavior as say_marco and listen_polo,
# through some combination of new and reused methods
# 2) TurnFactory must be updated to return that subclass when given it's 2-letter code
# 
# A Turn object stores the CA name and node pair for which it is a turn-- these are ultimately 
# included in the request.
#
# Coupling/Dependencies-- This module loads the config file directly. It also hardcodes the CA request format.
#                         If either of these change format, this module will not work.
import os
import requests
import datetime
import time
import random
import string
import subprocess
from abc import ABC, abstractmethod
import json
from utils.node import Node, NodeResponseError, NodeRequestError
from utils.loaders import load_config
from utils.loggers import http_logger, error_logger, general_logger

dir_path = os.path.dirname(os.path.realpath(__file__))


# Factory function to initialize the appropriate subclass
class TurnFactory:
    @staticmethod
    def create(ca_name, ca_endpoint, node_a: Node, node_b: Node):
        ca_name = ca_name.lower()
        if ca_name == "ggf":
            return GGFTurn(ca_endpoint, node_a, node_b)
        elif ca_name == "ggp":
            return GGPTurn(ca_endpoint, node_a, node_b)
        elif ca_name == "om":
            return OMTurn(ca_endpoint, node_a, node_b)
        elif ca_name == "cf":
            return CFTurn(ca_endpoint, node_a, node_b)
        elif ca_name=="le":
            return LETurn(ca_endpoint, node_a, node_b)
        else:
            raise ValueError(f"Unknown certificate authority: {ca_name}")

class Turn(ABC):
    def __init__(self, ca_endpoint, node_a: Node, node_b: Node):
        self.node_a = node_a
        self.node_b = node_b
        self.endpoint = ca_endpoint

    @abstractmethod
    def generate_request(self, token):
        pass

    # This function uses the token to identify VP requests associated with this Turn.
    # Specifically, it requests from each node the set of IP addresses that contacted it
    # using the given token.
    def listen_polo(self, token):
        """
        Retrieves IP addresses from two nodes using the provided token.
        Args:
            token (str): The token used for authentication in the requests.
        Returns:
            tuple: A tuple containing two lists of IP addresses. The first list contains IP addresses from node A, 
                   and the second list contains IP addresses from node B.
        Raises:
            NodeRequestError: If there is an error making a request to either node.
            NodeResponseError: If the response from either node does not contain the expected 'ip_addresses' attribute.
        """
        node_a_ips = []
        node_b_ips = []
        try:
            response = requests.get(f"http://{self.node_a.ip}/getips?token={token}")
            response.raise_for_status()
            node_a_ips = response.json()['ip_addresses']
        except requests.exceptions.RequestException as e:
            raise NodeRequestError(f"Error making request to {self.node_a.name} ({self.node_a.ip}): {e}")
        except KeyError as e:
            raise NodeResponseError(f"Error: {self.node_a.name} ({self.node_a.ip}) has no attribute 'ip_addresses'", e)

        try:
            response = requests.get(f"http://{self.node_b.ip}/getips?token={token}")
            response.raise_for_status()
            node_b_ips = response.json()['ip_addresses']
        except requests.exceptions.RequestException as e:
            raise NodeRequestError(f"Error making request to {self.node_b.name} ({self.node_b.ip}): {e}")
        except KeyError as e:
            raise NodeResponseError(f"Error: {self.node_b.name} ({self.node_b.ip}) has no attribute 'ip_addresses'", e)
            

        return node_a_ips, node_b_ips

    # Get a successful request and returns the corresponding 
    def say_marco(self):
        retries = 5
        for attempt in range(retries):
            response, token = self._single_request()
            if response.status_code == 200:
                return token
            elif attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed with status code {response.status_code}. Waiting 10 seconds and retrying...")
                time.sleep(10)
            else:
                # log error
                error_logger.info(f"{self.node_a.name},{self.node_b.name}:\tHTTP Error: Failed after {retries} attempts with final status code {response.status_code}")
    
    def _single_request(self):
        # Create a random token to identify the cert-request
        # Note: ClourFlare requires a 21 character token, or it'll respond with a 400-- "Not enough entropy in token"
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=21)) 

        # Returns a request with the token embedded in it
        cert_req =self.generate_request(token)
        response = requests.post(**cert_req)

        # Log request and response (but filter out the long list of VP's returned by the open_mpic implemenation)
        http_logger.info(cert_req)
        filtered_response = {key: value for key, value in response.json().items() if key != 'perspectives'} 
        http_logger.info(filtered_response)
        
        return response, token
        


class OMTurn(Turn):
    def __init__(self, node_a: Node, node_b: Node, ca_endpoint: str):
        super().__init__(node_a, node_b, ca_endpoint)
        self.ca_name = "ggp"

    def generate_request(self, token):
        return {
            "url": self.endpoint,
            "headers": {
            "Content-Type": "application/json",
            "x-api-key": os.getenv('MPIC_API_KEY', 'not_set')
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
                        "http_token_path": token,
                        "challenge_value": "test"
                    }
            }
            }
        }

class GGFTurn(Turn):
    def __init__(self, node_a: Node, node_b: Node, ca_endpoint: str):
        super().__init__(node_a, node_b, ca_endpoint)
        self.ca_name = "ggp"

    def generate_request(self, token):
        return {
            "url": self.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "token": token,
                "node_a": self.node_a.name,
                "node_b": self.node_b.name,
            }
        }

class GGPTurn(Turn):
    def __init__(self, node_a: Node, node_b: Node, ca_endpoint: str):
        super().__init__(node_a, node_b, ca_endpoint)
        self.ca_name = "ggp"

    def generate_request(self, token):
        return {
            "url": self.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "token": token,
                "node_a": self.node_a.name,
                "node_b": self.node_b.name,
            }
        }

class CFTurn(Turn):
    def __init__(self, node_a: Node, node_b: Node, ca_endpoint: str):
        super().__init__(node_a, node_b, ca_endpoint)
        self.ca_name = "cf"

    def generate_request(self, token):
        return {
            "url": self.endpoint,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": {
                "method": "acme/http-01",
                "kaHash": "TfPD9o_Mg7J-nULJBDGnJJnxeHXIGlmbVmyYiblpZwM=",
                "token": token,
                "domain": "subdomain.arins.pretend-crypto-wallet.com",
                "accessToken": "YTrWJscsDU2BJNF_AUaXjg=="
            }
        }
    

# Let's Encrypt uses certbot to send certificate requests, so say_marco is completely different.
# It must trigger a certbot process, and requires custom hook scripts to manage the token used. 
# Certbot uses a preflight request, so 
class LETurn(Turn):
    def __init__(self, node_a: Node, node_b: Node, ca_endpoint: str):
        super().__init__(node_a, node_b, ca_endpoint)
        self.ca_name = "le"

    def generate_request():
        return
    def say_marco(self):
        certbot_tools = os.path.expanduser("~/certbot_tools")
        # manual-- needed because cerbot isn't being run on the target webserver (can't place token automatically)
        # auth-hook-- writes token to file, allowing us to read it, and validation string  to file, passing the 
        # preflight request (otherwise the others won't succeed)
        # cleanup-hook-- deletes token file
        subprocess.run([
            "certbot",
            "certonly",
            "--manual",     # allows us to run custom scripts
            "--manual-auth-hook", f"{certbot_tools}/authenticator.sh",  # writes token to file, allowing us to read it, and validation string  to file, passing the preflight request (without which secondary VP's would be triggered)
            "--manual-cleanup-hook", f"{certbot_tools}/cleanup.sh",
            "--dry-run",
            "-d", "sajghfgfhsdfasdf.arins.pretend-crypto-wallet.com"
        ])
        with open(f"{certbot_tools}/token", "r") as file:
            return file.read().strip()

if __name__=="__main__":
    turn = TurnFactory.create("ggp", Node("node_a", "1"), Node("node_b", "1"))
    turn.generate_request("bleh")
