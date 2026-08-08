"""
ASTRAEA-IX — Scientific Spacecraft Datasets
Provides real NASA/ESA aerospace mission configuration datasets for scientific upload.
"""

from typing import Dict, Any

SCIENTIFIC_DATASETS: Dict[str, Dict[str, Any]] = {
    "NASA_ARTEMIS_ORION": {
        "name": "NASA Artemis Orion CSM",
        "dry_mass_kg": 11200.0,
        "fuel_mass_kg": 15320.0,
        "max_thrust_n": 30000.0,
        "isp_sec": 316.0,
        "fuel_reserve_kg": 1500.0,
        "description": "Deep-space human exploration capsule for Lunar & Mars transit operations.",
    },
    "ESA_EXOMARS_TGO": {
        "name": "ESA ExoMars Trace Gas Orbiter",
        "dry_mass_kg": 1365.0,
        "fuel_mass_kg": 2967.0,
        "max_thrust_n": 425.0,
        "isp_sec": 321.0,
        "fuel_reserve_kg": 250.0,
        "description": "European Space Agency Mars atmospheric research & navigation satellite.",
    },
    "NASA_MRO": {
        "name": "NASA Mars Reconnaissance Orbiter",
        "dry_mass_kg": 1031.0,
        "fuel_mass_kg": 1149.0,
        "max_thrust_n": 1700.0,
        "isp_sec": 312.0,
        "fuel_reserve_kg": 120.0,
        "description": "High-resolution orbital survey spacecraft deployed in Mars heliocentric transfer.",
    },
}
