import time
import sys
from dataclasses import dataclass
from typing import List, Set, Tuple, Dict
from enum import Enum

# --- 1. Defaults and basics ---
class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class DoorState(Enum):
    CLOSED = 0
    OPENED = 1

@dataclass
class ElevatorSnapshot:
    id: int
    current_floor: int
    current_direction: Direction
    door_state: DoorState
    internal_buttons: Set[int]

MAX_FLOOR = 20
MIN_FLOOR = 1
NUM_ELEVATOR = 3


"""
# Assign hall calls to elevators
"""
def split_hall_calls_for_elevator(
        elevators: List[ElevatorSnapshot], 
        hall_calls: Set[Tuple[int, Direction]], 
        hall_calls_for_elevator: List[Set[Tuple[int, Direction]]],
        max_depth: int
        ) -> List[Set[Tuple[int, Direction]]]:
    
    # Update hall_calls_for_elevator
    for hall_call in hall_calls:
        min_effort_elevator = decide_elevator(elevators, hall_call, hall_calls_for_elevator)
        if len(hall_calls_for_elevator[min_effort_elevator]) == 0 or max_depth >= 5:
            hall_calls_for_elevator[min_effort_elevator].add(hall_call)
        else:
            copied_set = hall_calls_for_elevator[min_effort_elevator].copy()
            hall_calls_for_elevator[min_effort_elevator] = set()
            hall_calls_for_elevator[min_effort_elevator].add(hall_call)

            # For the other external requests in the target elevator, re-evaluate their optimal assignment. 
            # If the conclusion remains unchanged, keep them; 
            # otherwise, recursively verify the other requests assigned to the newly assigned elevator.
            to_double_check = []
            for hc in copied_set:
                updated_elevator = decide_elevator(elevators, hc, hall_calls_for_elevator)
                if updated_elevator == min_effort_elevator:
                    hall_calls_for_elevator[min_effort_elevator].add(hc)
                else:
                    to_double_check.append(hc)
            
            split_hall_calls_for_elevator(elevators, to_double_check, hall_calls_for_elevator, max_depth+1)

    return hall_calls_for_elevator

"""
# Assign one hall call to an elevator
"""
def decide_elevator(elevators: List[ElevatorSnapshot], hall_call: Tuple[int, Direction], hall_calls_for_elevator: List[Set[Tuple[int, Direction]]]):
    floor, direction = hall_call
    # Calculate each elevator's effort to handle this hall_call
    # Assign hall_call to the elevator with minimum effort
    min_effort = MAX_FLOOR + 2
    min_effort_elevator = 0
    for i, elevator in enumerate(elevators):
        if elevator.current_floor == floor and elevator.current_direction == direction:
            # Elevator and external request are on the same floor and moving in the same direction --> effort is 0, open door directly
            effort = 0
        elif (elevator.current_floor < floor and elevator.current_direction == Direction.UP) \
            or (elevator.current_floor > floor and elevator.current_direction == Direction.DOWN):
            # Elevator and external request are moving in the same direction but not yet arrived --> difference in floors = effort
            effort = abs(elevator.current_floor - floor)
        elif (elevator.current_direction == Direction.IDLE):
            # Elevator is idle --> difference in floors + 1 = effort (simulate startup delay)
            effort = abs(elevator.current_floor - floor) + 1
        else:
            # Elevator and external request are moving in opposite directions --> elevator reaches furthest target floor + distance from furthest target to external request = effort
            furthest_floor = find_furthest_target_floor(elevator, hall_calls_for_elevator[i])
            effort = abs(elevator.current_floor - furthest_floor) + abs(floor - furthest_floor) + 1
            
        if effort < min_effort:
            min_effort = effort
            min_effort_elevator = i
        if effort == min_effort and len(hall_calls_for_elevator[i]) < len(hall_calls_for_elevator[min_effort_elevator]):
            min_effort_elevator = i
    return min_effort_elevator

"""
# Find the furthest target floor in the elevator's current direction
# Used to calculate the difficulty of picking up requests in the opposite direction
"""
def find_furthest_target_floor(elevator: ElevatorSnapshot, my_hall_calls: Set[Tuple[int, Direction]]):
    if elevator.current_direction == Direction.UP:
        higher_hc = {hc for hc in my_hall_calls if hc[0] > elevator.current_floor}
        if len(higher_hc) == 0:
            furthest = elevator.current_floor
        else:
            furthest = max(higher_hc, key=lambda hc: (hc[0]-elevator.current_floor))[0]
        
        if len(elevator.internal_buttons) == 0:
            return furthest
        else:
            return max(furthest, max(elevator.internal_buttons))
    elif elevator.current_direction == Direction.DOWN:
        lower_hc = {hc for hc in my_hall_calls if hc[0] < elevator.current_floor}
        if len(lower_hc) == 0:
            furthest = elevator.current_floor
        else:
            furthest = max(lower_hc, key=lambda hc: (elevator.current_floor-hc[0]))[0]
        
        if len(elevator.internal_buttons) == 0:
            return furthest
        else:
            return min(furthest, min(elevator.internal_buttons))
    else:
        raise(RuntimeError)



# --- 2. Core algorithms ---
class GroupElevatorAlgorithm:
    def __init__(self, num_elevators):
        self.num_elevators = num_elevators
    """
    # Decide the next action for a single elevator
    """
    def decide_next_action(self, state: ElevatorSnapshot, my_hall_calls: Set[Tuple[int, Direction]]) -> Direction:
        if len(my_hall_calls) == 0 and len(state.internal_buttons) == 0:
            return Direction.IDLE
        if state.current_direction == Direction.IDLE:
            target_floors = {call[0] for call in my_hall_calls} | state.internal_buttons
            nearest_floor = sorted(target_floors, key=lambda x: abs(x - state.current_floor))[0] 
            if nearest_floor < state.current_floor: 
                return Direction.DOWN
            else: 
                return Direction.UP
        elif state.current_direction == Direction.UP:
            # 1. Check if there are calls from above
            has_upper_task = False
            for call in my_hall_calls:
                if call[0] > state.current_floor: has_upper_task = True
            for button in state.internal_buttons:
                if button > state.current_floor: has_upper_task = True
            
            if has_upper_task:
                return Direction.UP

            # 2. No calls from above, check if there are calls from below
            has_lower_task = False
            for call in my_hall_calls:
                if call[0] < state.current_floor: has_lower_task = True
            for button in state.internal_buttons:
                if button < state.current_floor: has_lower_task = True
                
            if has_lower_task:
                return Direction.DOWN   # Turn around directly, no IDLE in between
            
            return Direction.IDLE
        else:
            # 1. Check if there are calls from below
            has_lower_task = False
            for call in my_hall_calls:
                if call[0] < state.current_floor: has_lower_task = True
            for button in state.internal_buttons:
                if button < state.current_floor: has_lower_task = True

            if has_lower_task:
                return Direction.DOWN

            # 2. No calls from below, check if there are calls from above
            has_upper_task = False
            for call in my_hall_calls:
                if call[0] > state.current_floor: has_upper_task = True
            for button in state.internal_buttons:
                if button > state.current_floor: has_upper_task = True
                
            if has_upper_task:
                return Direction.UP     # Turn around directly, no IDLE in between
            
            return Direction.IDLE

    """
    # Decide the next action for all elevators
    """
    def decide_next_action_for_all(self, elevators: List[ElevatorSnapshot], hall_calls: Set[Tuple[int, Direction]], hall_calls_for_elevators: List[Set[Tuple[int, Direction]]]) -> List[Direction]:     
        results = []

        # 1. Assign hall_calls for all elevators - hall_calls_for_elevator
        hall_calls_for_elevator = split_hall_calls_for_elevator(elevators, hall_calls, [set() for _ in range(NUM_ELEVATOR)], 0)
        
        # 2. Each elevator decides next_dir based on its own hall_calls_for_elevator and state
        for i, state in enumerate(elevators):
            next_dir = self.decide_next_action(state, hall_calls_for_elevator[i])
            results.append(next_dir)

        return results


# --- 3. Elevator simulation engine ---
class ElevatorPhysics:
    def __init__(self, elevator_id, hall_calls_ref, min_floor=MIN_FLOOR, max_floor=MAX_FLOOR, internal_buttons=None):
        self.id = elevator_id
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.door_state = DoorState.CLOSED
        if internal_buttons is None:
            self.internal_buttons = set()
        else:
            self.internal_buttons = internal_buttons
        self.hall_calls = hall_calls_ref 
        
    def add_internal_request(self, floor):
        if self.min_floor <= floor <= self.max_floor:
            self.internal_buttons.add(floor)
            return True
        return False

    def get_snapshot(self):
        return ElevatorSnapshot(
            id=self.id,
            current_floor=self.current_floor,
            current_direction=self.direction,
            door_state=self.door_state,
            internal_buttons=self.internal_buttons.copy()
        )

    def print_status(self):
        print(f"E{self.id} | Floor: {self.current_floor} | Dir: {self.direction.name} | Door: {self.door_state.name} | Internal: {self.internal_buttons}")

    def tick(self, next_direction_command):
        # 1. Check if the door should open
        should_open = False
        
        # A. Internal passengers arrive
        if self.current_floor in self.internal_buttons:
            should_open = True
            self.internal_buttons.remove(self.current_floor)
            print(f"Elevator {self.id} reached target floor: {self.current_floor} | request: elevator {self.id} internal")
            
        # B. External calls arrived
        # If the elevator reaches a floor and the direction matches (or is idle), pick up all requests in that direction
        # Note: This modifies the global hall_calls, simulating "lights going out" after a request is picked up
        to_remove = set()
        for call in self.hall_calls:
            floor, req_dir = call
            if floor == self.current_floor:
                # self.print_status()
                # Logic: elevator is idle, or elevator is going the same direction, or elevator is about to stop (IDLE)
                if self.direction == Direction.IDLE or req_dir == self.direction or next_direction_command == Direction.IDLE:
                    should_open = True
                    to_remove.add(call)
        
        # Remove the picked-up calls from the global list
        for item in to_remove:
            if item in self.hall_calls:
                self.hall_calls.remove(item)
                print(f"Elevator {self.id} reached target floor: {item[0]} | request: external, {item[0]}{item[1].name[0]}")

        # 2. State transitions: open/close door
        if should_open:
            # self.print_status()
            self.door_state = DoorState.OPENED
            self.direction = Direction.IDLE 
            return 
        if self.door_state == DoorState.OPENED:
            self.door_state = DoorState.CLOSED
            self.direction = next_direction_command
            return

        # 3. Move elevator
        if self.door_state == DoorState.CLOSED:
            self.direction = next_direction_command
            if self.direction == Direction.UP and self.current_floor < self.max_floor:
                self.current_floor += 1
            elif self.direction == Direction.DOWN and self.current_floor > self.min_floor:
                self.current_floor -= 1


# --- 4. Interactive Console ---
def print_dashboard(tick, elevators_state, hall_calls, hall_calls_for_elevators, last_decisions):
    print("-"*109)
    print(f" ⏱️  TICK: {tick}")
    print(f" 🌍 External hall calls: {[f'{f}{d.name[0]}' for f, d in sorted(hall_calls, key=lambda hc: hc[0])]}")
    print(f'Assigned Hall calls: {[f"{[f'{fl}{dr.name[0]}' for fl, dr in sorted(hall_calls_for_elevators[i], key=lambda hc: hc[0])]}" for i in range(3)]}')
    print("-" * 109)
    
    # Print format： | E1: 1F [IDLE] | E2: 5F [UP] | ...
    header = ""
    status_line = ""
    internal_line = ""
    external_line = ""
    decision_line = ""
    
    for i, state in enumerate(elevators_state):
        name = f"E{i}"
        d_icon = "⬆️" if state.current_direction == Direction.UP else ("⬇️" if state.current_direction == Direction.DOWN else "⏹️")
        door = "🚪" if state.door_state == DoorState.OPENED else "🧱"
        
        header += f"| {name.center(33)} "
        status_line += f"| {str(state.current_floor).rjust(2)}F {d_icon} {door} {state.door_state.name[:].ljust(24)} "
        internal_line += f"| In:{str(list(state.internal_buttons)).ljust(30)} "
        external_line += f"| Ex:{str([f'{fl}{dr.name[0]}' for fl, dr in hall_calls_for_elevators[i]]).ljust(31)}"
        
        dec = last_decisions[i].name if last_decisions else "None"
        decision_line += f"| Cmd: {dec.ljust(28)} "

    print(header + "|")
    print(status_line + "|")
    print(internal_line + "|")
    print(external_line + "|")
    print(decision_line + "|")
    print("="*109)

def parse_input(physics_list, hall_calls):
    print("Command: [ENTER] next tick | [5u] level 5 press up | [3d] level 3 press down | [1:5] elevator 1 to floor 5 | [q] quit program")
    
    while True:
        raw = input("👉 Command: ").strip().lower()
        if raw == 'q': sys.exit(0)
        if raw == '': break 
            
        cmds = raw.split()
        for cmd in cmds:
            try:
                if ':' in cmd:
                    e_idx, floor = cmd.split(':')
                    e_idx = int(e_idx) - 1
                    floor = int(floor)
                    if 0 <= e_idx < len(physics_list):
                        physics_list[e_idx].add_internal_request(floor)
                        print(f"  ✅ E{e_idx+1} internal call: floor {floor}")

                elif cmd.endswith('u'):
                    floor = int(cmd[:-1])
                    hall_calls.add((floor, Direction.UP))
                    print(f"  ✅ Building {floor} floor pressed up")
                elif cmd.endswith('d'):
                    floor = int(cmd[:-1])
                    hall_calls.add((floor, Direction.DOWN))
                    print(f"  ✅ Building {floor} floor pressed down")
            except:
                print(f"  ❌ Invalid command: {cmd}")

def run_interactive_simulation():
    # Global predefined external hall calls
    hall_calls = set()
    hall_calls.add((3, Direction.UP))
    hall_calls.add((6, Direction.DOWN))
    hall_calls.add((4, Direction.DOWN))
    hall_calls.add((5, Direction.DOWN))
    hall_calls.add((9, Direction.DOWN))
    hall_calls.add((9, Direction.UP))
    hall_calls.add((11, Direction.DOWN))
    
    elevators = [
        ElevatorPhysics(1, hall_calls, max_floor=MAX_FLOOR, min_floor=MIN_FLOOR),
        ElevatorPhysics(2, hall_calls, max_floor=MAX_FLOOR, min_floor=MIN_FLOOR, internal_buttons={6, 10}),
        ElevatorPhysics(3, hall_calls, max_floor=MAX_FLOOR, min_floor=MIN_FLOOR)
    ]
    assert len(elevators) == NUM_ELEVATOR
    
    algorithm = GroupElevatorAlgorithm(num_elevators=NUM_ELEVATOR)
    tick_count = 0
    last_decisions = []

    while True:
        # 1. Get all elevators' snapshots
        snapshots = [e.get_snapshot() for e in elevators]
        
        # 2. Display dashboard
        hall_calls_for_elevators = split_hall_calls_for_elevator(snapshots, hall_calls, [set() for _ in range(NUM_ELEVATOR)], 0)
        print_dashboard(tick_count, snapshots, hall_calls, hall_calls_for_elevators, last_decisions)
        
        # 3. Interactive input
        parse_input(elevators, hall_calls)
        
        # 4. Get snapshots again
        snapshots = [e.get_snapshot() for e in elevators]
        
        # 5. Algorithm decision
        hall_calls_for_elevators = split_hall_calls_for_elevator(snapshots, hall_calls, [set() for _ in range(NUM_ELEVATOR)], 0)
        last_decisions = algorithm.decide_next_action_for_all(snapshots, hall_calls, hall_calls_for_elevators)
        
        # 6. Physics simulation
        print("\n" + "="*109)
        print("="*109)
        for i, e in enumerate(elevators):
            e.tick(last_decisions[i])
        
        tick_count += 1

if __name__ == "__main__":
    run_interactive_simulation()
