import math
from typing import List

import pygame

from road import Line
from settings import (
    BLACK_RUMBLE,
    DARK_GRASS,
    DARK_ROAD,
    LIGHT_GRASS,
    LIGHT_ROAD,
    SEGMENT_LENGTH,
    WHITE_RUMBLE,
)


def build_demo_road(sprites: List[pygame.Surface]) -> List[Line]:
    lines: List[Line] = []
    for i in range(1600):
        line = Line(i)
        line.z = i * SEGMENT_LENGTH + 0.00001  # avoid Line.project() errors

        # change color at every other 3 lines (int floor division)
        line.grass_color = LIGHT_GRASS if (i // 3) % 2 else DARK_GRASS
        line.rumble_color = WHITE_RUMBLE if (i // 3) % 2 else BLACK_RUMBLE
        line.road_color = LIGHT_ROAD if (i // 3) % 2 else DARK_ROAD

        # right curve
        if 300 < i < 700:
            line.curve = 0.5

        # uphill and downhill
        if i > 750:
            line.y = math.sin(i / 30.0) * 1500

        # left curve
        if i > 1100:
            line.curve = -0.7

        # Sprites segments
        if i < 300 and i % 20 == 0:
            line.spriteX = -2.5
            line.sprite = sprites[4]

        if i % 17 == 0:
            line.spriteX = 2.0
            line.sprite = sprites[5]

        if i > 300 and i % 20 == 0:
            line.spriteX = -0.7
            line.sprite = sprites[3]

        if i > 800 and i % 20 == 0:
            line.spriteX = -1.2
            line.sprite = sprites[0]

        if i == 400:
            line.spriteX = -1.2
            line.sprite = sprites[6]

        lines.append(line)

    return lines
