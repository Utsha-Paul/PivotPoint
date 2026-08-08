"""
ASTRAEA-IX — Physical and Mission Constants
"""

# Astronomical Units (SI)
AU_METERS = 1.495978707e11
SPEED_OF_LIGHT = 299792458.0  # m/s

# Mass Constants (kg)
MASS_SUN = 1.989e30
MASS_EARTH = 5.972e24
MASS_MOON = 7.342e22
MASS_MARS = 6.4171e23

# Default Spacecraft Constants
SPACECRAFT_DRY_MASS = 1000.0  # kg
SPACECRAFT_FUEL_INITIAL = 1000.0  # kg
SPACECRAFT_FUEL_RESERVE = 100.0  # kg
SPACECRAFT_ISP = 310.0  # s (high efficiency chemical/electric propulsion)
SPACECRAFT_MAX_THRUST = 150.0  # N

# Target Orbital Destinations
DESTINATIONS = {
    "Mars": {
        "name": "Mars",
        "distance_au": 1.524,
        "mass": MASS_MARS,
        "radius_m": 3389500.0,
    },
    "Moon": {
        "name": "Moon",
        "distance_au": 0.00257,
        "mass": MASS_MOON,
        "radius_m": 1737400.0,
    },
}
