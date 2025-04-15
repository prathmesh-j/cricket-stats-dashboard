# cricket-stats-dashboard
This Streamlit web application provides an interactive dashboard to analyze the batting and bowling performance of players from the Huskies Cricket Club during the 2024 season. It pulls data from match scorecards and aggregates key performance metrics for each player.

🔍 Key Features:
- Batting Dashboard: View runs, strike rates, averages, boundaries, and power-hitting analysis.
- Bowling Dashboard: Analyze wickets, economy rates, maidens, dot balls, and match-wise bowling records.
- Interactive Filters: Filter stats by opponent and player name.
- Visual Insights: Charts to compare top performers, batting impact, and bowling efficiency.
- Dismissal Breakdown: Pie chart of dismissal types for each player.

The app helps team members, analysts, and fans understand player form, strengths, and areas of impact in both batting and bowling formats.


## 🚀 How to Run the Huskies Cricket Dashboard App
🛠️ Prerequisites
Ensure the following are installed:
- Python 3.8+
- pipx

### 📦 1. Install Required Packages

Open your terminal/command prompt and run:
```bash
pipx install streamlit pandas plotly
```

### 📁 2. Prepare Your Files
Place the following files in the same directory:

- app.py – The main Streamlit script (the one we built).
- huskies_2024_batting.csv – CSV file with batting stats.
- huskies_2024_bowling.csv – CSV file with bowling stats.

Make sure your CSV file names match the filenames used in the code, or update the file paths in the script accordingly.

### ▶️ 3. Run the Streamlit App
In the terminal, navigate to the folder containing the files and run:

```bash
streamlit run app.py
```

### 🌐 4. View in Browser
Once the app starts, it will open automatically in your browser. If not, go to:
```http://localhost:8501```
