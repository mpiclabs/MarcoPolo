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
# A Turn object stores the CA name, endpoint, and node pair for which it is a turn-- these are ultimately 
# included in the request.
#
# Coupling/Dependencies-- This module hardcodes the CA request format. If this changes format, 
#                         this module will not work.

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
from utils.data_objects import TurnData

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
    def __init__(self, ca_name, ca_endpoint, node_a: Node, node_b: Node):
        self.node_a = node_a
        self.node_b = node_b
        self.endpoint = ca_endpoint
        self.ca_name = ca_name

    @abstractmethod
    def generate_request(self, token):
        pass

    def execute(self):
        result = TurnData(  ca = self.ca_name, 
                            node_a_name = self.node_a.name,
                            node_a_ip = self.node_a.ip,
                            node_b_name = self.node_b.name,
                            node_b_ip = self.node_b.ip,
                            start_time = datetime.datetime.now())
        
        try:
            result.token, result.marco_num_tries = self.say_marco()
            result.marco_succeeded = True        
        except Exception as e:
            result.errors.append(f"Error in say_marco: {e}")
            result.marco_succeeded = False
            result.end_time = datetime.datetime.now()
            return result
        
        try: 
            result.polo_results_node_a, result.polo_results_node_b = self.listen_polo(result.token)
            result.listen_polo_succeeded = True
        except Exception as e:
            result.errors.append(f"Error in listen_polo: {e}")
            result.listen_polo_succeeded = False
            result.end_time = datetime.datetime.now()
            return result
        
        result.end_time = datetime.datetime.now()
        return result

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
            NodeResponseError: If there is an error parsing the response from either node.
        """
        results = []
        for node in [self.node_a, self.node_b]:
            try:
                response = requests.get(f"http://{node.ip}/getips?token={token}")
                response.raise_for_status()
                results.append(response.json()['ip_addresses'])
            except requests.exceptions.RequestException as e:
                raise NodeRequestError(f"Error making request to {node.name} ({node.ip}): {e}")
            except KeyError as e:
                raise NodeResponseError(f"Error parsing response from {node.name} ({node.ip}):", e)
        return tuple(results)

    def say_marco(self):
        """
        Attempts to perform a request up to a specified number of retries.

        This method will attempt to perform the defined cert request up to 5 times. If the request is successful
        (i.e., the response status code is 200), it returns True, the token, and the attempt number.
        If all attempts fail, it raises an exception.

        Returns:
            tuple: A tuple containing:
                - bool: True if the request was successful, otherwise False.
                - str: The token received from the request.
                - int: The number of attempts made.
        """
        retries = 5
        response = None
        for attempt_num in range(retries):
            response, token = self._single_request()
            if response.status_code == 200:
                return token, attempt_num
            else:
                print(f"Attempt {attempt_num} failed with status code {response.status_code}. Waiting 10 seconds and retrying...")
                time.sleep(10)
        # log error
        error_logger.info(f"{self.node_a.name},{self.node_b.name}:\tHTTP Error: Failed after {retries} attempts with final status code {response.status_code}")
        raise Exception(f"say_marco failed after {retries} attempts, with status code {response.status_code}")


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
    def __init__(self, ca_endpoint: str, node_a: Node, node_b: Node):
        super().__init__("om", ca_endpoint, node_a, node_b)

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
    def __init__(self, ca_endpoint: str, node_a: Node, node_b: Node):
        super().__init__("ggp", ca_endpoint, node_a, node_b)


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
    def __init__(self, ca_endpoint: str, node_a: Node, node_b: Node):
        super().__init__("ggp", ca_endpoint, node_a, node_b)

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
    def __init__(self, ca_endpoint: str, node_a: Node, node_b: Node):
        super().__init__("cf", ca_endpoint, node_a, node_b)

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
    def __init__(self, ca_endpoint: str, node_a: Node, node_b: Node):
        super().__init__("le", ca_endpoint, node_a, node_b)

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
    turn = TurnFactory.create("ggp", "endpoint", Node("node_a", "1"), Node("node_b", "2"))
    turn.generate_request("bleh")
