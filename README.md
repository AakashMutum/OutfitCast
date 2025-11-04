# 👕 OutfitCast — Weather-Based Smart Outfit Recommendation System  

> *Dress smarter for today’s weather.*  
> **Forecast your outfit.**

---

## 🌍 Problem Statement  

In cities where weather changes rapidly — like Chennai, Mumbai, or Bangalore — deciding what to wear each day can be surprisingly tricky.  
Temperature, humidity, wind, and rainfall fluctuate often, making it hard to balance **comfort**, **style**, and **practicality**.  

People rely on multiple apps: one for weather, another for outfit inspiration, and still end up making guesses.  
Our project aims to bring all of this into **one intelligent, personalized platform**.

---

## 💡 Solution  

**OutfitCast** is a smart, single-page web application that analyzes local weather conditions and recommends outfits best suited for the user’s comfort and environment.  

Built entirely in **Python (Streamlit)**, the app simulates a real-time experience — complete with weather summaries, hourly forecasts, and outfit cards — while being API-ready for live integration in the future.  

✨ *Because sometimes, what you wear depends on what the sky says — OutfitCast helps you forecast your outfit.*  

---

## 🎯 Core Features
- 🌦️ **City-based Forecast:** Select any Indian capital from a dropdown to get weather-linked outfit ideas.  
- 👕 **Outfit Recommendation Engine:** Suggests tops, bottoms, outerwear, footwear, and accessories.  
- 🕒 **Time & Forecast Display:** Real-time local time display and a 6-hour forecast simulator.  
- 🧠 **Rule-Based Logic:** Temperature, humidity, and rainfall rules determine clothing suggestions.  
- 💻 **Responsive UI:** Designed with a sleek dark theme and modern spacing for readability and polish.  
- ⚙️ **Future-Ready:** The structure is built to plug directly into the Open-Meteo API for live weather data.  

---

## 🧱 Tech Stack  

| Component | Technology Used |
|------------|-----------------|
| Language | Python |
| Framework | Streamlit |
| Styling | Custom CSS |
| Data Source | Dummy simulated weather data (API-ready) |
| Deployment | Netlify / Vercel-friendly (via Streamlit Cloud) |

---

## 🧩 How It Works  

1. **User selects a city** from the dropdown list of Indian capitals.  
2. The system simulates **realistic weather data** (temperature, humidity, and forecast icons).  
3. A **rule-based outfit logic engine** processes this data and outputs:  
   - A main outfit suggestion  
   - Two alternate outfit ideas  
   - Quick reasoning behind each (e.g., “High humidity and 32°C — choose breathable cotton and carry an umbrella.”)  
4. The interface displays **current weather**, **local time**, and a **6-hour mini forecast** — all dynamically generated.  

---

## 🧠 What We Have Built  

- A **complete frontend skeleton** ready for live data integration.  
- A **responsive, accessible, production-ready UI** made entirely in Python — no HTML or JS required.  
- A **clean modular structure** (single-file build) that can be easily expanded for personalization or notifications.  
- **Robust placeholder logic** mimicking real API behavior (with graceful error handling already structured).  

---

## 🚀 Future Updates  

We’re turning this prototype into a truly smart weather-aware fashion assistant.  
Planned enhancements include:  

- 🌐 **Live Weather Integration** using [Open-Meteo API](https://open-meteo.com/)  
- 👗 **Personal Wardrobe System** — users mark owned items and get personalized suggestions  
- ⚙️ **User Preferences Panel** — choose comfort vs. style bias  
- 🔔 **Daily Notifications** — morning outfit reminders based on the day’s forecast  
- 📱 **Progressive Web App (PWA)** — add to home screen & offline functionality  
- 🧵 **AI-Powered Recommendation Engine** — learns user style preferences over time  

---

## 🧭 How to Run Locally  

```bash
# 1. Clone the repository
git clone https://github.com/<yourusername>/OutfitCast.git
cd OutfitCast

# 2. Install dependencies
pip install streamlit

# 3. Run the app
streamlit run OutfitCast.py
```

Your app will open automatically in your default browser at  
👉 `http://localhost:8501`

---

## 🪄 UI Preview  

| Feature | Description |
|----------|--------------|
| 🏠 **Landing Page** | Elegant dark interface with “Enter” button |
| 🌆 **City Selector** | Dropdown of Indian capitals with state names |
| ☁️ **Weather Card** | Displays current temperature, humidity, and forecast icons |
| 👕 **Outfit Suggestions** | Three recommendations with reasoning lines |
| 🕐 **Forecast Strip** | Shows six upcoming hourly predictions |
| 💫 **Polished Design** | Clean typography, smooth transitions, and compact layout |

---

## 🧑‍💻 Team Vision  

We wanted to build something that feels **useful, beautiful, and effortless**.  
OutfitCast bridges the gap between *weather awareness* and *daily comfort*, proving that technology can make even the simplest routines — like dressing up — smarter and easier.  

> ☁️ **OutfitCast — Forecast your outfit.**

---

## 🏁 Summary  

> “OutfitCast helps you dress with confidence, no matter the forecast.”  

This project stands as a complete foundation for a **data-driven, user-personalized outfit recommendation platform** — built with simplicity, scalability, and future innovation in mind.

---

**Made with ❤️ using Python & Streamlit**
