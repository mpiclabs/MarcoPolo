from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime



@dataclass
class TurnData:
    ca_name: str
    ca_endpoint: str
    node_a_name: str 
    node_a_ip: str
    node_b_name: str  
    node_b_ip: str
    turn_id: str = None
    round_id: str = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    marco_num_tries: Optional[int] = None
    marco_succeeded: Optional[bool] = None
    token: Optional[str] = None
    listen_polo_succeeded: Optional[bool] = None
    polos_num_tries: Optional[int] = None
    polo_results_node_a: Optional[List[str]] = field(default_factory=list)  # Node -> Count of polos
    polo_results_node_b: Optional[List[str]] = field(default_factory=list)  # Node -> Count of polos
    errors: Optional[List[str]] = field(default_factory=list)

    def __repr__(self):
        return (f"Turn(turn_id={self.turn_id}, round_id={self.round_id}, ca={self.ca}, "
                f"node_a={self.node_a}, node_b={self.node_b}, start_time={self.start_time}, "
                f"end_time={self.end_time}, marco_num_tries={self.marco_num_tries}, "
                f"marco_succeeded={self.marco_succeeded}, token={self.token}, "
                f"polos_num_tries={self.polos_num_tries}, polo_results_node_a={self.polo_results_node_a}, "
                f"polo_results_node_b={self.polo_results_node_b}, errors={self.errors})")


@dataclass
class RoundData:
    node_a_name: str 
    node_a_ip: str
    node_b_name: str  
    node_b_ip: str
    ca_names: List[str]
    ip_announced: str
    start_time: datetime
    end_time: datetime
    round_id: str
    game_id: str
    turns: List[TurnData] = field(default_factory=list)
    errors: Optional[List[str]] = field(default_factory=list)

    def __repr__(self):
        return (f"Round(round_id={self.round_id}, game_id={self.game_id}, "
                f"node_pair={self.node_pair}, ip_announcement={self.ip_announcement}, "
                f"turns={len(self.turns)} turns, errors={self.errors})")


@dataclass
class Game:
    game_id: str
    nodes: List[str]  # All nodes participating in the game
    cas: List[str]  # Certificate authorities involved
    rounds: List[RoundData] = field(default_factory=list)
    summary: Optional[Dict[str, int]] = field(default_factory=dict)

    def __repr__(self):
        return (f"Game(game_id={self.game_id}, nodes={self.nodes}, "
                f"cas={self.cas}, rounds={len(self.rounds)} rounds, "
                f"summary={self.summary})")