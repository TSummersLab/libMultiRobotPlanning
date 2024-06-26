[![Build](https://github.com/whoenig/libMultiRobotPlanning/actions/workflows/build.yml/badge.svg)](https://github.com/whoenig/libMultiRobotPlanning/actions/workflows/build.yml)

# libMultiRobotPlanning

libMultiRobotPlanning is a library with search algorithms primarily for task and path planning for multi robot/agent systems.
It is written in C++(14), highly templated for good performance, and comes with useful examples.

The following algorithms are currently supported:

* Single-Robot Algorithms
  * A*
  * A* epsilon (also known as focal search)
  * SIPP (Safe Interval Path Planning)

* Multi-Robot Algorithms
  * Conflict-Based Search (CBS)
  * Enhanced Conflict-Based Search (ECBS)
  * Conflict-Based Search with Optimal Task Assignment (CBS-TA)
  * Enhanced Conflict-Based Search with Optimal Task Assignment (ECBS-TA)
  * Prioritized Planning using SIPP (example code for SIPP)

* Assignment Algorithms
  * Minimum sum-of-cost (flow-based; integer costs; any number of agents/tasks)
  * Best Next Assignment (series of optimal solutions)

## Building

Tested on Ubuntu 22.04.
Originally tested on Ubuntu 16.04.

```
mkdir build
cd build
cmake ..
make
```

Note: To generate videos, `ffmpeg` is required.
Install with `sudo apt install ffmpeg`

### Targets

* `make`: Build examples, only
* `make docs`: build doxygen documentation
* `make clang-format`: Re-format all source files
* `make clang-tidy`: Run linter & static code analyzer
* `make run-test`: Run unit-tests

## Run specific tests

```
python3 ../test/test_next_best_assignment.py TestNextBestAssignment.test_1by2
```

## Run example instances

### ECBS

````
./ecbs -i ../benchmark/32x32_obst204/map_32by32_obst204_agents10_ex1.yaml -o output.yaml -w 1.3
python3 ../example/visualize.py ../benchmark/32x32_obst204/map_32by32_obst204_agents10_ex1.yaml output.yaml
````

### Generalized Roadmaps

CBS works on generalized graphs, with a particular focus on optional wait actions (e.g., this can be used with motion primitives as well).
However, the roadmap annotation and visualization step currently assume a 2D Euclidean embedding and straight-line edges.

```
python3 ../tools/annotate_roadmap.py ../test/mapf_simple1_roadmap_to_annotate.yaml mapf_simple1_roadmap_annotated.yaml
./cbs_roadmap -i mapf_simple1_roadmap_annotated.yaml -o output.yaml
python3 ../example/visualize_roadmap.py mapf_simple1_roadmap_annotated.yaml output.yaml
```

# MAPF Demo
The `demo` directory contains some demo code targeting the TurtleBot platform.
To run the demo, follow these steps.
1. Build the `libMultiRobotPlanning` package as described above. 
2. (Optional) Add a scenario by creating a folder in `demo/scenarios` and add the `agents.txt` and `env.txt` files.
3. Set the scenario name in the `demo/mapf.py` script by editing the `rel_path` variable.
4. Run the `mapf.py` script. This will generate the schedule and the video visualization.

Once `mapf.py` executes, it will output the trajectories and indicate if planning for any of the robots failed (they will be kept in place which causes collisions since other agents will ignore them).
The script will also save a video (optional) of the solution and two schedule text files: `schedule.txt` and `schedule_global.txt`.
Both text files contain the same information, but the difference is in the coordinate frames.
- `schedule.txt` is with respect to the grid in which the planning happened, so all values will correspond to cell indices.
- `scehdule_global.txt` transforms the data in `schedule.txt` to a real world global coordinate frame where the center is placed at one of the grid's corners and the cells of the grid are mapped to a square region in the real world global coordinate frame whose size is given in meters.

The latter is useful when, for example, using the schedule to operate physical robots in a motion capture environment. 

---
**NOTE**

The `agents.txt` file should contain the start and goal locations of the agents organized as follows:
```
sx0, sy0, gx0, gy0
sx1, sy1, gx1, gy1
...
```
where `(sx0, sy0), (gx0, gy0)` are the start and end `(x,y)` position of agent0 and similarly for other agents.

The `env.txt` file should contain the size of the grid and the location of the obstacle organized as follows:
```
m, n
x0, y0
x1, y1
...
```
where `m, n` is the size of the map and `(x0, y0)` is the position of obstacle0 and similarly for other agents.

The start, goal, and obstacle locations are the indices of the cells in the `m x n` grid. The MAPF problem will be solved in this discrete environment.

Converting to a global coordinate frame is done through the `transform_coordinates_to_world` function in `demo/mapf.py`.  

Also, no empty lines are allowed (even at the end of the file).

---


