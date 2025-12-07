# Project Overview: Satellite Orbit Visualization Tool

## 1. Project Summary
This project is a Python-based application designed to track and visualize satellite orbits in real-time or for a specified duration using Two-Line Element (TLE) sets. It generates interactive 3D/2D visualizations (HTML) and static ground tracks (PNG).

## 2. Directory Structure
```
ana_TLE/
├── assets/                 # Static resources (e.g., Earth maps)
├── config/                 # Configuration files
│   └── stations.csv        # Ground Station coordinates
├── data/                   # Data files
│   └── sample.tle          # Fallback TLE data
├── docs/                   # Documentation
│   ├── PROJECT_OVERVIEW.md
│   └── DETAILED_SPEC.md
├── logs/                   # Log files
├── output/                 # Generated files (HTML, PNG)
├── src/                    # Source Code
│   ├── data_fetcher.py     
│   ├── orbit_propagator.py 
│   ├── visualizer.py       
│   ├── plotter.py          
│   └── logger.py           
├── tests/                  # Unit Tests
├── main.py                 # CLI Entry Point
├── requirements.txt        # Python dependencies
└── venv/                   # Virtual Environment
```

## 3. Module & Class Structure

### Core Modules
*   **`main.py`**: The command-line interface (CLI) entry point. Handles parsing arguments, invoking TLE fetching, propagation, and visualization.
    *   **Commands**: `track` (Visualizes orbit), `search` (Finds launches).

*   **`src.data_fetcher`**: Handles network requests to retrieve TLE data.
    *   `get_tle_by_intdes(int_designator)`: Fetches TLE from CelesTrak.
    *   `search_launches(date)`: Searches for satellite launches.

*   **`src.orbit_propagator`**: Responsible for the physics and math of orbit prediction using `skyfield` (SGP4).
    *   `propagate_orbit(tle_line1, tle_line2, start_time, duration, step)`: Calculates satellite positions (Lat, Lon, Alt, ECI, ECEF) over time. Returns a list of state vectors.

*   **`src.visualizer`**: Generates high-quality interactive visualizations using `plotly`.
    *   `create_animation(positions, object_name, tle_epoch, stations)`: Builds the HTML file containing:
        *   **2D Map**: Equirectangular projection with ground track, current position, and ground stations.
        *   **3D Globe**: Orthographic projection with real-time satellite movement.
        *   **Features**: Time sliders, Play/Pause controls, "UTCG" time formatting.

*   **`src.plotter`**: Generates static 2D ground track images using `matplotlib` and `cartopy`.
    *   `plot_ground_track(df, object_name)`: Saves a `.png` image of the orbit path.

*   **`src.logger`**: Provides a centralized logging function.
    *   `log(message)`: Prints timestamped messages to console.

## 4. Key Dependencies
*   **`skyfield`**: For high-precision TLE propagation and coordinate transformations.
*   **`plotly`**: For generating interactive web-based visualizations.
*   **`pandas`**: For efficient data handling of time-series orbital data.
*   **`requests`**: For API interactions with CelesTrak.
*   **`numpy`**: For numerical operations.
