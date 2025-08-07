#!/usr/bin/env python3
from dataclasses import dataclass, field
import uuid
import datetime
from typing import Dict, Any, Callable, List
import pickle
import json

import networkx as nx
from networkx.readwrite import json_graph
from dateutil.parser import isoparse

@dataclass
class MemoryEvent:
    """
    Represents a single event in Q’s life.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    type: str = ""                     # e.g. "collapse", "anchor_added", "sensor_reading"
    payload: Dict[str, Any] = field(default_factory=dict)

class MemoryGraph:
    """
    Episodic memory stored as a directed graph.
    Nodes are MemoryEvent instances; edges carry a 'relation' label.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event: MemoryEvent):
        """Add a new event node, auto-linking to the last event in time."""
        self.graph.add_node(event.id, event=event)
        # Auto-link temporal edge from the most recent prior event
        all_nodes = list(self.graph.nodes)
        if len(all_nodes) > 1:
            prior = [
                (nid, self.graph.nodes[nid]['event'].timestamp)
                for nid in all_nodes if nid != event.id
            ]
            prior.sort(key=lambda x: x[1], reverse=True)
            last_id = prior[0][0]
            self.link_events(last_id, event.id, relation="next_in_time")

    def link_events(self, src_id: str, dst_id: str, relation: str):
        """Create a labeled edge from src to dst (e.g. causal, shared_anchor)."""
        if src_id in self.graph and dst_id in self.graph:
            self.graph.add_edge(src_id, dst_id, relation=relation)
        else:
            raise KeyError(f"Cannot link {src_id} → {dst_id}: node missing")

    def retrieve(
        self,
        filter_fn: Callable[[MemoryEvent], bool],
        max_results: int = 10
    ) -> List[MemoryEvent]:
        """
        Return up to `max_results` events matching `filter_fn`,
        sorted by most-recent timestamp first.
        """
        matches = [
            data['event']
            for _, data in self.graph.nodes(data=True)
            if filter_fn(data['event'])
        ]
        matches.sort(key=lambda e: e.timestamp, reverse=True)
        return matches[:max_results]

    def related(self, event_id: str, depth: int = 1) -> List[MemoryEvent]:
        """
        Return all events within `depth` hops of `event_id`
        (excluding the root event itself).
        """
        if event_id not in self.graph:
            raise KeyError(f"Event {event_id} not in graph")
        lengths = nx.single_source_shortest_path_length(self.graph, event_id, cutoff=depth)
        return [
            self.graph.nodes[n]['event']
            for n, dist in lengths.items() if n != event_id
        ]

    def save(self, filepath: str):
        """Persist the graph via pickle."""
        with open(filepath, 'wb') as f:
            pickle.dump(self.graph, f)

    def load(self, filepath: str):
        """Load a previously saved graph via pickle."""
        with open(filepath, 'rb') as f:
            self.graph = pickle.load(f)

    def save_json(self, filepath: str):
        """
        Persist the graph as JSON (node-link data), serializing MemoryEvent nodes.
        """
        data = json_graph.node_link_data(self.graph)
        for node in data.get('nodes', []):
            ev = node.get('event')
            if isinstance(ev, MemoryEvent):
                node['event'] = {
                    'id': ev.id,
                    'timestamp': ev.timestamp.isoformat(),
                    'type': ev.type,
                    'payload': ev.payload
                }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_json(self, filepath: str):
        """
        Load and rehydrate a graph from JSON.
        Reconstructs MemoryEvent instances from stored dicts.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        G = json_graph.node_link_graph(data, edges="links")
        for nid, attrs in G.nodes(data=True):
            ev_dict = attrs.get('event')
            if isinstance(ev_dict, dict):
                attrs['event'] = MemoryEvent(
                    id=ev_dict.get('id'),
                    timestamp=isoparse(ev_dict.get('timestamp')),
                    type=ev_dict.get('type'),
                    payload=ev_dict.get('payload', {})
                )
        self.graph = G

    # —————— Enhancements ——————

    def export_dot(self, path: str):
        """
        Write the current graph to GraphViz DOT format.
        """
        from networkx.drawing.nx_pydot import write_dot
        write_dot(self.graph, path)

    def to_cytoscape_json(self) -> dict:
        """
        Return a Cytoscape-compatible JSON for the graph.
        """
        return json_graph.cytoscape_data(self.graph)

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def avg_degree(self) -> float:
        n = self.node_count()
        if n == 0:
            return 0.0
        return sum(dict(self.graph.degree()).values()) / n

    def clustering_coefficient(self) -> float:
        return nx.average_clustering(self.graph)

    def compute_phi(self) -> float:
        """
        Compute Integrated Information Φ for current graph state.
        """
        import pyphi
        # Build adjacency matrix in node order
        nodes = list(self.graph.nodes())
        A = nx.to_numpy_array(self.graph, nodelist=nodes)
        network = pyphi.Network(A, node_labels=nodes)
        # Placeholder: assume all nodes 'on'
        state = tuple(1 for _ in nodes)
        return pyphi.compute.phi(network, state)


