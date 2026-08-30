"""
Enterprise CSS system with Dark & Light theme support, glassmorphism,
glowing status badges, high-contrast chips, and responsive layout styling.
"""


def get_custom_css(theme: str = "dark") -> str:
    if theme == "light":
        bg_main = "#f8fafc"
        bg_card = "#ffffff"
        border_card = "#e2e8f0"
        text_primary = "#0f172a"
        text_secondary = "#475569"
        chip_energy_bg = "#fef3c7"
        chip_energy_text = "#92400e"
        chip_energy_border = "#f59e0b"
        chip_control_bg = "#fee2e2"
        chip_control_text = "#991b1b"
        chip_control_border = "#ef4444"
        chip_safe_bg = "#dcfce7"
        chip_safe_text = "#166534"
        chip_safe_border = "#22c55e"
    else:
        bg_main = "#0d1117"
        bg_card = "#161b22"
        border_card = "#30363d"
        text_primary = "#e6edf3"
        text_secondary = "#8b949e"
        chip_energy_bg = "#3a2a12"
        chip_energy_text = "#ffb84d"
        chip_energy_border = "#a5670e"
        chip_control_bg = "#351515"
        chip_control_text = "#ff8080"
        chip_control_border = "#8f1f1f"
        chip_safe_bg = "#12351c"
        chip_safe_text = "#5fd88f"
        chip_safe_border = "#1f8f47"

    return f"""
<style>
/* Main App Background */
.stApp {{
    background-color: {bg_main};
    color: {text_primary};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    color: {text_primary} !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}}

/* Metric Cards */
.metric-card {{
    background: {bg_card};
    border: 1px solid {border_card};
    border-radius: 12px;
    padding: 16px 18px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s ease, border-color 0.2s ease;
}}
.metric-card:hover {{
    transform: translateY(-2px);
    border-color: #ff5c5c;
}}
.metric-card h3 {{
    color: {text_primary} !important;
    margin: 0 0 4px 0;
    font-size: 1.75rem;
    font-weight: 800;
}}
.metric-card .subtitle {{
    color: {text_secondary};
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Chips */
.chip {{
    display: inline-block;
    padding: 5px 12px;
    margin: 3px 4px 3px 0;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}}
.chip-energy {{
    background: {chip_energy_bg};
    color: {chip_energy_text};
    border: 1px solid {chip_energy_border};
}}
.chip-control {{
    background: {chip_control_bg};
    color: {chip_control_text};
    border: 1px solid {chip_control_border};
}}
.chip-safe {{
    background: {chip_safe_bg};
    color: {chip_safe_text};
    border: 1px solid {chip_safe_border};
}}

/* Status Pills */
.pill-critical {{
    background: #450a0a;
    color: #f87171;
    border: 1px solid #dc2626;
    padding: 6px 14px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}}
.pill-caution {{
    background: #451a03;
    color: #fbbf24;
    border: 1px solid #d97706;
    padding: 6px 14px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}}
.pill-safe {{
    background: #052e16;
    color: #4ade80;
    border: 1px solid #16a34a;
    padding: 6px 14px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}}

/* Flow box */
.flow-box {{
    background: {bg_card};
    border: 1px solid {border_card};
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
    font-weight: 600;
    font-size: 0.88rem;
    color: {text_primary};
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* Team Banner */
.team-banner {{
    text-align: center;
    padding: 4px 0 10px;
}}
.team-name {{
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 6px;
    background: linear-gradient(90deg, #ff5c5c, #ffb84d, #5fd88f, #4dc8ff, #ff5c5c);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 6s linear infinite;
}}
@keyframes shine {{
    0% {{ background-position: 0% center; }}
    100% {{ background-position: 300% center; }}
}}
.team-quote {{
    color: {text_secondary};
    font-style: italic;
    font-size: 0.95rem;
    margin-top: 3px;
}}

/* Emergency Boxes */
.helpline-box {{
    background: {bg_card};
    border: 1px solid {border_card};
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: {text_primary};
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.helpline-num {{
    color: #ef4444;
    font-weight: 800;
    font-size: 0.95rem;
}}
.helpline-critical {{
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid #dc2626;
    border-radius: 12px;
    padding: 16px 18px;
    margin-top: 12px;
    color: {text_primary};
}}

/* Token Usage Card */
.token-card {{
    background: {bg_card};
    border: 1px dashed {border_card};
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.82rem;
    color: {text_secondary};
}}

/* Similar Incident Item */
.similar-card {{
    background: {bg_card};
    border: 1px solid {border_card};
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
}}
</style>
"""
