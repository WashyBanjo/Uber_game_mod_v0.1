# Racing Pseudo 3D in Python

## Outrun or Top Gear

Based on _"Let's make 16 games in C++: Outrun (Pseudo 3d racing)"_ https://www.youtube.com/watch?v=N60lBZDEwJ8, but adapted to Python using Pygame.

The current refactor keeps the pseudo-3D rendering path intact while moving authored road content into a graph world model.

- `road_graph.py` defines graph topology (`Node`, `Edge`, `RoadGraph`)
- `road_builder.py` authors multiple connected edges with branch-capable topology and a default route
- `game.py` still flattens the default route into an ordered line ribbon for the existing renderer contract

## Run

```bash
pip install pygame==2.1.2
python src/main.py
```
