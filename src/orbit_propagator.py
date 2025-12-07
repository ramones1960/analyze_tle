from skyfield.api import EarthSatellite, load, wgs84
import datetime
import numpy as np

def propagate_orbit(tle_line1, tle_line2, step_seconds=600.0, step_count=144, satellite_name='Satellite', start_time=None):
    """
    Propagates the orbit of a satellite using TLE data.
    
    Args:
        tle_line1 (str): Line 1 of the TLE.
        tle_line2 (str): Line 2 of the TLE.
        step_seconds (float): Time step in seconds.
        step_count (int): Number of steps to propagate.
        satellite_name (str): Name of the satellite.
        start_time (datetime, optional): Start time for propagation. Defaults to now.
        
    Returns:
        list: List of dictionaries containing time, lat, lon, alt.
    """
    ts = load.timescale()
    satellite = EarthSatellite(tle_line1, tle_line2, satellite_name, ts)
    
    if start_time is None:
        start_time = ts.now()
    else:
        # Check if it's already a Time object or datetime
        if not hasattr(start_time, 'utc_datetime'):
            # Assume datetime
            # Ensure timezone awareness
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)
            start_time = ts.from_datetime(start_time)

    current_dt = start_time.utc_datetime()
    
    # Ensure current_dt is strictly timezone aware
    if current_dt.tzinfo is None:
        current_dt = current_dt.replace(tzinfo=datetime.timezone.utc)
        
    # Create time steps
    steps = np.arange(step_count) * step_seconds
    # Create list of datetimes (list comprehension is fast for this size)
    times_dt = [current_dt + datetime.timedelta(seconds=float(s)) for s in steps]
    
    # Vectorized propagation
    ts_times = ts.from_datetimes(times_dt)
    geocentric = satellite.at(ts_times)
    subpoint = wgs84.subpoint_of(geocentric)
    
    lats = subpoint.latitude.degrees
    lons = subpoint.longitude.degrees
    alts = subpoint.elevation.km
    
    # Fallback if altitude is 0 (Skyfield issue)
    # WGS84 Semi-major axis approx 6378.137 km
    EARTH_RADIUS_KM = 6378.137
    
    # Check if alts are all zeros (allow for small epsilon)
    # Using simple heuristic: if max alt is < 1 km and radius is > 6500, something is wrong.
    # We can check distance magnitude.
    r_km = np.sqrt(np.sum(geocentric.position.km**2, axis=0))
    
    # If using numpy arrays
    if np.any(r_km > 6500) and np.all(np.abs(alts) < 1.0):
       # Calculate simple altitude
       alts = r_km - EARTH_RADIUS_KM
       
    # Helper to ensure array if scalar (e.g., single point)
    if np.ndim(alts) == 0:
        alts = np.full(lats.shape, alts)
        
    # Extract 3D Coordinates
    # ECI (GCRS via Skyfield)
    eci_xyz = geocentric.position.km
    x_eci, y_eci, z_eci = eci_xyz[0], eci_xyz[1], eci_xyz[2]
    
    # ECEF (ITRS via subpoint result)
    # subpoint is a GeographicPosition which wraps ITRS
    ecef_xyz = subpoint.itrs_xyz.km
    x_ecef, y_ecef, z_ecef = ecef_xyz[0], ecef_xyz[1], ecef_xyz[2]
    
    # Ensure all are arrays for generic handling if scalar
    if np.ndim(x_eci) == 0:
        x_eci = np.full(lats.shape, x_eci)
        y_eci = np.full(lats.shape, y_eci)
        z_eci = np.full(lats.shape, z_eci)
        x_ecef = np.full(lats.shape, x_ecef)
        y_ecef = np.full(lats.shape, y_ecef)
        z_ecef = np.full(lats.shape, z_ecef)

    # Reassemble results
    # Using list comprehension for speed
    results = [
        {
            'time': dt,
            'latitude': lat,
            'longitude': lon,
            'altitude_km': alt,
            'eci': {'x': xe, 'y': ye, 'z': ze},
            'ecef': {'x': xf, 'y': yf, 'z': zf}
        }
        for dt, lat, lon, alt, xe, ye, ze, xf, yf, zf in zip(times_dt, lats, lons, alts, x_eci, y_eci, z_eci, x_ecef, y_ecef, z_ecef)
    ]

    return results, satellite.epoch.utc_jpl()
