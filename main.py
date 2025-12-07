import argparse
import sys
import json
from src.data_fetcher import get_launches_by_date, get_tle_by_intdes
from src.orbit_propagator import propagate_orbit
from src.plotter import plot_ground_track
from src.visualizer import create_animation
from src.logger import log

def main():
    parser = argparse.ArgumentParser(description='Satellite Orbit Analysis Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Command 1: List launches
    parser_search = subparsers.add_parser('search', help='Search for launches on a specific date')
    parser_search.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser_search.add_argument('--output', help='Output file for results (optional)')
    
    # Command 2: Track object
    parser_track = subparsers.add_parser('track', help='Track an object')
    parser_track.add_argument('intdes', help='International Designator (e.g. 1998-067A)')
    parser_track.add_argument('-s', '--step', type=float, default=60.0, help='Time step in seconds (default: 60.0)')
    parser_track.add_argument('-c', '--count', type=int, default=4320, help='Number of steps (default: 4320)')
    parser_track.add_argument('--stations', help='Path to CSV file containing ground stations (name,lat,lon)')
    parser_track.add_argument('--tle-file', help='Path to TLE file to use instead of fetching')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        log(f"Searching for launches on {args.date}...")
        results = get_launches_by_date(args.date)
        if results:
            log(f"Found {len(results)} launches.")
            for r in results:
                log(f"- {r.get('OBJECT_NAME')} ({r.get('OBJECT_ID')})")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                log(f"Results saved to {args.output}")
        else:
            log("No launches found for this date.")
            
    elif args.command == 'track':
        line1, line2, name = None, None, None
        
        if args.tle_file:
            log(f"Reading TLE from {args.tle_file}...")
            try:
                with open(args.tle_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 3:
                        name = lines[0].strip()
                        line1 = lines[1].strip()
                        line2 = lines[2].strip()
                    elif len(lines) == 2:
                        name = "Unknown"
                        line1 = lines[0].strip()
                        line2 = lines[1].strip()
                log(f"Loaded TLE for {name}")
            except Exception as e:
                log(f"Error reading TLE file: {e}")
        else:
            log(f"Fetching TLE for {args.intdes}...")
            line1, line2, name = get_tle_by_intdes(args.intdes)
        
        if line1 and line2:
            if not args.tle_file:
                log(f"Found TLE for {name}")
            
            # Load stations if provided
            stations = []
            if args.stations:
                try:
                    import pandas as pd
                    stations_df = pd.read_csv(args.stations)
                    stations = stations_df.to_dict('records')
                    log(f"Loaded {len(stations)} ground stations.")
                except Exception as e:
                    log(f"Error loading stations: {e}")
            
            log("Propagating orbit...")
            positions, epoch_str = propagate_orbit(line1, line2, step_seconds=args.step, step_count=args.count, satellite_name=name)
            log(f"Calculated {len(positions)} points.")
            plot_ground_track(positions, name)
            create_animation(positions, name, epoch_str, stations=stations)
        else:
            log("Failed to fetch TLE.")
            
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
