from pathlib import Path
from typing import List

import pygame

from settings import WINDOW_WIDTH


def _images_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "images"


def load_background() -> tuple[pygame.Surface, pygame.Rect]:
    image_path = _images_dir() / "bg.png"
    background_image = pygame.image.load(str(image_path)).convert_alpha()
    background_image = pygame.transform.scale(
        background_image, (WINDOW_WIDTH, background_image.get_height())
    )
    background_surface = pygame.Surface(
        (background_image.get_width() * 3, background_image.get_height())
    )
    background_surface.blit(background_image, (0, 0))
    background_surface.blit(background_image, (background_image.get_width(), 0))
    background_surface.blit(background_image, (background_image.get_width() * 2, 0))
    background_rect = background_surface.get_rect(
        topleft=(-background_image.get_width(), 0)
    )
    return background_surface, background_rect


def load_sprites() -> List[pygame.Surface]:
    sprites: List[pygame.Surface] = []
    for i in range(1, 8):
        sprites.append(
            pygame.image.load(str(_images_dir() / f"{i}.png")).convert_alpha()
        )
    return sprites
