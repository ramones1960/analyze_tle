import matplotlib.pyplot as plt
import os
from .logger import log

def plot_ground_track(positions, object_name):
    """
    Plots the ground track of a satellite.
    
    Args:
        positions (list): List of dictionaries containing lat/lon.
        object_name (str): Name of the satellite.
    """
    lats = [p['latitude'] for p in positions]
    lons = [p['longitude'] for p in positions]
    
    plt.figure(figsize=(10, 5))
    
    # Load or download Earth background
    # Load or download Earth background
    map_filename = os.path.join("assets", "earth_map.jpg")
    if not os.path.exists(map_filename):
        try:
            import requests # Lazy import
            log("Downloading Earth map...")
            # Use NASA Blue Marble image which is reliable
            url = "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57752/land_shallow_topo_2048.jpg"
            # headers = {'User-Agent': 'Mozilla/5.0 ...'} # NASA usually doesn't block simple agents but headers help
            headers = {'User-Agent': 'Python Satellite Tool'}
            r = requests.get(url, headers=headers)
            with open(map_filename, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            log(f"Failed to download map: {e}")
            
    if os.path.exists(map_filename):
        try:
            img = plt.imread(map_filename)
            plt.imshow(img, extent=[-180, 180, -90, 90])
        except Exception as e:
            log(f"Failed to load map image: {e}")
            
    plt.scatter(lons, lats, s=1, c='red', label='Ground Track')
    plt.title(f'Ground Track for {object_name}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    # plt.legend() # User requested to remove legend
    
    filename = f"{object_name.strip().replace(' ', '_')}_ground_track.png"
    output_path = os.path.join('output', filename)
    plt.savefig(output_path)
    log(f"Plot saved to {output_path}")
    # plt.show() # Don't show in headless/agent env usually, but we can if interactive.
    # For this agent workflow, saving is better.
