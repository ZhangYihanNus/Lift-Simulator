# Lift-Simulator


### Introduction

This repository implements a multi-elevator group control system simulator with an optimized dispatcher algorithm. 

The system manages three elevators across a 20-floor building, handling both external hall calls (up/down requests at each floor) and internal passenger requests. The core dispatcher employs a recursive assignment strategy that minimizes elevator effort by calculating the cost of each request—measuring distance, direction alignment, and idle state—then reassigning conflicting requests to ensure optimal distribution. The physics simulation models realistic elevator behavior including door state transitions, directional changes, and floor-to-floor movement, while the interactive console allows real-time request injection and system state visualization for testing and demonstration purposes.



### Running the program
```
python lift_simulator.py
```