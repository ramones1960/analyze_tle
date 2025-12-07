import datetime

def log(message):
    """Prints a message with the current UTC timestamp."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")
