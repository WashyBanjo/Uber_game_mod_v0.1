import pygame

from road_graph import RoadGraph
from route_sampler import RouteSampleCursor


def _fit_world_to_rect(
    nodes: dict,
    origin_x: int,
    origin_y: int,
    width: int,
    height: int,
    padding: int = 16,
):
    xs = [node.world_pos[0] for node in nodes.values() if node.world_pos is not None]
    ys = [node.world_pos[1] for node in nodes.values() if node.world_pos is not None]

    if not xs or not ys:
        return lambda _p: (origin_x + width // 2, origin_y + height // 2)

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)

    draw_w = max(width - padding * 2, 1)
    draw_h = max(height - padding * 2, 1)

    def to_screen(pos):
        px = (pos[0] - min_x) / span_x
        py = (pos[1] - min_y) / span_y
        x = origin_x + padding + int(px * draw_w)
        y = origin_y + padding + int(py * draw_h)
        return x, y

    return to_screen


def _draw_text_block(surface: pygame.Surface, lines: list[str], x: int, y: int):
    font = pygame.font.SysFont("Arial", 14)
    for i, line in enumerate(lines):
        text = font.render(line, True, pygame.Color("white"))
        surface.blit(text, (x, y + i * 16))


def draw_debug_overlay(
    surface: pygame.Surface,
    road_graph: RoadGraph,
    cursor: RouteSampleCursor,
    pending_next_edge_id: str | None,
    sampled_edge_ids: list[str],
):
    map_x, map_y, map_w, map_h = 16, 16, 300, 220
    panel_rect = pygame.Rect(map_x, map_y, map_w, map_h)
    pygame.draw.rect(surface, pygame.Color(20, 20, 20), panel_rect)
    pygame.draw.rect(surface, pygame.Color(180, 180, 180), panel_rect, 2)

    to_screen = _fit_world_to_rect(road_graph.nodes, map_x, map_y, map_w, map_h)

    # base graph edges
    for edge in road_graph.edges.values():
        start_node = road_graph.nodes[edge.start_node_id]
        end_node = road_graph.nodes[edge.end_node_id]
        if start_node.world_pos is None or end_node.world_pos is None:
            continue
        pygame.draw.line(
            surface,
            pygame.Color(90, 90, 90),
            to_screen(start_node.world_pos),
            to_screen(end_node.world_pos),
            2,
        )

    # sampled forward path edges
    for edge_id in sampled_edge_ids:
        edge = road_graph.edges.get(edge_id)
        if edge is None:
            continue
        start_node = road_graph.nodes[edge.start_node_id]
        end_node = road_graph.nodes[edge.end_node_id]
        if start_node.world_pos is None or end_node.world_pos is None:
            continue
        pygame.draw.line(
            surface,
            pygame.Color(80, 180, 255),
            to_screen(start_node.world_pos),
            to_screen(end_node.world_pos),
            3,
        )

    # pending branch edge highlight
    if pending_next_edge_id is not None and pending_next_edge_id in road_graph.edges:
        edge = road_graph.edges[pending_next_edge_id]
        start_node = road_graph.nodes[edge.start_node_id]
        end_node = road_graph.nodes[edge.end_node_id]
        if start_node.world_pos is not None and end_node.world_pos is not None:
            pygame.draw.line(
                surface,
                pygame.Color(255, 200, 0),
                to_screen(start_node.world_pos),
                to_screen(end_node.world_pos),
                4,
            )

    # current edge highlight
    current_edge = road_graph.edges[cursor.edge_id]
    start_node = road_graph.nodes[current_edge.start_node_id]
    end_node = road_graph.nodes[current_edge.end_node_id]
    if start_node.world_pos is not None and end_node.world_pos is not None:
        start_xy = to_screen(start_node.world_pos)
        end_xy = to_screen(end_node.world_pos)
        pygame.draw.line(surface, pygame.Color(255, 80, 80), start_xy, end_xy, 5)

        # player marker interpolated along current edge
        t = 0.0
        if len(current_edge.lines) > 1:
            t = cursor.line_index / (len(current_edge.lines) - 1)
        px = int(start_xy[0] + (end_xy[0] - start_xy[0]) * t)
        py = int(start_xy[1] + (end_xy[1] - start_xy[1]) * t)
        pygame.draw.circle(surface, pygame.Color(255, 255, 255), (px, py), 5)

    # nodes on top
    for node in road_graph.nodes.values():
        if node.world_pos is None:
            continue
        nx, ny = to_screen(node.world_pos)
        pygame.draw.circle(surface, pygame.Color(200, 200, 200), (nx, ny), 4)

    sampled_preview = ", ".join(sampled_edge_ids[:5]) if sampled_edge_ids else "None"
    debug_lines = [
        f"edge: {cursor.edge_id}",
        f"line: {cursor.line_index}",
        f"pending: {pending_next_edge_id or 'None'}",
        f"sampled: {sampled_preview}",
        "toggle: M",
    ]
    _draw_text_block(surface, debug_lines, map_x + 10, map_y + map_h + 8)
