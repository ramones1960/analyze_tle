import requests
import datetime
from .logger import log

def get_launches_by_date(date_str):
    """
    Fetches satellite launch data for a specific date from CelesTrak SATCAT.
    
    Args:
        date_str (str): Date in 'YYYY-MM-DD' format.
        
    Returns:
        list: List of dictionaries containing launch data.
    """
    # Using CelesTrak SATCAT query
    # There isn't a direct "launch date" query param in the simple GP API, 
    # but we can filter the full SATCAT or use a range. 
    # However, CelesTrak allows filtering by International Designator (Launch Year).
    # A more robust way for "specific date" is to fetch a larger range or use Space-Track, 
    # but stick to CelesTrak public API.
    # Actually, we can just download the full SATCAT (it's not that huge ~5MB) or query by year if possible.
    # But for this specific requirement, let's try to find a way to filter.
    
    # Correction: The user wants to list objects launched on a specific date.
    # The SATCAT has launch date.
    # We can fetch recent launches or specific queries. 
    # Let's try to use the generic query if available, or just parse the JS/JSON if we can find a good endpoint.
    # CelesTrak standard: https://celestrak.org/satcat/records.php?JSON
    
    # We will fetch all and filter client side for better accuracy if the API doesn't support exact date filter efficiently,
    # OR we can assume the user provides Year and we filter.
    # But fetching the whole SATCAT might be slow every time.
    
    # Let's try to query by Launch Date range if possible.
    # The API documentation says: ?LAUNCH_YEAR=yyyy&LAUNCH_NUM=nnn
    # Maybe just fetch by Year and filter in Python.
    
    try:
        url = "https://celestrak.org/pub/satcat.csv"
        # Download with stream to avoid massive memory usage if it grows
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse CSV
        import csv
        import io
        
        # Decode content
        content = response.content.decode('utf-8')
        f = io.StringIO(content)
        reader = csv.DictReader(f)
        
        filtered_launches = []
        for row in reader:
            if row.get('LAUNCH_DATE') == date_str:
                filtered_launches.append(row)
                
        return filtered_launches

    except Exception as e:
        log(f"Error fetching launch data: {e}")
        return []

def get_tle_by_intdes(int_designator):
    """
    Fetches the latest TLE for a given International Designator.
    
    Args:
        int_designator (str): International Designator (e.g., '1998-067A').
        
    Returns:
        list: [line1, line2] of TLE.
    """
    url = f"https://celestrak.org/NORAD/elements/gp.php?INTDES={int_designator}&FORMAT=TLE"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Simple retry logic
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            text = response.text.strip().splitlines()
            
            # TLE usually comes with a 0th line (name). We need the 1st and 2nd lines (the actual TLE).
            if len(text) >= 3:
                return text[1], text[2], text[0].strip()
            elif len(text) == 2:
                 return text[0], text[1], "Unknown" # Assuming no header
            
            # If we get here with empty/short text, maybe retry or fail
            log(f"Received invalid TLE format on attempt {attempt+1}")
            
        except Exception as e:
            log(f"Error fetching TLE (Attempt {attempt+1}/3): {e}")
            import time
            time.sleep(2)
            
    return None, None, None
