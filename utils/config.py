
# Configuration for Global Hub Dashboard

# File Paths
DATA_PATH = "www/HorizonScanCombined.csv"

# UI Colors
COLORS = {
    "primary": "#0056b3",
    "secondary": "#007bff",
    "bg": "#f8f9fa",
    "fg": "#212529",
    "status_colors": ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
}

# Coordinate Mapping for Map Visualization
COUNTRY_COORDS = {
    "Kenya": {"lat": -0.02, "lon": 37.9},
    "Senegal": {"lat": 14.5, "lon": -14.4},
    "South Africa": {"lat": -30.6, "lon": 22.9},
    "Overall": {"lat": 0.0, "lon": 0.0},
    "Brazil": {"lat": -10.8, "lon": -52.9},
    "India": {"lat": 21.0, "lon": 78.0},
    "Nigeria": {"lat": 9.1, "lon": 8.7},
    "Tanzania": {"lat": -6.4, "lon": 35.0},
    "Ghana": {"lat": 7.9, "lon": -1.0}
}

# Column Mappings
COLUMN_MAPPING = {
    "time_to_regulatory_approval": "Time_to_Approval",
    "time_to_market": "Time_to_Market",
}
