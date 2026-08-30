"""
Deterministic rule-based SIF scoring algorithm based on the
Campbell Institute / DuPont high-energy control barrier methodology.
"""
import re
from typing import Dict, List, Tuple, Any
from src.domain.constants import HIGH_ENERGY_SOURCES, CONTROL_FAILURE_MARKERS, SEVERITY_LEVELS


def generate_corrective_actions(matched_energy: List[str], matched_controls: List[str]) -> List[str]:
    """Generates immediate hierarchy-of-control action items based on detected factors."""
    actions = []
    
    # Energy-specific mitigations
    for e in matched_energy:
        if "Fall" in e:
            actions.append("Halt height operations until 100% certified tie-off and scaffold inspection tag are verified.")
        elif "Vehicle" in e or "Struck" in e:
            actions.append("Establish physical exclusion zones and assign dedicated banksman with high-vis baton.")
        elif "Fire" in e or "Explosion" in e:
            actions.append("Verify gas test certificate (<0% LEL), continuous combustible monitor, and fire watch on site.")
        elif "Chemical" in e or "Gas" in e:
            actions.append("Evacuate upwind, deploy breathing apparatus (SCBA), and initiate emergency flange isolation.")
        elif "Electrical" in e:
            actions.append("Perform Lockout/Tagout (LOTO), verify zero energy state via multimeter, and ground conductors.")
        elif "Confined" in e:
            actions.append("Halt entry: conduct multi-gas testing (O2, H2S, LEL, CO) and verify standby rescue technician.")
        elif "Lifting" in e or "Crane" in e:
            actions.append("Inspect wire ropes, verify crane load chart, and bar personnel from suspended load shadow.")
        elif "Pressure" in e or "Steam" in e:
            actions.append("Depressurize line, lock out inlet valves, and inspect rupture discs / safety valves.")

    # Control failure mitigations
    for c in matched_controls:
        c_lower = c.lower()
        if "permit" in c_lower:
            actions.append("Verify Permit-To-Work (PTW) authorization with Asset Area Manager.")
        if "harness" in c_lower or "ppe" in c_lower or "belt" in c_lower:
            actions.append("Mandate immediate PPE audit and issue formal stop-work notice.")
        if "lockout" in c_lower or "isolation" in c_lower or "loto" in c_lower:
            actions.append("Perform physical verification of energy isolation padlocks and tag register.")
        if "signal" in c_lower or "banksman" in c_lower or "spotter" in c_lower:
            actions.append("Deploy trained banksman prior to any further heavy equipment movement.")
        if "bypass" in c_lower or "guard" in c_lower:
            actions.append("Reinstate safety interlocks and physical guards immediately.")

    if not actions:
        actions.append("Log observation in safety register; discuss during next toolbox safety briefing.")
        actions.append("Reinforce basic housekeeping standards and buddy-system monitoring.")

    return list(dict.fromkeys(actions))  # Deduplicate while preserving order


def calculate_rule_based_sif(
    text: str,
    energy_sources_dict: Dict[str, Any] = None,
    control_markers_list: List[str] = None
) -> Tuple[str, int, List[str], List[str], List[str]]:
    """
    Calculates deterministic SIF classification and risk score from text.
    
    Returns:
        (category, score, matched_energy, matched_controls, corrective_actions)
    """
    if energy_sources_dict is None:
        energy_sources_dict = HIGH_ENERGY_SOURCES
    if control_markers_list is None:
        control_markers_list = CONTROL_FAILURE_MARKERS

    text_lower = text.lower()
    
    # 1. Match high-energy sources
    matched_energy = []
    total_energy_weight = 0
    for name, cfg in energy_sources_dict.items():
        for kw in cfg["keywords"]:
            kw_clean = kw.lower().strip()
            # Check for keyword phrase
            if kw_clean in text_lower or re.search(r"\b" + re.escape(kw_clean) + r"\b", text_lower):
                matched_energy.append(name)
                total_energy_weight += cfg["weight"]
                break

    # 2. Match control / barrier failures
    matched_controls = []
    # Pattern extensions for common variations
    flexible_patterns = [
        (r"\b(without|no|not wearing|bina|nahi)\s+.*?(harness|safety belt|belt)", "without harness"),
        (r"\b(without|no|bina|nahi)\s+.*?(permit|ptw)", "no permit"),
        (r"\b(without|no|not wearing|bina)\s+.*?(ppe|helmet|goggles|gloves)", "without ppe"),
        (r"\b(without|no|bina)\s+.*?(lockout|tagout|loto|isolation)", "no lockout / isolation"),
        (r"\b(no|without|bina)\s+.*?(signal|banksman|spotter)", "no signal person / banksman"),
        (r"\b(bypassed|disabled|guard hataya|disconnected)", "interlock / guard bypassed"),
        (r"\b(unfastened|unsecured|not secured|loose)", "not secured / unfastened"),
        (r"\b(snapped|ruptured|cracked|burst|leaking|leak)", "equipment failure / leak"),
    ]

    for pat, label in flexible_patterns:
        if re.search(pat, text_lower):
            matched_controls.append(label)

    # Also check exact markers
    for marker in control_markers_list:
        m_clean = marker.lower().strip()
        if m_clean in text_lower or re.search(r"\b" + re.escape(m_clean) + r"\b", text_lower):
            if marker not in matched_controls:
                matched_controls.append(marker)

    # Deduplicate matched controls
    matched_controls = list(dict.fromkeys(matched_controls))

    # Core Campbell Institute Decision Matrix
    if matched_energy and matched_controls:
        category = "Critical SIF Precursor"
        # High base score + additive energy weight + control failure penalty
        base_score = 78 + min(20, total_energy_weight + 3 * len(matched_controls))
    elif matched_energy:
        category = "Potential Precursor / Elevated Risk"
        base_score = 44 + min(34, total_energy_weight * 2)
    elif matched_controls:
        category = "Potential Precursor / Elevated Risk"
        base_score = 38 + min(25, 4 * len(matched_controls))
    else:
        category = "Routine Safety Observation"
        word_count = len(text_lower.split())
        base_score = 12 + min(28, 4 * (word_count // 8))

    score = int(max(5, min(base_score, 99)))
    corrective_actions = generate_corrective_actions(matched_energy, matched_controls)

    return category, score, matched_energy, matched_controls, corrective_actions
