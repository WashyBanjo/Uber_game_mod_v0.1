from dataclasses import dataclass

from road import Line
from road_graph import RoadGraph
from settings import SEGMENT_LENGTH


@dataclass
class RouteSampleCursor:
    edge_id: str
    line_index: int


class RouteSampler:
    def __init__(self, road_graph: RoadGraph):
        self.road_graph = road_graph
        self.default_route_edge_ids = list(road_graph.default_route_edge_ids)
        self._default_route_offsets: list[tuple[str, int, int]] = []

        offset = 0
        for edge_id in self.default_route_edge_ids:
            edge = self.road_graph.edges[edge_id]
            edge_len = len(edge.lines)
            self._default_route_offsets.append((edge_id, offset, edge_len))
            offset += edge_len
        self.route_cycle_length = offset

        self._default_route_next: dict[str, str] = {}
        for i, edge_id in enumerate(self.default_route_edge_ids):
            next_edge = self.default_route_edge_ids[(i + 1) % len(self.default_route_edge_ids)]
            self._default_route_next[edge_id] = next_edge

    def cursor_from_legacy_position(self, pos: int) -> RouteSampleCursor:
        route_index = (pos // SEGMENT_LENGTH) % self.route_cycle_length
        for edge_id, offset, edge_len in self._default_route_offsets:
            if route_index < offset + edge_len:
                return RouteSampleCursor(edge_id=edge_id, line_index=route_index - offset)
        fallback_edge_id = self.default_route_edge_ids[0]
        return RouteSampleCursor(edge_id=fallback_edge_id, line_index=0)

    def source_line_at_cursor(self, cursor: RouteSampleCursor) -> Line:
        edge = self.road_graph.edges[cursor.edge_id]
        return edge.lines[cursor.line_index]

    def _next_edge_id(self, edge_id: str) -> str:
        edge = self.road_graph.edges[edge_id]
        if edge.next_edge_ids:
            return edge.next_edge_ids[0]
        return self._default_route_next.get(edge_id, self.default_route_edge_ids[0])

    def _clone_line(self, source_line: Line, index: int) -> Line:
        line = Line(index)
        line.x = source_line.x
        line.y = source_line.y
        line.z = index * SEGMENT_LENGTH + 0.00001
        line.curve = source_line.curve
        line.spriteX = source_line.spriteX
        line.sprite = source_line.sprite
        line.grass_color = source_line.grass_color
        line.rumble_color = source_line.rumble_color
        line.road_color = source_line.road_color
        return line

    def sample_forward(self, cursor: RouteSampleCursor, n_segments: int) -> list[Line]:
        sampled: list[Line] = []

        current_edge_id = cursor.edge_id
        local_index = cursor.line_index

        while len(sampled) < n_segments:
            edge = self.road_graph.edges[current_edge_id]
            while local_index < len(edge.lines) and len(sampled) < n_segments:
                sampled.append(self._clone_line(edge.lines[local_index], len(sampled)))
                local_index += 1

            if len(sampled) >= n_segments:
                break

            current_edge_id = self._next_edge_id(current_edge_id)
            local_index = 0

        return sampled
