# Lift-Simulator

## Overview

Lift-Simulator is a Python-based simulation of a multi-elevator control system for a 20-floor building. The simulator models three elevators and uses an optimized dispatcher algorithm to assign hall (external) and internal passenger requests efficiently.

### Features

- **Multi-elevator dispatching:** Assigns hall calls to elevators based on a cost function considering distance, direction, and idle status.
- **Recursive assignment:** Reassigns conflicting requests to optimize elevator workload distribution.
- **Realistic elevator physics:** Simulates elevator movement, door operations, and direction changes.
- **Interactive console:** Allows users to inject requests and observe elevator states in real time.

### How It Works

- **Elevator Assignment:** The dispatcher algorithm calculates the best elevator for each hall call, minimizing total effort and travel.
- **Simulation Engine:** Each elevator processes requests, moves between floors, and opens/closes doors according to its assigned tasks.
- **User Interaction:** Users can input commands to simulate hall calls (up/down requests at floors) and internal requests (passenger destinations).

### Running the Simulator

1. **Requirements:**  
   - Python 3.x

2. **Start the simulation:**  
   Open a terminal in the project directory and run:
   ```
   python lift_simulator.py
   ```

3. **Interactive Commands:**  
   - `[ENTER]` : Advance simulation by one tick  
   - `[5u]` : Hall call for up at floor 5  
   - `[3d]` : Hall call for down at floor 3  
   - `[1:5]` : Internal request for elevator 1 to go to floor 5  
   - `[q]` : Quit the program

The dashboard displays elevator positions, directions, door states, and assigned requests at each tick.

---