import streamlit as st 
import plotly.graph_objects as go 
import numpy as np 
 
def get_position_coordinates(position): 
    """Get coordinates based on player position""" 
    position_coords = { 
        'Goalkeeper': (-45, 0), 
        'Left Back': (-30, -20), 
        'Right Back': (-30, 20), 
        'Center Back': (-30, 0), 
        'Left Midfielder': (0, -25), 
        'Right Midfielder': (0, 25), 
        'Center Midfielder': (0, 0), 
        'Left Forward': (30, -20), 
        'Right Forward': (30, 20), 
        'Striker': (40, 0), 
        'Forward': (35, 0), 
        'Midfielder': (0, 0), 
        'Defender': (-25, 0) 
    } 
    return position_coords.get(position, (0, 0)) 
