import pygame

from road import Line
from settings import SHOW_N_SEGMENTS, WINDOW_WIDTH


def draw_quad(
    surface: pygame.Surface,
    color: pygame.Color,
    x1: int,
    y1: int,
    w1: int,
    x2: int,
    y2: int,
    w2: int,
):
    pygame.draw.polygon(
        surface, color, [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)]
    )


def draw_background(
    window_surface: pygame.Surface,
    background_surface: pygame.Surface,
    background_rect: pygame.Rect,
):
    window_surface.blit(background_surface, background_rect)


def draw_road(
    window_surface: pygame.Surface,
    lines: list[Line],
    start_pos: int,
    segment_count: int,
    player_x: int,
    cam_h: int,
    pos: int,
    segment_length: int,
):
    n_lines = len(lines)
    x = dx = 0.0
    maxy = window_surface.get_height()

    for n in range(start_pos, start_pos + segment_count):
        current = lines[n % n_lines]
        current.project(
            player_x - x,
            cam_h,
            pos - (n_lines * segment_length if n >= n_lines else 0),
        )
        x += dx
        dx += current.curve

        current.clip = maxy

        if current.Y >= maxy:
            continue
        maxy = current.Y

        prev = lines[(n - 1) % n_lines]

        draw_quad(
            window_surface,
            current.grass_color,
            0,
            prev.Y,
            WINDOW_WIDTH,
            0,
            current.Y,
            WINDOW_WIDTH,
        )
        draw_quad(
            window_surface,
            current.rumble_color,
            prev.X,
            prev.Y,
            prev.W * 1.2,
            current.X,
            current.Y,
            current.W * 1.2,
        )
        draw_quad(
            window_surface,
            current.road_color,
            prev.X,
            prev.Y,
            prev.W,
            current.X,
            current.Y,
            current.W,
        )


def draw_sprites(window_surface: pygame.Surface, lines: list[Line], start_pos: int):
    n_lines = len(lines)
    for n in range(start_pos + SHOW_N_SEGMENTS, start_pos + 1, -1):
        lines[n % n_lines].drawSprite(window_surface)
