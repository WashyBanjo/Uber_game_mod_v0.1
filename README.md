# Racing Pseudo 3D in Python

## Outrun or Top Gear

Based on _"Let's make 16 games in C++: Outrun (Pseudo 3d racing)"_ https://www.youtube.com/watch?v=N60lBZDEwJ8, but adapted to Python using Pygame.

This pass keeps the same demo behavior while restructuring the project into modules under `src/`:

- `game.py` runtime loop and player state
- `road.py` line projection/sprite drawing contract
- `road_builder.py` authored demo road generation
- `renderer.py` drawing helpers and road/sprite render path
- `assets.py` image loading
- `settings.py` constants
- `main.py` entry point

## Run

```bash
pip install pygame==2.1.2
python src/main.py
```
