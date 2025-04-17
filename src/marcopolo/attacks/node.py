import ipaddress
from typing import List
import requests

from pydantic import BaseModel, IPvAnyAddress
from marcopolo.utils.logs_writer import http_logger

class Node(BaseModel):
    name: str
    ip: IPvAnyAddress

    def get_perspectives(self, token: str) -> List[IPvAnyAddress]:
        """
        Gets all perspective ips from this node for a given token.
        
        Args:
            token: The token to search for in the node's logs
            
        Returns:
            List[str]: List of polo results found for this token
            
        Raises:
            NodeRequestError: If the request to the node fails
            NodeResponseError: If the response is invalid
        """
        try:
            # PART ONE: REQUEST. If something goes wrong, raises request error.

            response = requests.get(
                f"http://{self.ip}/getips",
                params={"token": token},
                timeout=5
            )
            http_logger.info(f"Response to getips for node {self.name}: {response.text}")
            response.raise_for_status()

            # PART TWO: RESPONSE. If something goes wrong, raises response error.
            json_data = response.json()
            if 'ip_addresses' not in json_data:
                raise NodeResponseError(f"'ip_addresses' field missing in response from {self.name}")

            ip_list = json_data['ip_addresses']
            if not isinstance(ip_list, list):
                raise NodeResponseError(f"'ip_addresses' must be a list of strings from {self.name}, got: {ip_list}")

            return [ipaddress.ip_address(ip) for ip in ip_list]
            
        except requests.RequestException as e:
            raise NodeRequestError(f"Failed to get perspectives from {self.name}: {str(e)}")

class NodeRequestError(Exception):
    """Raised when there is an issue with a node request."""
    pass

class NodeResponseError(Exception):
    """Raised when the node response is invalid."""
    pass