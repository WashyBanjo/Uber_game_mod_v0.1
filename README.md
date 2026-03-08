# Racing Pseudo 3D in Python

## Outrun or Top Gear

Based on _"Let's make 16 games in C++: Outrun (Pseudo 3d racing)"_ https://www.youtube.com/watch?v=N60lBZDEwJ8, but adapted to Python using Pygame.

The current refactor keeps the pseudo-3D rendering path intact while moving authored road content into a graph world model.

- `road_graph.py` defines graph topology (`Node`, `Edge`, `RoadGraph`)
- `road_builder.py` authors multiple connected edges with branch-capable topology and a default route
- `route_sampler.py` traverses graph edges and supports junction continuation overrides for branch choice
- `game.py` owns graph-relative vehicle cursor state, applies left/right branch intent near junctions, and renders sampled ribbons with a toggleable minimap/debug overlay

## Run

```bash
pip install pygame==2.1.2
python src/main.py
```


Press `M` in-game to toggle the minimap/debug overlay.
