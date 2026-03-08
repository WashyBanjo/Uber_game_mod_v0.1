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
        self._default_route_prev: dict[str, str] = {}
        for i, edge_id in enumerate(self.default_route_edge_ids):
            next_edge = self.default_route_edge_ids[(i + 1) % len(self.default_route_edge_ids)]
            prev_edge = self.default_route_edge_ids[(i - 1) % len(self.default_route_edge_ids)]
            self._default_route_next[edge_id] = next_edge
            self._default_route_prev[edge_id] = prev_edge

    def initial_cursor(self) -> RouteSampleCursor:
        return RouteSampleCursor(edge_id=self.default_route_edge_ids[0], line_index=0)

    def cursor_from_legacy_position(self, pos: int) -> RouteSampleCursor:
        route_index = (pos // SEGMENT_LENGTH) % self.route_cycle_length
        for edge_id, offset, edge_len in self._default_route_offsets:
            if route_index < offset + edge_len:
                return RouteSampleCursor(edge_id=edge_id, line_index=route_index - offset)
        return self.initial_cursor()

    def source_line_at_cursor(self, cursor: RouteSampleCursor) -> Line:
        edge = self.road_graph.edges[cursor.edge_id]
        return edge.lines[cursor.line_index]

    def choose_next_edge_id(
        self,
        edge_id: str,
        overrides: dict[str, str] | None = None,
    ) -> str:
        edge = self.road_graph.edges[edge_id]

        override_edge_id = None
        if overrides:
            override_edge_id = overrides.get(edge_id)
        if override_edge_id in edge.next_edge_ids:
            return override_edge_id

        default_next = self._default_route_next.get(edge_id)
        if default_next in edge.next_edge_ids:
            return default_next

        if edge.next_edge_ids:
            return edge.next_edge_ids[0]

        return self.default_route_edge_ids[0]

    def _prev_edge_id(self, edge_id: str) -> str:
        return self._default_route_prev.get(edge_id, self.default_route_edge_ids[-1])

    def advance_cursor(
        self,
        cursor: RouteSampleCursor,
        steps: int,
        overrides: dict[str, str] | None = None,
    ) -> RouteSampleCursor:
        if steps == 0:
            return RouteSampleCursor(cursor.edge_id, cursor.line_index)

        edge_id = cursor.edge_id
        line_index = cursor.line_index

        if steps > 0:
            remaining = steps
            while remaining > 0:
                edge = self.road_graph.edges[edge_id]
                line_index += 1
                if line_index >= len(edge.lines):
                    edge_id = self.choose_next_edge_id(edge_id, overrides=overrides)
                    line_index = 0
                remaining -= 1
        else:
            remaining = -steps
            while remaining > 0:
                line_index -= 1
                if line_index < 0:
                    edge_id = self._prev_edge_id(edge_id)
                    prev_edge = self.road_graph.edges[edge_id]
                    line_index = len(prev_edge.lines) - 1
                remaining -= 1

        return RouteSampleCursor(edge_id=edge_id, line_index=line_index)

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


    def sample_forward_with_edges(
        self,
        cursor: RouteSampleCursor,
        n_segments: int,
        overrides: dict[str, str] | None = None,
    ) -> tuple[list[Line], list[str]]:
        sampled: list[Line] = []
        traversed_edge_ids: list[str] = []

        current_edge_id = cursor.edge_id
        local_index = cursor.line_index

        while len(sampled) < n_segments:
            edge = self.road_graph.edges[current_edge_id]
            if not traversed_edge_ids or traversed_edge_ids[-1] != current_edge_id:
                traversed_edge_ids.append(current_edge_id)

            while local_index < len(edge.lines) and len(sampled) < n_segments:
                sampled.append(self._clone_line(edge.lines[local_index], len(sampled)))
                local_index += 1

            if len(sampled) >= n_segments:
                break

            current_edge_id = self.choose_next_edge_id(current_edge_id, overrides=overrides)
            local_index = 0

        return sampled, traversed_edge_ids

    def sample_forward(
        self,
        cursor: RouteSampleCursor,
        n_segments: int,
        overrides: dict[str, str] | None = None,
    ) -> list[Line]:
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

            current_edge_id = self.choose_next_edge_id(current_edge_id, overrides=overrides)
            local_index = 0

        return sampled
