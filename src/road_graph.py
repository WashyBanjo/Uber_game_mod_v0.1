from dataclasses import dataclass, field

from road import Line
from settings import SEGMENT_LENGTH


@dataclass
class Node:
    id: str
    world_pos: tuple[float, float] | None = None


@dataclass
class Edge:
    id: str
    start_node_id: str
    end_node_id: str
    lines: list[Line]
    next_edge_ids: list[str] = field(default_factory=list)


@dataclass
class RoadGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)
    default_route_edge_ids: list[str] = field(default_factory=list)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge

    def flatten_default_route(self) -> list[Line]:
        flattened: list[Line] = []
        for edge_id in self.default_route_edge_ids:
            edge = self.edges[edge_id]
            for source_line in edge.lines:
                line = Line(len(flattened))
                line.x = source_line.x
                line.y = source_line.y
                line.z = len(flattened) * SEGMENT_LENGTH + 0.00001
                line.curve = source_line.curve
                line.spriteX = source_line.spriteX
                line.sprite = source_line.sprite
                line.grass_color = source_line.grass_color
                line.rumble_color = source_line.rumble_color
                line.road_color = source_line.road_color
                flattened.append(line)
        return flattened
