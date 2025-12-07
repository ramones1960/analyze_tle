import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from .logger import log

def create_animation(positions, object_name, tle_epoch, stations=[]):
    """
    Creates an interactive HTML animation of the satellite orbit.
    Functionality:
    - Left: 2D Equirectangular projection Map.
    - Right: 3D Orthographic projection (Globe) View.
    
    Args:
        positions (list): List of dictionaries containing time, lat, lon, alt.
        object_name (str): Name of the satellite.
        tle_epoch (str): TLE Epoch string.
        stations (list): List of dicts (name, lat, lon) for ground stations.
    """
    log("Generating 3D/2D animation (Globe View)...")
    
    # Check if we have data
    if not positions:
        log("No positions to visualize.")
        return

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(positions)
    df['time_str'] = df['time'].astype(str)
    
    # Ensure TLE Epoch uses UTCG if it says UTC
    if tle_epoch and "UTC" in tle_epoch:
        tle_epoch = tle_epoch.replace("UTC", "UTCG")
    
    # --- Plotly Figures ---
    
    from plotly.subplots import make_subplots
    
    # Create subplots with 2 geo types
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scattergeo"}, {"type": "scattergeo"}]],
        subplot_titles=("2D Map", "3D Globe"),
        horizontal_spacing=0.05
    )
    
    # --- Traces ---
    
    # Trace 1: Ground Track on 2D Map (Left)
    fig.add_trace(
        go.Scattergeo(
            lon=df['longitude'],
            lat=df['latitude'],
            mode='lines',
            line=dict(width=2, color='blue'),
            name='Ground Track (2D)'
        ),
        row=1, col=1
    )
    
    # Trace 2: Orbit Path on 3D Globe (Right)
    # We use Scattergeo again, but this will be projected onto the orthographic sphere
    fig.add_trace(
        go.Scattergeo(
            lon=df['longitude'],
            lat=df['latitude'],
            mode='lines',
            line=dict(width=2, color='red'),
            name='Orbit Path (3D)'
        ),
        row=1, col=2
    )

    # --- Markers for Animation (Initial) ---
    
    # Trace 3: Current Pos on 2D Map
    fig.add_trace(
        go.Scattergeo(
            lon=[df.iloc[0]['longitude']],
            lat=[df.iloc[0]['latitude']],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Pos 2D'
        ),
        row=1, col=1
    )
    
    # Trace 4: Current Pos on 3D Globe
    fig.add_trace(
        go.Scattergeo(
            lon=[df.iloc[0]['longitude']],
            lat=[df.iloc[0]['latitude']],
            mode='markers',
            marker=dict(size=10, color='cyan'),
            name='Pos 3D'
        ),
        row=1, col=2
    )

    # Trace 5: Grid Labels (Manual "Degree" symbols)
    # Plotly geo axes don't support custom ticksuffix easily, so we add text traces.
    
    # Latitude Labels (along the right edge, Lon 180)
    # Moving to right edge to avoid overlapping with left-aligned titles or map content if cluttered
    lat_vals = list(range(-90, 91, 30))
    lat_text = [f"{i}°" for i in lat_vals]
    lat_lons = [180] * len(lat_vals) 
    
    fig.add_trace(
        go.Scattergeo(
            lon=lat_lons,
            lat=lat_vals,
            text=lat_text,
            mode="text",
            textposition="middle left", # Inside the map from the right edge
            name='LatGrid',
            hoverinfo='none',
            showlegend=False,
            textfont=dict(size=10, color="gray")
        ),
        row=1, col=1
    )
    
    # Longitude Labels (along the bottom, Lat -85)
    # Moving to bottom to clear the equator
    lon_vals = list(range(-180, 181, 30))
    lon_text = [f"{i}°" for i in lon_vals]
    lon_lats = [-85] * len(lon_vals)
    
    fig.add_trace(
        go.Scattergeo(
            lon=lon_vals,
            lat=lon_lats,
            text=lon_text,
            mode="text",
            textposition="bottom center",
            name='LonGrid',
            hoverinfo='none',
            showlegend=False,
            textfont=dict(size=10, color="gray")
        ),
        row=1, col=1
    )

    # Trace 6: Ground Stations - update to show on all? Or just geo? 
    # Just geo for now, hard to map to ECI without time conversion per station?
    # Actually stations fixed in ECEF, so we CAN add to ECEF plot easily.
    
    if stations:
        station_lats = [s['lat'] for s in stations]
        station_lons = [s['lon'] for s in stations]
        station_names = [s['name'] for s in stations]
        
        # Add to 2D Map
        fig.add_trace(
            go.Scattergeo(
                lon=station_lons,
                lat=station_lats,
                mode='markers+text',
                marker=dict(size=8, color='green', symbol='circle'),
                text=station_names,
                textposition="top center",
                name='Stations (2D)',
                hoverinfo='text+lon+lat'
            ),
            row=1, col=1
        )
        
        # Add to 3D Globe
        fig.add_trace(
            go.Scattergeo(
                lon=station_lons,
                lat=station_lats,
                mode='markers+text',
                marker=dict(size=8, color='magenta', symbol='circle'),
                text=station_names,
                textposition="top center",
                name='Stations (Globe)',
                hoverinfo='text+lon+lat'
            ),
            row=1, col=2
        )
        
    # Indices to update
    # 2: Pos 2D
    # 3: Pos 3D
    update_indices = [2, 3]

    # --- Animation Frames ---
    
    frames = []
    # Downsample for animation speed if too many points? 
    # Current step=60s, count=4320 -> 4320 frames is A LOT for browser.
    # Usually we skip frames.
    skip = 1
    if len(df) > 500:
        skip = int(len(df) / 500) # Aim for ~500 frames max
    
    frame_indices = range(0, len(df), skip)
    
    for k in frame_indices:
        row_data = df.iloc[k]
        frame_time_str = str(row_data['time'])
        
        # Fixed width formatting for Lat/Lon
        # Align decimal points by fixing total width to 11 chars (enough for -180.000000)
        # >11.6f aligns to the right with spaces, ensuring dot alignment
        lat_str = "{:>11.6f}".format(row_data['latitude'])
        lon_str = "{:>11.6f}".format(row_data['longitude'])
        
        # Format with aligned colons using non-breaking spaces if needed, but monospace handles spaces well.
        # labels: 'UTCG', 'Lat.', 'Lon'
        # Max length 4 ('UTCG' w/o space? No 'UTCG ' is 5). 'Lat.' is 4. 'Lon' is 3.
        # We want:
        # UTCG : 
        # Lat. : 
        # Lon. : 
        title_html = (
            f"Satellite: {object_name} (TLE: {tle_epoch})<br>"
            f"<span style='font-family: monospace; white-space: pre;'>"
            f"UTCG : {frame_time_str}<br>"
            f"Lat. : {lat_str}<br>"
            f"Lon. : {lon_str}"
            f"</span>"
        )
        
        frames.append(
            go.Frame(
                data=[
                    # Update Trace 2 (Pos 2D)
                    go.Scattergeo(
                        lon=[row_data['longitude']],
                        lat=[row_data['latitude']],
                        mode='markers',
                        marker=dict(size=10, color='red'),
                    ),
                    # Update Trace 3 (Pos 3D)
                    go.Scattergeo(
                        lon=[row_data['longitude']],
                        lat=[row_data['latitude']],
                        mode='markers',
                        marker=dict(size=10, color='cyan')
                    )
                ],
                layout=go.Layout(
                    title_text=title_html
                ),
                traces=update_indices, 
                name=f"frame{k}"
            )
        )
        
    fig.frames = frames

    
    # --- Controls ---
    # Slider
    sliders = [dict(
        steps=[dict(
            method='animate',
            args=[[f'frame{k}'], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
            label=f"{k}"
        ) for k in frame_indices],
        transition=dict(duration=0),
        x=0.1,
        len=0.9,
        currentvalue=dict(font=dict(size=12), prefix='Step: ', visible=True, xanchor='center'),
        pad=dict(b=10, t=50)
    )]
    
    # Buttons for Play/Pause
    updatemenus = [
        dict(
            type="buttons",
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, dict(frame=dict(duration=1000, redraw=True), fromcurrent=True, transition=dict(duration=0))]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=True), mode="immediate", transition=dict(duration=0))])
            ],
            direction="left",
            pad={"r": 10, "t": 87},
            showactive=False,
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top"
        )
    ]
    
    # Layout settings
    lat_str = "{:>11.6f}".format(df.iloc[0]['latitude'])
    lon_str = "{:>11.6f}".format(df.iloc[0]['longitude'])
    
    initial_title_html = (
        f"Satellite: {object_name} (TLE: {tle_epoch})<br>"
        f"<span style='font-family: monospace; white-space: pre;'>"
        f"UTCG : {df.iloc[0]['time']}<br>"
        f"Lat. : {lat_str}<br>"
        f"Lon. : {lon_str}"
        f"</span>"
    )
    
    fig.update_layout(
        title_text=initial_title_html,
        uirevision="constant", # Critical for maintaining interactivity/zoom during animation
        # geo  = Left Subplot (domain x=[0, 0.45] approx)
        # geo2 = Right Subplot (domain x=[0.55, 1] approx)
        geo=dict( # 2D Map settings
            projection_type="equirectangular",
            showland=True,
            showocean=False,
            showcoastlines=True,
            landcolor="lightgray",
            # domain=dict(x=[0, 0.48]), # Left side - Plotly handles subplots generally, but explicit domain helps split
            # Grid settings
            lataxis=dict(
                showgrid=True,
                gridcolor='rgb(180, 180, 180)',
                gridwidth=0.5,
                dtick=30,
                tick0=-90
            ),
            lonaxis=dict(
                showgrid=True,
                gridcolor='rgb(180, 180, 180)',
                gridwidth=0.5,
                dtick=30,
                tick0=-180
            ),
        ),
        geo2=dict( # 3D Globe settings
            projection_type="orthographic",
            showland=True,
            showocean=True,
            oceancolor="lightblue",
            showcoastlines=True,
            landcolor="forestgreen",
            showcountries=True,
            countrycolor="black",
            projection_rotation=dict(lon=df.iloc[0]['longitude'], lat=df.iloc[0]['latitude'])
        ),
        updatemenus=updatemenus,
        sliders=sliders,
        annotations=[
            dict(
                text="Propagated with SGP4 Model",
                showarrow=False,
                xref="paper", yref="paper",
                x=1, y=0,
                xanchor="right", yanchor="bottom",
                font=dict(size=10, color="grey")
            )
        ]
    )
    
    # Save to HTML
    import os
    filename = f"{object_name.strip().replace(' ', '_')}_orbit_viz.html"
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in ('_', '.')]).rstrip()
    
    output_path = os.path.join('output', filename)
    
    log(f"Saving visualization to {output_path}...")
    fig.write_html(output_path, auto_play=False)
    log("Done.")
