"""
Domain constants for SIF (Serious Injury & Fatality) detection,
based on the Campbell Institute and DuPont high-energy control frameworks.
"""

HIGH_ENERGY_SOURCES = {
    "Fall from Height": {
        "weight": 9,
        "keywords": [
            "fall", "falling", "height", "scaffold", "scaffolding", "harness", "ladder",
            "roof", "edge", "elevated", "platform", "gir gaya", "girna", "uchai",
            "uncha", "chhat", "slips", "trips from height", "basket", "manlift"
        ],
        "category_code": "HE_FALL",
        "description": "Potential fall greater than 1.8m (6ft) or into hazardous machinery."
    },
    "Struck-By / Vehicle": {
        "weight": 8,
        "keywords": [
            "struck", "vehicle", "forklift", "collision", "run over", "reversing",
            "traffic", "dumper", "truck", "gaadi", "takkar", "vehicle se takra",
            "tractor", "hydra", "crane movement", "speeding"
        ],
        "category_code": "HE_VEHICLE",
        "description": "Heavy moving plant, mobile equipment, or vehicle interaction with pedestrians."
    },
    "Caught-in / Machinery": {
        "weight": 8,
        "keywords": [
            "caught", "machinery", "conveyor", "rotating", "pinch point", "entangled",
            "unguarded machine", "machine mein fasa", "haath fas gaya", "roller",
            "pulley", "nip point", "crushed"
        ],
        "category_code": "HE_MECH",
        "description": "Moving mechanical components with nip points, pinch points, or entanglement hazards."
    },
    "Electrical": {
        "weight": 9,
        "keywords": [
            "electrical", "shock", "voltage", "live wire", "cable", "electrocution",
            "panel", "current lag gaya", "bijli", "high voltage", "hv line",
            "transformer", "short circuit", "substation", "switchgear"
        ],
        "category_code": "HE_ELEC",
        "description": "Exposed electrical conductors, high-voltage systems, or arc-flash potential."
    },
    "Fire / Explosion": {
        "weight": 10,
        "keywords": [
            "fire", "explosion", "flammable", "spark", "ignition", "hot work",
            "flash fire", "aag", "blast", "visfot", "chingari", "gas flare",
            "hydrocarbon leak", "combustible", "welding spark"
        ],
        "category_code": "HE_FIRE_EXP",
        "description": "Presence of combustible atmospheres, flammable liquids, or ignition sources in hazardous zones."
    },
    "Chemical / Gas Release": {
        "weight": 9,
        "keywords": [
            "leak", "gas", "toxic", "chemical spill", "h2s", "fume", "vapour",
            "vapor", "poisonous gas", "gas rissav", "chemical leak", "rasayan",
            "acid", "caustic", "chlorine", "hydrocarbon cloud"
        ],
        "category_code": "HE_CHEM_GAS",
        "description": "Uncontrolled release of toxic gases (e.g. H2S), asphyxiants, or corrosive chemicals."
    },
    "Lifting / Crane Ops": {
        "weight": 8,
        "keywords": [
            "crane", "lifting", "load", "rigging", "hoist", "suspended", "sling",
            "snap", "crane operation", "bhari saman utha", "load gira", "shackle",
            "tagline", "winch", "boom collapse"
        ],
        "category_code": "HE_LIFT",
        "description": "Critical heavy lifts, suspended loads over personnel, or rigging degradation."
    },
    "Confined Space": {
        "weight": 10,
        "keywords": [
            "confined space", "tank entry", "vessel entry", "manhole",
            "oxygen deficient", "band jagah", "tank ke andar", "column entry",
            "pit entry", "sump", "culvert"
        ],
        "category_code": "HE_CONFINED",
        "description": "Enclosed volumes with restricted ingress/egress and hazardous or oxygen-deficient atmosphere."
    },
    "Excavation / Trenching": {
        "weight": 7,
        "keywords": [
            "excavation", "trench", "collapse", "underground", "shoring",
            "khudai", "gadha", "cave in", "earth slip", "soil collapse"
        ],
        "category_code": "HE_EXCAV",
        "description": "Excavations deeper than 1.2m without certified shoring, benching, or shielding."
    },
    "Working Offshore / Marine Rig": {
        "weight": 8,
        "keywords": [
            "offshore", "rig floor", "derrick", "overboard", "samudra",
            "jahaz", "marine vessel", "gangway", "drill floor", "moonpool"
        ],
        "category_code": "HE_OFFSHORE",
        "description": "Offshore drilling/production platform operations with man-overboard or derrick risks."
    },
    "Pressure / Steam Systems": {
        "weight": 8,
        "keywords": [
            "pressure vessel", "steam leak", "high pressure", "boiler", "rupture",
            "burst pipe", "flange leak", "relief valve", "prv pop"
        ],
        "category_code": "HE_PRESSURE",
        "description": "Pressurized fluids, high-pressure piping, steam lines, or hydraulic accumulators."
    },
    "Radiation / Hazardous Energy": {
        "weight": 9,
        "keywords": [
            "radiation", "radioactive source", "gamma", "x-ray exposure", "isotope",
            "pigging tool", "ndt camera", "radiography"
        ],
        "category_code": "HE_RAD",
        "description": "Industrial radiography sources, gamma emitters, or unshielded nuclear gauges."
    }
}

CONTROL_FAILURE_MARKERS = [
    "without harness", "no harness", "not wearing", "without ppe", "no ppe",
    "bypassed", "disabled", "unguarded", "no permit", "without permit",
    "not isolated", "no barricade", "unauthorized", "overloaded",
    "no lockout", "without lockout", "failed", "malfunctioned", "not secured",
    "no signal person", "no banksman", "worn out", "expired inspection",
    "harness nahi", "permit nahi", "bina permit", "bina harness", "bina ppe",
    "safety belt nahi", "guard hataya", "check nahi kiya", "training nahi",
    "not trained", "improper storage", "no supervision", "no isolation",
    "damaged cable", "leaking seal", "valve left open", "unattended hot work",
    "interlock bypassed", "gas detector off", "calibration overdue"
]

SEVERITY_LEVELS = {
    "Critical SIF Precursor": {
        "pill": "pill-critical",
        "emoji": "??",
        "color": "#ff5c5c",
        "badge_bg": "rgba(255, 92, 92, 0.15)",
        "badge_border": "#ff5c5c",
        "description": "High-Energy source present AND Direct Barrier/Control Failed. Immediate stop-work required."
    },
    "Potential Precursor / Elevated Risk": {
        "pill": "pill-caution",
        "emoji": "??",
        "color": "#ffcc4d",
        "badge_bg": "rgba(255, 204, 77, 0.15)",
        "badge_border": "#ffcc4d",
        "description": "High-Energy source present with degraded barriers, or severe barrier failure under low energy."
    },
    "Routine Safety Observation": {
        "pill": "pill-safe",
        "emoji": "?",
        "color": "#5fd88f",
        "badge_bg": "rgba(95, 216, 143, 0.15)",
        "badge_border": "#5fd88f",
        "description": "Low energy involved; standard housekeeping, behavioral reminder, or routine maintenance."
    }
}

INCIDENT_TYPES = list(HIGH_ENERGY_SOURCES.keys())

OIL_INDIA_LOCATIONS = {
    "Duliajan Operational HQ": {"lat": 27.3591, "lon": 95.3182, "state": "Assam", "type": "Headquarters"},
    "Well Pad A (Naharkatiya)": {"lat": 27.2842, "lon": 95.2891, "state": "Assam", "type": "Production Well"},
    "Refinery Unit 3 (Digboi)": {"lat": 27.3800, "lon": 95.6200, "state": "Assam", "type": "Refinery"},
    "Numaligarh Refinery Link": {"lat": 26.5900, "lon": 93.7500, "state": "Assam", "type": "Refinery"},
    "Pipeline Sector 7 (Moran)": {"lat": 27.1800, "lon": 94.9300, "state": "Assam", "type": "Pipeline"},
    "Storage Yard & Logistics": {"lat": 27.3400, "lon": 95.3300, "state": "Assam", "type": "Logistics Yard"},
    "Offshore Rig OI-2 (KG Basin)": {"lat": 16.3500, "lon": 82.2500, "state": "Andhra Offshore", "type": "Offshore Platform"},
    "Tank Farm North": {"lat": 27.3700, "lon": 95.3000, "state": "Assam", "type": "Storage Facility"},
    "Loading Bay & Gantry": {"lat": 27.3620, "lon": 95.3150, "state": "Assam", "type": "Terminal"},
    "Central Workshop & Maintenance": {"lat": 27.3550, "lon": 95.3220, "state": "Assam", "type": "Workshop"}
}

EMERGENCY_HELPLINES = [
    {"label": "National Emergency Number", "number": "112", "icon": "??", "category": "General"},
    {"label": "Fire Brigade (On-Site Response)", "number": "101", "icon": "??", "category": "Fire"},
    {"label": "Ambulance / Medical Trauma", "number": "102 / 108", "icon": "??", "category": "Medical"},
    {"label": "Disaster Management (NDMA)", "number": "108", "icon": "???", "category": "Disaster"},
    {"label": "Hydrocarbon / Gas Leak Emergency", "number": "1906", "icon": "?", "category": "Oil & Gas"},
    {"label": "Oil India HSE Control Room (Duliajan)", "number": "+91-374-2800555", "icon": "???", "category": "Corporate"},
]
