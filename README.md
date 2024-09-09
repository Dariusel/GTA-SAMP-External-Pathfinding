# GTA-SAMP-External Pathfinding

This project provides an external pathfinding solution for GTA San Andreas Multiplayer (GTA-SAMP). It includes a GUI that displays and controls the pathfinding algorithm, which currently supports Dijkstra's algorithm, with plans to add A* in the future. The application reads memory from `gta_sa.exe` to determine the player's position and vehicle orientation, then automatically pathfinds and drives the vehicle to the desired destination.

## Features

- **Graphical User Interface (GUI)**: Easily interact with the pathfinding algorithms.
- **Directed Pathfinding Algorithms**: 
  - **Dijkstra's Algorithm**: Currently implemented for finding the shortest path.
  - **A\***: Planned for future implementation.
- **Memory Reading**: Reads the position and vehicle orientation directly from the `gta_sa.exe` memory.
- **Automatic Undetectable Driving**: Simulates key presses using Windows API to drive the vehicle to the destination.

## Prerequisites
- **Python 3.12.5**: Other versions have not been tested yet.

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

4. **Run the program as much as you want**:
   ```sh
   python main.py

## Other Info
- **Blip Memory Reading Temporary Fix**: I haven't yet found the memory address of the Blip Coordinates in the game memory yet. A workaround is storing the memory address of the blip position with a custom CLEO Mod. For blip functions to work follow these steps:
   **1. Install CLEO to your GTA:SA Directory**: CLEO is a GTA:SA modding framework, follow steps online for this installation.
   **2. Extract `external_pathfinding.cs` to CLEO folder**: You can find this file inside `GTA-SAMP-External-Pathfinding/resources/cleo/external_pathfinding.cs`.
   **3. Enable GPS Blip inside code**: Open `GTA-SAMP-External-Pathfinding/resources/utils/memory/memory_adresses.py` and change `TEMP_GPS_ENABLED = True`.
