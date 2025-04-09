from typing import List, Dict, Optional
from dataclasses import field
from datetime import datetime
from pydantic import BaseModel, HttpUrl, IPvAnyAddress, RootModel

from ..attacks.node import Node

from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl, IPvAnyAddress
from typing import Literal

CompatibleCertAuth = Literal[
    "ggf",
    "ggp",
    "om",
    "cf",
    "le",
    "az"
]

class CertAuth(BaseModel):
    name: CompatibleCertAuth
    endpoint: Optional[HttpUrl]
    num_perspectives: Optional[int] = None

class SayMarcoData(BaseModel):
    token: Optional[str] = None
    response: Optional[str] = None
    num_tries: int
    error_message: Optional[str] = None
    failed: bool = False


class ListenPoloData(BaseModel):
    token: Optional[str] = None
    response: Optional[str] = None
    node_a: Node
    node_b: Node
    node_a_perspectives: Optional[List[IPvAnyAddress]] = None
    node_b_perspectives: Optional[List[IPvAnyAddress]] = None
    total_num_perspectives: Optional[int] = None
    error_message: Optional[str] = None
    failed: bool = False


class TurnData(BaseModel):
    ca: CertAuth
    node_a: Node
    node_b: Node
    start_time: datetime
    end_time: Optional[datetime] = None
    say_marco_data: Optional[SayMarcoData] = None
    listen_polo_data: Optional[ListenPoloData] = None
    error: Optional[str] = None


class RoundData(BaseModel):
    node_a: Node
    node_b: Node
    cas: list[CertAuth]
    bgp_prefix: str
    start_time: datetime
    turns: List[TurnData] = []
    end_time: Optional[datetime] = None
    errors: List[Optional[str]] = field(default_factory=list)
    something_failed: bool = False


class Game(BaseModel):
    game_id: str
    nodes: List[Node]  # All nodes participating in the game
    cas: List[CertAuth]  # Certificate authorities involved
    rounds: List[RoundData] = []
    summary: Dict[str, int] = {}

Region = Literal[
    "ams",
    "atl",
    "blr",
    "bom",
    "cdg",
    "del",
    "dfw",
    "ewr",
    "fra",
    "icn",
    "itm",
    "jnb",
    "lax",
    "lhr",
    "mad",
    "man",
    "mel",
    "mex",
    "mia",
    "nrt",
    "ord",
    "scl",
    "sea",
    "sgp",
    "sjc",
    "sto",
    "syd",
    "tlv",
    "waw",
    "yto",
    "sao",
    "hnl",
]




class Config(BaseModel):
    nodes: List[Node]
    vultr_regions: Dict[str, Region]
    certificate_authorities: List[CertAuth]

class State(BaseModel):
    mid_test: bool
    curr_node_a: str
    curr_node_b: str


CAResults = dict[str, dict[str, list[str]]]