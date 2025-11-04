"""
outfitcast.py

Single-file Streamlit app: OutfitCast
Run:
    pip install streamlit
    streamlit run outfitcast.py

This is a frontend-only demo skeleton (no APIs, no network calls).
It shows a landing page with an Enter button, then a main UI where the user
selects an Indian state capital and clicks "Forecast my outfit" to see
deterministic dummy weather + outfit suggestions.

All logic and UI are contained in this one file.
"""

from __future__ import annotations
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import hashlib
import math

# -------------------------
# Constants & Static Data
# -------------------------

APP_TITLE = "OutfitCast"

# List of (State — Capital) shown in the dropdown
CAPITALS: List[str] = [
    "Andhra Pradesh — Amaravati",
    "Arunachal Pradesh — Itanagar",
    "Assam — Dispur",
    "Bihar — Patna",
    "Chhattisgarh — Raipur",
    "Goa — Panaji",
    "Gujarat — Gandhinagar",
    "Haryana — Chandigarh",
    "Himachal Pradesh — Shimla",
    "Jharkhand — Ranchi",
    "Karnataka — Bengaluru",
    "Kerala — Thiruvananthapuram",
    "Madhya Pradesh — Bhopal",
    "Maharashtra — Mumbai",
    "Manipur — Imphal",
    "Meghalaya — Shillong",
    "Mizoram — Aizawl",
    "Nagaland — Kohima",
    "Odisha — Bhubaneswar",
    "Punjab — Chandigarh",
    "Rajasthan — Jaipur",
    "Sikkim — Gangtok",
    "Tamil Nadu — Chennai",
    "Telangana — Hyderabad",
    "Tripura — Agartala",
    "Uttar Pradesh — Lucknow",
    "Uttarakhand — Dehradun",
    "West Bengal — Kolkata",
    "Andaman and Nicobar Islands — Port Blair",
    "Chandigarh — Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu — Daman",
    "Delhi (NCT) — New Delhi",
    "Jammu & Kashmir — Srinagar",
    "Ladakh — Leh",
    "Lakshadweep — Kavaratti",
    "Puducherry — Puducherry",
]

WEATHER_EMOJI = {
    "clear": "☀️",
    "partly": "⛅",
    "cloudy": "☁️",
    "rain": "🌧️",
    "storm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

# -------------------------
# Helper Functions
# -------------------------

def init_session_state() -> None:
    """
    Initialize required session state keys safely.
    """
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "selected_city" not in st.session_state:
        st.session_state.selected_city = None
    if "forecast_generated" not in st.session_state:
        st.session_state.forecast_generated = False
    if "light_mode" not in st.session_state:
        st.session_state.light_mode = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def city_to_seed(city: str) -> int:
    """
    Deterministically convert a city string to an integer seed.
    """
    if not city:
        return 0
    h = hashlib.sha256(city.encode("utf-8")).hexdigest()
    # take first 8 hex digits -> int
    return int(h[:8], 16)


def synthesize_weather(city: str) -> Dict[str, Any]:
    """
    Produce deterministic dummy weather for a given city string.
    Returns a dict with keys: temp_c, humidity, precip_chance, wind_kmh, condition_key
    """
    seed = city_to_seed(city)
    # Use modular arithmetic to map into realistic ranges
    temp_c = 12 + (seed % 26)  # 12..37
    humidity = 30 + ((seed >> 3) % 71)  # 30..100
    precip = (seed >> 6) % 101  # 0..100
    wind = 5 + ((seed >> 10) % 36)  # 5..40 km/h

    # Simple condition selection
    if precip > 60:
        condition = "storm" if wind > 25 else "rain"
    elif precip > 25:
        condition = "rain" if humidity > 60 else "partly"
    elif temp_c <= 5:
        condition = "snow"
    elif humidity > 80 and temp_c < 20:
        condition = "mist"
    elif temp_c >= 30:
        condition = "clear"
    elif temp_c >= 22:
        condition = "partly"
    else:
        condition = "cloudy"

    return {
        "temp_c": temp_c,
        "humidity": humidity,
        "precip_chance": precip,
        "wind_kmh": wind,
        "condition": condition,
    }


def generate_hourly_forecast(base_temp: int, base_condition: str) -> List[Dict[str, Any]]:
    """
    Generate a small 6-hour static forecast list from base values.
    Each item: {"hour": "3 PM", "temp": 31, "emoji": "☀️"}
    """
    now = datetime.now()
    hourly = []
    seed_offset = base_temp % 7

    for i in range(6):
        # Cross-platform hour formatting
        # Use %I for 12-hour format and strip leading zeros manually (Windows safe)
        hour_time = (now + timedelta(hours=i)).strftime("%I %p").lstrip("0")

        # temp swings +/- up to 3 degrees
        temp = base_temp + ((i + seed_offset) % 7) - 3

        # pick an emoji: slightly vary condition across hours
        cond_variation_index = (i + seed_offset) % 5
        if base_condition in ("rain", "storm") and i % 2 == 0:
            emoji = WEATHER_EMOJI["rain"]
        elif base_condition == "clear":
            emoji = WEATHER_EMOJI["clear"] if cond_variation_index < 3 else WEATHER_EMOJI["partly"]
        elif base_condition == "partly":
            emoji = WEATHER_EMOJI["partly"]
        elif base_condition == "cloudy":
            emoji = WEATHER_EMOJI["cloudy"]
        elif base_condition == "mist":
            emoji = WEATHER_EMOJI["mist"]
        elif base_condition == "snow":
            emoji = WEATHER_EMOJI["snow"]
        else:
            emoji = WEATHER_EMOJI.get(base_condition, "🌤️")

        hourly.append({"hour": hour_time, "temp": temp, "emoji": emoji})

    return hourly



def outfit_logic_from_weather(weather: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply simple rule-based logic to produce outfit suggestions and a confidence score.
    Returns a dict with keys:
      - primary: dict(top,bottom,outer,footwear,accessories)
      - alternates: list of 2 outfits
      - confidence: int 0-100
      - reasoning: short string
      - bullets: list[str]
    """
    temp = weather["temp_c"]
    hum = weather["humidity"]
    precip = weather["precip_chance"]
    wind = weather["wind_kmh"]

    # Helper to create outfit dicts
    def outfit(top, bottom, outer, footwear, accessories):
        return {
            "top": top,
            "bottom": bottom,
            "outerwear": outer,
            "footwear": footwear,
            "accessories": accessories,
        }

    # Base recommendations
    reasons = []
    matches = 0

    # Rule matches accumulate
    if temp >= 30 and hum >= 65:
        # hot and humid
        matches += 2
        primary = outfit("Breathable cotton t-shirt", "Light cotton shorts", "None", "Sandals", "Cap")
        alt1 = outfit("Linen shirt", "Chino shorts", "Light scarf", "Slip-ons", "Sunglasses")
        alt2 = outfit("Moisture-wicking tee", "Athletic shorts", "None", "Sport sandals", "Small umbrella" if precip > 30 else "Cap")
        reasons.append(f"High temperature ({temp} °C) and humidity ({hum}%) → breathable fabrics")
    elif 22 <= temp < 30:
        matches += 2
        primary = outfit("Light long-sleeve tee", "Chinos", "Light layer (cardigan)", "Sneakers", "Watch")
        alt1 = outfit("Polo shirt", "Jeans", "Light jacket", "Casual sneakers", "Sunglasses")
        alt2 = outfit("Button-up shirt", "Tailored shorts", "Light hoodie", "Loafers", "Cap")
        reasons.append(f"Moderate temperature ({temp} °C) → light layers")
    elif 18 <= temp < 22:
        matches += 2
        primary = outfit("Long-sleeve shirt", "Jeans", "Light jacket", "Sneakers", "Beanie (optional)")
        alt1 = outfit("Thermal tee", "Corduroy pants", "Denim jacket", "Ankle boots", "Scarf")
        alt2 = outfit("Sweater", "Chinos", "Trench coat", "Casual boots", "Watch")
        reasons.append(f"Cool temperature ({temp} °C) → consider light outerwear")
    else:
        # temp < 18
        matches += 3
        primary = outfit("Thermal top", "Warm trousers", "Warm coat", "Boots", "Scarf & gloves")
        alt1 = outfit("Wool sweater", "Jeans", "Puffer jacket", "Insulated boots", "Beanie")
        alt2 = outfit("Turtleneck", "Wool skirt + tights", "Overcoat", "Knee boots", "Gloves")
        reasons.append(f"Cold temperature ({temp} °C) → warm outerwear recommended")

    # Rain logic
    if precip > 40:
        matches += 2
        # add umbrella or raincoat into accessories/outer if not present
        primary["accessories"] = (primary.get("accessories", "") + ", Umbrella").strip(", ")
        if primary.get("outerwear") in (None, "None"):
            primary["outerwear"] = "Packable raincoat"
        reasons.append(f"High precipitation chance ({precip}%) → carry umbrella or wear raincoat")

    # Humidity bias
    if hum > 70:
        matches += 1
        # prefer breathable options: tweak wording
        primary["top"] = primary["top"].replace("Wool", "Breathable wool-blend") if "Wool" in primary["top"] else primary["top"]
        reasons.append(f"High humidity ({hum}%) → prefer breathable fabrics and avoid heavy layers")

    # Wind consideration
    if wind > 30:
        matches += 1
        # note wind influence in reasons
        reasons.append(f"Windy ({wind} km/h) → consider secure footwear and windproof layers")

    # Confidence: scale matches into 50..100 roughly
    confidence = min(100, 40 + matches * 12)
    # Small tweak: temp extremes increase confidence
    if temp >= 30 or temp < 18:
        confidence = min(100, confidence + 8)

    # Short reasoning sentence (one-liner)
    reasoning = f"{' and '.join([s.split('→')[0].strip() for s in reasons[:2]])} — choose accordingly."

    # Ensure alternates differ: tweak slightly if duplicates
    def ensure_variation(base, alt):
        # Guarantees alt differs at least in footwear or accessories
        if base["footwear"] == alt["footwear"] and base["accessories"] == alt["accessories"]:
            alt["footwear"] = alt["footwear"] + " (alt)"
        return alt

    alt1 = ensure_variation(primary, alt1)
    alt2 = ensure_variation(primary, alt2)

    return {
        "primary": primary,
        "alternates": [alt1, alt2],
        "confidence": int(confidence),
        "reasoning": reasoning,
        "bullets": reasons,
    }


# -------------------------
# UI Components (helpers)
# -------------------------

def inject_css(light_mode: bool) -> None:
    """
    Inject CSS to style the Streamlit app with a glassy dark or light theme.
    """
    dark_bg = "#0b0f16"
    panel = "#0f1720"
    glass = "rgba(255,255,255,0.03)"
    text = "#e6edf3"
    accent = "#60a5fa"  # soft blue
    light_bg = "#f7fafc"
    light_panel = "#ffffff"
    light_text = "#0b1220"
    if light_mode:
        css = f"""
        <style>
        :root {{
            --bg: {light_bg};
            --panel: {light_panel};
            --text: {light_text};
            --accent: #2563eb;
        }}
        .reportview-container, .main {{
            background: var(--bg);
        }}
        .card {{
            background: linear-gradient(180deg, var(--panel), #f3f4f6);
            color: var(--text);
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 6px 18px rgba(15,23,42,0.06);
            border: 1px solid rgba(0,0,0,0.04);
        }}
        .badge {{
            background: var(--panel);
            color: var(--text);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
        }}
        .muted {{ color: #475569; }}
        .forecast-item {{ display:inline-block; margin-right:8px; padding:6px 8px; border-radius:8px; }}
        </style>
        """
    else:
        css = f"""
        <style>
        :root {{
            --bg: {dark_bg};
            --panel: {panel};
            --text: {text};
            --accent: {accent};
        }}
        .reportview-container, .main {{
            background: linear-gradient(180deg, var(--bg), #071021);
        }}
        .card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            color: var(--text);
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 6px 18px rgba(2,6,23,0.7);
            border: 1px solid rgba(255,255,255,0.03);
            backdrop-filter: blur(6px);
        }}
        .badge {{
            background: rgba(255,255,255,0.04);
            color: var(--text);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
        }}
        .muted {{ color: rgba(230,237,243,0.7); opacity:0.8; }}
        .forecast-item {{ display:inline-block; margin-right:8px; padding:6px 8px; border-radius:8px; }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def render_header() -> None:
    """
    Simple fixed dark header with app name only.
    """
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; justify-content:space-between;
                    padding:8px 12px; background:rgba(255,255,255,0.02);
                    border-bottom:1px solid rgba(255,255,255,0.05);'>
            <div style='font-weight:700; font-size:22px; color:#e6edf3;'>{APP_TITLE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )




def landing_page() -> None:
    """
    Landing page with Enter button.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin-bottom:6px'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    # Enter button centered
    if st.button("Enter", key="enter_button"):
        st.session_state.page = "main"
        st.session_state.forecast_generated = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def ui_main() -> None:
    """
    Main UI after Enter is clicked.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    render_header()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Two-column layout: main (left) and sidebar (right)
    left_col, right_col = st.columns([2.4, 1])

    with left_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2>Dress smarter for today’s weather.</h2>", unsafe_allow_html=True)
        st.markdown("<p class='muted'>Select your city and get a demo outfit forecast (static data).</p>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # City select
        selected = st.selectbox("Select city (State — Capital)", options=[""] + CAPITALS, index=0)
        st.session_state.selected_city = selected if selected else None

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        # Forecast button
        if st.button("Forecast my outfit", key="forecast_button"):
            if not st.session_state.selected_city:
                st.warning("Please choose a city from the dropdown before forecasting.")
            else:
                # generate forecast and outfit using deterministic mapping
                weather = synthesize_weather(st.session_state.selected_city)
                outfit_result = outfit_logic_from_weather(weather)
                hourly = generate_hourly_forecast(weather["temp_c"], weather["condition"])
                # store result
                st.session_state.last_result = {
                    "city": st.session_state.selected_city,
                    "weather": weather,
                    "outfit": outfit_result,
                    "hourly": hourly,
                    "time": datetime.now().isoformat(),
                }
                st.session_state.forecast_generated = True
                # no rerun needed, the UI will update below

        # If forecast exists show the outfit card
        if st.session_state.forecast_generated and st.session_state.last_result:
            try:
                show_outfit_card(st.session_state.last_result)
            except Exception as e:
                st.error(f"An unexpected error occurred while rendering the result: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Weather Summary</h3>", unsafe_allow_html=True)
        if st.session_state.selected_city and st.session_state.forecast_generated and st.session_state.last_result:
            show_weather_sidebar(st.session_state.last_result)
        else:
            # show placeholder mock summary
            now = datetime.now().strftime("%I:%M %p")
            st.markdown(f"<div style='font-size:14px'><strong>City:</strong> <span class='muted'>Not selected</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:14px'><strong>Time:</strong> {now}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='muted'>Select a city and click 'Forecast my outfit' to see a demo forecast.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def show_outfit_card(result: Dict[str, Any]) -> None:
    """
    Render the outfit recommendation card from stored result.
    """
    city = result["city"]
    weather = result["weather"]
    outfit = result["outfit"]

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h3>Today's Recommendation — <span class='muted' style='font-weight:500'>{city}</span></h3>", unsafe_allow_html=True)

    # Top line: short reasoning and confidence
    st.markdown(f"<div style='display:flex; align-items:center; justify-content:space-between'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:14px' class='muted'>{outfit['reasoning']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:14px; font-weight:700'>{outfit['confidence']}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Primary outfit details
    primary = outfit["primary"]
    st.markdown("<div style='display:flex; gap:12px; flex-wrap:wrap'>", unsafe_allow_html=True)
    # Render as small cards
    for k, v in primary.items():
        label = k.replace("_", " ").title()
        st.markdown(f"<div style='min-width:170px; padding:10px; border-radius:10px; background: rgba(255,255,255,0.02);'>"
                    f"<div style='font-size:12px;color:var(--accent); font-weight:700'>{label}</div>"
                    f"<div style='margin-top:6px'>{v}</div>"
                    f"</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Alternates
    st.markdown("<div style='display:flex; gap:10px; flex-wrap:wrap'>", unsafe_allow_html=True)
    for i, alt in enumerate(outfit["alternates"], start=1):
        st.markdown(f"<div style='min-width:220px; padding:10px; border-radius:10px; background: rgba(255,255,255,0.015);'>"
                    f"<div style='font-size:13px; font-weight:700'>Alternate {i}</div>"
                    f"<div style='margin-top:8px; font-size:13px'>{alt['top']} / {alt['bottom']} / {alt['footwear']}</div>"
                    f"<div style='margin-top:6px; color:var(--accent); font-size:12px'>{alt.get('accessories','')}</div>"
                    f"</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Why this outfit? expander with bullets
    with st.expander("Why this outfit?"):
        for b in outfit["bullets"]:
            st.markdown(f"- {b}")

    st.markdown("</div>", unsafe_allow_html=True)


def show_weather_sidebar(result: Dict[str, Any]) -> None:
    """
    Render the weather info in the right column using the last result.
    """
    city = result["city"]
    weather = result["weather"]
    hourly = result["hourly"]
    time_str = datetime.now().strftime("%I:%M %p")

    # Basic summary
    condition = weather.get("condition", "clear")
    emoji = WEATHER_EMOJI.get(condition, "🌤️")
    st.markdown(f"<div style='font-size:15px; font-weight:700'>{city.split('—')[-1].strip()} {emoji}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px' class='muted'>Local time: {time_str}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:22px; font-weight:700'>{weather['temp_c']} °C</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>Feels like: {weather['temp_c']} °C</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>Humidity: {weather['humidity']}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>Precipitation chance: {weather['precip_chance']}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>Wind: {weather['wind_kmh']} km/h</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; font-weight:700; margin-bottom:6px'>6-hour forecast</div>", unsafe_allow_html=True)

    # Forecast strip
    strip_html = "<div style='display:flex; flex-direction:row;'>"
    for h in hourly:
        strip_html += f"<div class='forecast-item' style='background: rgba(255,255,255,0.01); padding:8px; margin-right:6px;'>"
        strip_html += f"<div style='font-size:12px'>{h['hour']}</div>"
        strip_html += f"<div style='font-size:18px'>{h['emoji']}</div>"
        strip_html += f"<div style='font-size:13px'>{h['temp']} °C</div>"
        strip_html += "</div>"
    strip_html += "</div>"
    st.markdown(strip_html, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='muted' style='font-size:12px'>Note: This is a static demo forecast generated from the city selection.</div>", unsafe_allow_html=True)


# -------------------------
# Main app
# -------------------------

def main() -> None:
    """
    Main Streamlit app entrypoint.
    """
    init_session_state()

    # Inject CSS
    inject_css(st.session_state.light_mode)

    # Page routing
    page = st.session_state.page

    # App container
    st.title("")  # keep Streamlit chrome subtle

    if page == "landing":
        landing_page()
    else:
        ui_main()

    # Footer with small about & navigation quick links
    st.markdown("<br>", unsafe_allow_html=True)
    footer_cols = st.columns([1, 2])
    with footer_cols[0]:
        st.markdown(f"<div class='muted'>© {APP_TITLE} 2025</div>", unsafe_allow_html=True)
    with footer_cols[1]:
        st.markdown("<div style='text-align:right' class='muted'>Prototype · Frontend only · Single-file demo</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    # Safe-run guard for Streamlit
    try:
        main()
    except Exception as e:
        # If anything unexpected happens, show a friendly message in the Streamlit UI
        st.error(f"An unexpected error occurred while starting the app: {e}")
        raise
