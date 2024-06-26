# GTA-SAMP-External Pathfinding

This project provides an external pathfinding solution for GTA San Andreas Multiplayer (GTA-SAMP). It includes a GUI that displays and controls the pathfinding algorithm, which currently supports Dijkstra's algorithm, with plans to add A* in the future. The application reads memory from `gta_sa.exe` to determine the player's position and vehicle orientation, then automatically pathfinds and drives the vehicle to the desired destination.

## Features

- **Graphical User Interface (GUI)**: Easily interact with the pathfinding algorithms.
- **Directed Pathfinding Algorithms**: 
  - **Dijkstra's Algorithm**: Currently implemented for finding the shortest path.
  - **A\***: Planned for future implementation.
- **Memory Reading**: Reads the position and vehicle orientation directly from the `gta_sa.exe` memory.
- **Automatic Undetectable Driving**: Simulates key presses using Windows API to drive the vehicle to the destination.

## Installation Steps

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/GTA-SAMP-External-Pathfinding.git
   cd GTA-SAMP-External-Pathfinding

2. **Activate virtual enviroment**:
   ```sh
   call env/scripts/activate
Or just run `terminal.bat` and it will automatically activate venv.

3. **Install requirements**:
   ```sh
   pip install -r requirements.txt

4. **Run**:
   ```sh
   python main.py
