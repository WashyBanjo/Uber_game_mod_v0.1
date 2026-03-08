import sys
import time

import pygame

from assets import load_background, load_sprites
from debug_overlay import draw_debug_overlay
from renderer import draw_background, draw_road, draw_sprites
from road_builder import build_demo_road_graph
from route_sampler import RouteSampleCursor, RouteSampler
from settings import SEGMENT_LENGTH, SHOW_N_SEGMENTS, WINDOW_HEIGHT, WINDOW_WIDTH


class Game:
    def __init__(self):
        pygame.display.set_caption("Racing Pseudo 3D")
        self.window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0

        self.background_surface, self.background_rect = load_background()
        self.window_surface.blit(self.background_surface, self.background_rect)

        self.sprites = load_sprites()
        self.road_graph = build_demo_road_graph(self.sprites)
        self.route_sampler = RouteSampler(self.road_graph)
        self.route_edge_ids = list(self.road_graph.default_route_edge_ids)

        self.current_edge_id = self.route_edge_ids[0]
        self.current_line_index = 0
        self.pending_next_edge_id: str | None = None

        self.branch_choice_threshold = 30
        self.sampling_window = SHOW_N_SEGMENTS + 8
        self.lines = self.route_sampler.sample_forward(
            self.current_cursor(),
            self.sampling_window,
        )
        self.sampled_edge_ids: list[str] = []

        self.show_debug_overlay = True

        self.playerX = 0
        self.playerY = 1500

    def current_cursor(self) -> RouteSampleCursor:
        return RouteSampleCursor(self.current_edge_id, self.current_line_index)

    def handle_events(self):
        for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.show_debug_overlay = not self.show_debug_overlay

    def sample_input(self) -> tuple[int, bool, bool]:
        speed = 0
        keys = pygame.key.get_pressed()

        left_pressed = keys[pygame.K_LEFT]
        right_pressed = keys[pygame.K_RIGHT]

        if keys[pygame.K_UP]:
            speed += SEGMENT_LENGTH
        if keys[pygame.K_DOWN]:
            speed -= SEGMENT_LENGTH
        if right_pressed:
            self.playerX += 200
        if left_pressed:
            self.playerX -= 200
        if keys[pygame.K_w]:
            self.playerY += 100
        if keys[pygame.K_s]:
            self.playerY -= 100
        if self.playerY < 500:
            self.playerY = 500
        if keys[pygame.K_TAB]:
            speed *= 2

        return speed, left_pressed, right_pressed

    def _choice_overrides(self) -> dict[str, str] | None:
        if self.pending_next_edge_id is None:
            return None
        return {self.current_edge_id: self.pending_next_edge_id}

    def _default_pending_for_edge(self, edge_id: str) -> str | None:
        edge = self.road_graph.edges[edge_id]
        if not edge.next_edge_ids:
            return None

        default_next = self.route_sampler.choose_next_edge_id(edge_id)
        if default_next in edge.next_edge_ids:
            return default_next
        return edge.next_edge_ids[0]

    def _update_pending_branch_choice(self, left_pressed: bool, right_pressed: bool):
        edge = self.road_graph.edges[self.current_edge_id]

        if len(edge.next_edge_ids) <= 1:
            self.pending_next_edge_id = None
            return

        near_end = self.current_line_index >= len(edge.lines) - self.branch_choice_threshold
        if not near_end:
            self.pending_next_edge_id = None
            return

        if self.pending_next_edge_id not in edge.next_edge_ids:
            self.pending_next_edge_id = self._default_pending_for_edge(self.current_edge_id)

        if left_pressed and not right_pressed:
            self.pending_next_edge_id = edge.next_edge_ids[0]
            return

        if right_pressed and not left_pressed:
            self.pending_next_edge_id = edge.next_edge_ids[-1]
            return

        if self.pending_next_edge_id is None:
            self.pending_next_edge_id = self._default_pending_for_edge(self.current_edge_id)

    def update(self, speed: int, left_pressed: bool, right_pressed: bool):
        self._update_pending_branch_choice(left_pressed, right_pressed)

        step_count = speed // SEGMENT_LENGTH
        next_cursor = self.route_sampler.advance_cursor(
            self.current_cursor(),
            step_count,
            overrides=self._choice_overrides(),
        )

        edge_changed = next_cursor.edge_id != self.current_edge_id
        self.current_edge_id = next_cursor.edge_id
        self.current_line_index = next_cursor.line_index

        if edge_changed:
            self.pending_next_edge_id = None

        current_source_line = self.route_sampler.source_line_at_cursor(next_cursor)

        if speed > 0:
            self.background_rect.x -= current_source_line.curve * 2
        elif speed < 0:
            self.background_rect.x += current_source_line.curve * 2

        if self.background_rect.right < WINDOW_WIDTH:
            self.background_rect.x = -WINDOW_WIDTH
        elif self.background_rect.left > 0:
            self.background_rect.x = -WINDOW_WIDTH

        return next_cursor

    def render(self, cursor: RouteSampleCursor):
        self.window_surface.fill((105, 205, 4))
        draw_background(self.window_surface, self.background_surface, self.background_rect)

        self.lines, self.sampled_edge_ids = self.route_sampler.sample_forward_with_edges(
            cursor,
            self.sampling_window,
            overrides=self._choice_overrides(),
        )

        camH = self.lines[0].y + self.playerY

        draw_road(
            self.window_surface,
            self.lines,
            0,
            SHOW_N_SEGMENTS,
            self.playerX,
            camH,
            0,
            SEGMENT_LENGTH,
        )
        draw_sprites(self.window_surface, self.lines, 0)

        if self.show_debug_overlay:
            draw_debug_overlay(
                self.window_surface,
                self.road_graph,
                cursor,
                self.pending_next_edge_id,
                self.sampled_edge_ids,
            )

        pygame.display.update()

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            self.handle_events()
            speed, left_pressed, right_pressed = self.sample_input()
            cursor = self.update(speed, left_pressed, right_pressed)
            self.render(cursor)
            self.clock.tick(60)
