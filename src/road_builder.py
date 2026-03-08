import math
from typing import List

import pygame

from road import Line
from road_graph import Edge, Node, RoadGraph
from settings import (
    BLACK_RUMBLE,
    DARK_GRASS,
    DARK_ROAD,
    LIGHT_GRASS,
    LIGHT_ROAD,
    SEGMENT_LENGTH,
    WHITE_RUMBLE,
)


def _make_edge_lines(length: int) -> list[Line]:
    lines: list[Line] = []
    for i in range(length):
        line = Line(i)
        line.z = i * SEGMENT_LENGTH + 0.00001
        line.grass_color = LIGHT_GRASS if (i // 3) % 2 else DARK_GRASS
        line.rumble_color = WHITE_RUMBLE if (i // 3) % 2 else BLACK_RUMBLE
        line.road_color = LIGHT_ROAD if (i // 3) % 2 else DARK_ROAD
        lines.append(line)
    return lines


def _apply_curve(lines: list[Line], start: int, end: int, amount: float):
    for i in range(start, min(end, len(lines))):
        lines[i].curve = amount


def _apply_hills(lines: list[Line], start: int, amplitude: float, frequency: float):
    for i in range(start, len(lines)):
        lines[i].y = math.sin(i / frequency) * amplitude


def _apply_sprite_pattern(
    lines: list[Line],
    sprite: pygame.Surface,
    sprite_x: float,
    modulo: int,
    min_index: int = 0,
):
    for i, line in enumerate(lines):
        if i >= min_index and i % modulo == 0:
            line.spriteX = sprite_x
            line.sprite = sprite


def build_demo_graph(sprites: List[pygame.Surface]) -> RoadGraph:
    graph = RoadGraph()

    graph.add_node(Node("A", 0, 0))
    graph.add_node(Node("B", 100, 0))
    graph.add_node(Node("C", 200, 20))
    graph.add_node(Node("D", 180, -80))
    graph.add_node(Node("E", 300, -10))
    graph.add_node(Node("F", 330, 80))

    edge_main_0_lines = _make_edge_lines(300)
    _apply_sprite_pattern(edge_main_0_lines, sprites[4], -2.5, 20)
    _apply_sprite_pattern(edge_main_0_lines, sprites[5], 2.0, 17)

    edge_main_1_lines = _make_edge_lines(400)
    _apply_curve(edge_main_1_lines, 20, 320, 0.5)
    _apply_sprite_pattern(edge_main_1_lines, sprites[3], -0.7, 20, min_index=60)
    edge_main_1_lines[200].spriteX = -1.2
    edge_main_1_lines[200].sprite = sprites[6]

    edge_main_2_lines = _make_edge_lines(450)
    _apply_hills(edge_main_2_lines, 30, 1500, 30.0)
    _apply_curve(edge_main_2_lines, 220, len(edge_main_2_lines), -0.7)
    _apply_sprite_pattern(edge_main_2_lines, sprites[0], -1.2, 20, min_index=120)

    edge_loop_lines = _make_edge_lines(450)
    _apply_curve(edge_loop_lines, 0, 200, -0.25)
    _apply_curve(edge_loop_lines, 200, len(edge_loop_lines), 0.25)
    _apply_sprite_pattern(edge_loop_lines, sprites[5], 2.0, 17)

    edge_branch_up_lines = _make_edge_lines(220)
    _apply_curve(edge_branch_up_lines, 40, 180, -0.45)
    _apply_hills(edge_branch_up_lines, 0, 1000, 20.0)
    _apply_sprite_pattern(edge_branch_up_lines, sprites[1], -1.0, 26)

    edge_branch_rejoin_lines = _make_edge_lines(180)
    _apply_curve(edge_branch_rejoin_lines, 20, 150, 0.35)
    _apply_hills(edge_branch_rejoin_lines, 0, 900, 18.0)
    _apply_sprite_pattern(edge_branch_rejoin_lines, sprites[2], 1.4, 23)

    edge_spur_lines = _make_edge_lines(140)
    _apply_curve(edge_spur_lines, 10, 130, 0.6)
    _apply_sprite_pattern(edge_spur_lines, sprites[6], -1.2, 35)

    graph.add_edge(Edge("main_0", "A", "B", edge_main_0_lines, ["main_1", "branch_up"]))
    graph.add_edge(Edge("main_1", "B", "C", edge_main_1_lines, ["main_2", "spur"]))
    graph.add_edge(Edge("main_2", "C", "E", edge_main_2_lines, ["loop_back"]))
    graph.add_edge(Edge("loop_back", "E", "B", edge_loop_lines, ["main_1", "branch_up"]))
    graph.add_edge(Edge("branch_up", "B", "D", edge_branch_up_lines, ["branch_rejoin"]))
    graph.add_edge(Edge("branch_rejoin", "D", "E", edge_branch_rejoin_lines, ["loop_back"]))
    graph.add_edge(Edge("spur", "C", "F", edge_spur_lines, []))

    graph.default_route_edge_ids = ["main_0", "main_1", "main_2", "loop_back"]

    return graph
