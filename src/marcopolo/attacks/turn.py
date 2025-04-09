#
# Author: Ari Brown
# 
# A Turn object represents a single turn of Marco-Polo, unique to the certificate authority and node pair. It has a lifecycle consisting of one say_marco and one listen_polo, at which point it has fulfilled its function and should not be reused. It is associated with a single token, which is used to identify any communications associated with that turn (most importantly VP requests). 
# 
# say_marco-- triggers a certificate request and saves the secret generated, to use in listen_polo.
#             
# listen_polo-- takes in that token and returns the distribution of VP's between the two nodes. 
# 
# Under the hood, Turn is actually a base class, with a subclass for each certificate authority to allow for different implementations (ex. different HTTP cert requests).
# TurnFactory takes the CA and node pair, and initializes the appropriate subclass with the node pair, returning the result. If a new CA needs to be accomodated, two modifications are necessary: 
# 1) a subclass needs to be created that results in the same behavior as say_marco and listen_polo,
# through some combination of new and reused methods
# 2) TurnFactory must be updated to return that subclass when given it's 2-letter code
# 
# A Turn object stores the CA name, endpoint, and node pair for which it is a turn-- these are ultimately included in the request.
#
# Coupling/Dependencies-- This module hardcodes the CA request format. If this changes format, 
#                         this module will not work.

import os
from pydantic import HttpUrl
import requests
import datetime
import time
import random
import string
import subprocess
from abc import ABC, abstractmethod
import json
from .node import Node, NodeResponseError, NodeRequestError
from marcopolo.utils.loaders import load_config
from marcopolo.utils.loggers import http_logger, error_logger, general_logger
from marcopolo.utils.data_objects import CertAuth, ListenPoloData, SayMarcoData, TurnData
from typing import List, Optional, Tuple
from marcopolo.paths import paths

dir_path = os.path.dirname(os.path.realpath(__file__))


# Factory function to initialize the appropriate subclass
class TurnFactory:
    @staticmethod
    def create(ca: CertAuth, node_a: Node, node_b: Node):
        ca_name = ca.name.lower()
        if ca_name == "ggf":
            return GGFTurn(ca, node_a, node_b)
        elif ca_name == "ggp":
            return GGPTurn(ca, node_a, node_b)
        elif ca_name == "om":
            return OMTurn(ca, node_a, node_b)
        elif ca_name == "cf":
            return CFTurn(ca, node_a, node_b)
        elif ca_name=="le":
            return LETurn(ca, node_a, node_b)
        elif ca_name=="az":
            return AzureTurn(ca, node_a, node_b)
        else:
            raise ValueError(f"Unknown certificate authority: {ca_name}")

class Turn(ABC):
    def __init__(self, ca: CertAuth, node_a: Node, node_b: Node):
        self.node_a: Node = node_a
        self.node_b: Node = node_b
        self.ca=ca

    @abstractmethod
    def generate_request(self, token):
        pass

    def execute(self)->TurnData:
        """
        Executes the turn process, which includes generating a request, 
        sending a 'say_marco' request to the nodes, and listening for 
        responses from the nodes.

        This method performs the following steps:
        1. Calls the `say_marco` method to initiate communication with the nodes.
        2. If successful, it calls the `listen_polo` method to retrieve IP addresses 
           from both nodes using the generated token.
        3. Handles any exceptions that may occur during these processes and logs errors 
           accordingly.

        Returns:
            TurnData: An object containing the results of the turn execution, including the success status, token, start/end times, node info, and any errors encountered.
        """
        
        result = TurnData(
            ca=self.ca,
            node_a=self.node_a,
            node_b=self.node_b,
            start_time=datetime.datetime.now()
        )
        
        # Make the certificate announcement and add record results
        result.say_marco_data = self.say_marco()
        
        if not result.say_marco_data.failed:
            assert result.say_marco_data.token is not None 
            # Ask for all communications and record results
            result.listen_polo_data = self.listen_polo(result.say_marco_data.token)
        
        result.end_time = datetime.datetime.now()
        return result

    # This function uses the token to identify VP requests associated with this Turn.
    # Specifically, it requests from each node the set of IP addresses that contacted it
    # using the given token.
    def listen_polo(self, token: str) -> ListenPoloData:
        """
        Retrieves polo responses from both nodes using the provided token.

        This method sends a request to both nodes to obtain their respective perspectives 
        based on the given token. It handles any potential request or response errors 
        and returns the results encapsulated in a ListenPoloData object.

        Args:
            token (str): The token used to query the nodes' logs for their perspectives.

        Returns:
            ListenPoloData: An object containing the results from both nodes, including 
            the perspectives obtained and any error messages if applicable. If an error occurs, both results are left blank.
        """
        try:
            results_a = self.node_a.get_perspectives(token)
            results_b = self.node_b.get_perspectives(token)
            return ListenPoloData(
                token=token,
                node_a=self.node_a,
                node_b=self.node_b,
                node_a_perspectives=results_a,
                node_b_perspectives=results_b,
                total_num_perspectives=len(results_a) + len(results_b)
            )
        
        except (NodeRequestError, NodeResponseError) as e:
            return ListenPoloData(
                token=token,
                node_a=self.node_a,
                node_b=self.node_b,
                node_a_perspectives=[],
                node_b_perspectives=[],
                error_message=str(e),
                failed=True
            )


    def say_marco(self)->SayMarcoData:
        """
        This method attempts to perform a certificate request up to five times. If successful (response status code 200),
        it returns the token and the number of attempts made. If all attempts fail, it returns an error message.

        Returns:
            SayMarcoData: An object containing:
                - token (str): The token received from the request.
                - response (Optional[str]): The response from the request, if successful.
                - num_tries (int): The number of attempts made.
                - failed (bool): Indicates if the request failed.
                - error_message (Optional[str]): Error message if the request failed.
        """
        retries = 5
        response = None
        error = None
        for attempt_num in range(1, retries+1):
            try:
                response, token = self._single_request()
                response.raise_for_status()
                # if 207 in christines, or 200 with mpic_completed=false in mpic, then try again
                # we have to communicate with all perspectives correctly
                return SayMarcoData(
                        token = token,
                        response = response.text,
                        num_tries = attempt_num,
                        failed = False,
                        error_message = None
                    )
            except Exception as e:
                    error = e
                    print(f"Attempt {attempt_num} failed with error {e}. Waiting 10 seconds and retrying...")
                    time.sleep(10)

        # log error
        error_message = f"Final attempt failed with error: {error}"
        error_logger.info(error_message)
        return SayMarcoData(
            token = None,
            response = None,
            num_tries = retries,
            failed = True,
            error_message = error_message
        )
    
    def _single_request(self):
        """
        This method performs a single request to the certificate authority (CA) endpoint.
        It generates a unique token for the request, constructs the request payload, 
        and sends a POST request to the CA. It handles any exceptions that may occur 
        during the request process and logs the request and response details.

        Returns:
            tuple: A tuple containing:
                - Response object: The response received from the CA.
                - str: The generated token used in the request.

        Raises:
            Exception: If there is an error during the requests.post process
        """
        # Create a random token to identify the cert-request
        # Note: ClourFlare requires a 21 character token, or it'll respond with a 400-- "Not enough entropy in token"
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=21)) 

        # Returns a request with the token embedded in it
        cert_req =self.generate_request(token)
        try:
            response = requests.post(**cert_req, timeout=30) # type: ignore
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error during POST request to {self.ca.endpoint}: {e}")

        # Log request and response (but filter out the long list of VP's returned by the open_mpic implemenation)
        http_logger.info(cert_req)
        filtered_response = {key: value for key, value in response.json().items() if key != 'perspectives'} 
        http_logger.info(filtered_response)
        
        return response, token
        


class OMTurn(Turn):
    def generate_request(self, token):
        return {
            "url": self.ca.endpoint,
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

    def generate_request(self, token):
        return {
            "url": self.ca.endpoint,
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
    def generate_request(self, token):
        return {
            "url": self.ca.endpoint,
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
    def generate_request(self, token):
        return {
            "url": self.ca.endpoint,
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
    
class AzureTurn(Turn):
    def generate_request(self, token):
        return {
            "url": self.ca.endpoint,
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

# Let's Encrypt uses certbot to send certificate requests, so say_marco is completely different.
# It must trigger a certbot process, and requires custom hook scripts to manage the token used. 
# Certbot uses a preflight request, so 
class LETurn(Turn):
    def generate_request(self, token):
        return
    
    def say_marco(self)->SayMarcoData:
        certbot_tools = paths.CERTBOT_TOOLS
        # manual-- needed because cerbot isn't being run on the target webserver (can't place token automatically)
        # auth-hook-- writes token to file, allowing us to read it, and validation string  to file, passing the preflight request (otherwise the others won't succeed)
        # cleanup-hook-- deletes token file
        general_logger.info(f"Running certbot with tools in {certbot_tools}")
        result = subprocess.run([
            "certbot",
            "certonly",
            "--manual",     # allows us to run custom scripts
            "--manual-auth-hook", f"{certbot_tools}/authenticator.sh", 
            "--manual-cleanup-hook", f"{certbot_tools}/cleanup.sh",
            "--config-dir", f"{certbot_tools}/config",
            "--work-dir", f"{certbot_tools}/work",
            "--logs-dir", f"{certbot_tools}/logs",
            "--dry-run",
            "-d", "sajghfgfhsdfasdf.arins.pretend-crypto-wallet.com"
        ], capture_output=True, text=True)
        general_logger.info(f"Certbot result: {result}")
        stdout_output = result.stdout
        stderr_output = result.stderr
        token = None
        with open(f"{certbot_tools}/token", "r") as file:
            token = file.read().strip()
        general_logger.info(f"Token: {token}")
        if token is not None:
            return SayMarcoData(
                        token = token,
                        response = stdout_output,
                        num_tries = 1,
                        failed = False,
                        error_message = stderr_output
                    )
        else:
            return SayMarcoData(
                        token = None,
                        response = stdout_output,
                        num_tries = 1,
                        failed = True,
                        error_message = "No token found: " + stderr_output
            )
        


