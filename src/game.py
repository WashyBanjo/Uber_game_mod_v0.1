import sys
import time

import pygame

from assets import load_background, load_sprites
from renderer import draw_background, draw_road, draw_sprites
from road_builder import build_demo_road_graph
from route_sampler import RouteSampler
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

        self.sampling_window = SHOW_N_SEGMENTS + 8
        self.lines = self.route_sampler.sample_forward(
            self.route_sampler.cursor_from_legacy_position(0),
            self.sampling_window,
        )
        self.n_lines = self.route_sampler.route_cycle_length

        self.pos = 0
        self.playerX = 0
        self.playerY = 1500

    def handle_events(self):
        for event in pygame.event.get([pygame.QUIT]):
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def sample_input(self) -> int:
        speed = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            speed += SEGMENT_LENGTH
        if keys[pygame.K_DOWN]:
            speed -= SEGMENT_LENGTH
        if keys[pygame.K_RIGHT]:
            self.playerX += 200
        if keys[pygame.K_LEFT]:
            self.playerX -= 200
        if keys[pygame.K_w]:
            self.playerY += 100
        if keys[pygame.K_s]:
            self.playerY -= 100
        if self.playerY < 500:
            self.playerY = 500
        if keys[pygame.K_TAB]:
            speed *= 2
        return speed

    def update(self, speed: int):
        self.pos += speed

        while self.pos >= self.n_lines * SEGMENT_LENGTH:
            self.pos -= self.n_lines * SEGMENT_LENGTH
        while self.pos < 0:
            self.pos += self.n_lines * SEGMENT_LENGTH

        cursor = self.route_sampler.cursor_from_legacy_position(self.pos)
        current_source_line = self.route_sampler.source_line_at_cursor(cursor)

        if speed > 0:
            self.background_rect.x -= current_source_line.curve * 2
        elif speed < 0:
            self.background_rect.x += current_source_line.curve * 2

        if self.background_rect.right < WINDOW_WIDTH:
            self.background_rect.x = -WINDOW_WIDTH
        elif self.background_rect.left > 0:
            self.background_rect.x = -WINDOW_WIDTH

        return cursor

    def render(self, cursor):
        self.window_surface.fill((105, 205, 4))
        draw_background(self.window_surface, self.background_surface, self.background_rect)

        self.lines = self.route_sampler.sample_forward(cursor, self.sampling_window)

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

        pygame.display.update()

    def run(self):
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            self.handle_events()
            speed = self.sample_input()
            cursor = self.update(speed)
            self.render(cursor)
            self.clock.tick(60)
