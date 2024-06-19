# GTA-SAMP-External Pathfinding

This project provides an external pathfinding solution for GTA San Andreas Multiplayer (GTA-SAMP). It includes a GUI that displays and controls the pathfinding algorithm, which currently supports Dijkstra's algorithm, with plans to add A* in the future. The application reads memory from `gta_sa.exe` to determine the player's position and vehicle orientation, then automatically pathfinds and drives the vehicle to the desired destination.

## Features

- **Graphical User Interface (GUI)**: Easily interact with the pathfinding algorithms.
- **Pathfinding Algorithms**: 
  - **Dijkstra's Algorithm**: Currently implemented for finding the shortest path.
  - **A\***: Planned for future implementation.
- **Memory Reading**: Reads the position and vehicle orientation directly from the `gta_sa.exe` memory.
- **Automatic Driving**: Automatically drives the vehicle to the destination based on the pathfinding results.

## Installation

### Prerequisites

- Python 3.x
- Required Python libraries (listed in `requirements.txt`)

### Steps

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/GTA-SAMP-External-Pathfinding.git
   cd GTA-SAMP-External-Pathfinding
