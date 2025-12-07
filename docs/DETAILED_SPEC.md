# detailed Program Specification

## 1. System Requirements
*   **Language**: Python 3.8+
*   **Dependencies**: Listed in `requirements.txt`
    *   `skyfield`
    *   `plotly`
    *   `pandas`
    *   `requests`
    *   `numpy`
    *   `matplotlib`
    *   `cartopy` (optional, for static plots)

## 2. CLI Interface (`main.py`)
The application is executed via the command line.

### Global Arguments
*   `--help`: Show help message.

### Command: `track`
Visualizes the orbit of a specific satellite.

**Usage**:
```bash
python main.py track <INT_DES> [OPTIONS]
```

**Arguments**:
*   `INT_DES` (Positional): International Designator (e.g., `2025-241A`) or NORAD ID.
*   `-s`, `--step` (Optional): Time step in seconds for propagation (Default: `60`).
*   `-c`, `--count` (Optional): Number of steps to propagate (Default: `1440` = 24 hours).
*   `--stations` (Optional): Path to CSV file containing ground station coordinates (e.g., `config/stations.csv`).
*   `--tle-file` (Optional): Path to a local file containing TLE data (e.g., `data/sample.tle`).

**Example**:
```bash
python main.py track 2025-241A -c 1440 -s 60 --stations config/stations.csv
```

### Command: `search`
Searches for satellite launches near a specific date.

**Usage**:
```bash
python main.py search --date <YYYY-MM-DD>
```

**Arguments**:
*   `--date`: The target date for the search.

## 3. Functional Specifications

### 3.1. TLE Loading
*   **Source Priority**:
    1.  **Local File**: If `--tle-file` is specified, the application reads the first 3 lines (Name, Line 1, Line 2) from the file.
    2.  **CelesTrak API**: If no file is provided, it queries `https://celestrak.org/NORAD/elements/gp.php` using the International Designator.
*   **Retry Logic**: The fetcher implements a retry mechanism (3 attempts with 2s delay) for network resilience.

### 3.2. Orbit Propagation (`orbit_propagator.py`)
*   **Algorithm**: SGP4 (via `skyfield`).
*   **Input**: TLE (Two-Line Element) set.
*   **Process**:
    1.  Initializes a `skyfield.EarthSatellite` object.
    2.  Generates a time array from `now` to `now + (count * step)`.
    3.  Computes position vectors for each time step.
*   **Calculated Data**:
    *   **Time**: UTC string (formatted as `UTCG`).
    *   **Geocentric Coordinates**: Latitude, Longitude, Altitude (km).
    *   **Inertial Frame (ECI)**: X, Y, Z coordinates (km) - *Internal use*.
    *   **Earth-Fixed Frame (ECEF)**: X, Y, Z coordinates (km) - *Internal use*.
*   **Output**: A list of dictionaries containing the calculated state for each time step.

### 3.3. Visualization (`visualizer.py`)
*   **Technology**: Plotly Graph Objects (`plotly.graph_objects`).
*   **Output Location**: `output/` directory.
*   **Layout**: `1x2` Subplot Grid.
    *   **Left Panel**: 2D Map (`scattergeo`, equirectangular projection).
    *   **Right Panel**: 3D Globe (`scattergeo`, orthographic projection).
*   **Components**:
    *   **Ground Track**: Continuous line showing the satellite's path history/future.
    *   **Satellite Marker**: Animated marker showing real-time position. 
        *   Color: Cyan (3D Globe), Red (2D Map).
    *   **Ground Stations**: Markers loaded from CSV.
        *   Color: Magenta (Globe), Green (2D Map).
        *   Labels: Station Name.
    *   **Grid Lines**: Custom latitude/longitude grid lines and labels.
*   **Interactivity**:
    *   **Zoom/Pan**: Enabled (`uirevision="constant"`).
    *   **Animation**: Play/Pause buttons, Time Slider.
    *   **Title Bar**: Displays Satellite Name, TLE Epoch, Current UTCG Time, and Lat/Lon.

### 3.4. Static Plotting (`plotter.py`)
*   **Output**: A static `.png` image saved to `output/` directory.
*   **Background**: Uses `assets/earth_map.jpg` (downloads if missing).

## 4. Data Formats

### 4.1. Ground Stations CSV (`stations.csv`)
Requires a header row.
```csv
name,lat,lon
Masuda,30.5530,131.0130
Katsuura,35.1594,140.3150
...
```

### 4.2. Local TLE File (`.tle`)
Standard 3-line format (Name + 2 TLE lines).
```
ISS (ZARYA)
1 25544U 98067A   24339.54842275  .00010486  00000+0  19195-3 0  9997
2 25544  51.6396 237.4083 0006456  64.5028  46.7977 15.49884501485002
```
