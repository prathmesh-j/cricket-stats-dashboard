import pandas as pd
import streamlit as st
import plotly.express as px

# Load the data
@st.cache_data
def load_batting_data():
  df = pd.read_csv("huskies_2024_batting_stats.csv")
  df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
  df["Not Out"] = df["Dismissal"].str.lower().str.contains("not out")
  df["Innings Played"] = df["Dismissal"].apply(lambda x: 0 if x == "DNB" else 1)
  df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce")
  df["Balls"] = pd.to_numeric(df["Balls"], errors="coerce")
  df["4s"] = pd.to_numeric(df["4s"], errors="coerce")
  df["6s"] = pd.to_numeric(df["6s"], errors="coerce")
  df["Dots"] = pd.to_numeric(df["Dots"], errors="coerce")
  return df

@st.cache_data
def load_bowling_data():
  df = pd.read_csv("huskies_2024_bowling_stats.csv")
  df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
  df["Overs"] = pd.to_numeric(df["Overs"], errors="coerce")
  df["Wickets"] = pd.to_numeric(df["Wickets"], errors="coerce")
  df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce")
  df["Economy"] = df["Runs"] / df["Overs"].replace(0, 0.1)
  df["Opponent"] = df["Opponent"]
  print(df["Opponent"])
  return df

# Separate batting and bowling data
batting_df = load_batting_data()
bowling_df = load_bowling_data()

# Page setup
st.set_page_config("Huskies Player Dashboard", layout="wide")
st.title("🏏 Huskies Cricket Club - Player Performance Dashboard")

# === Tabs for Batting and Bowling ===
batting_tab, bowling_tab = st.tabs(["🏏 Batting Dashboard", "🎯 Bowling Dashboard"])

# ================================
# 🏏 Batting Dashboard
# ================================
with batting_tab:
  # Calculate aggregates
  agg = batting_df[batting_df["Innings Played"] == 1].groupby("Player Name").agg(
    Matches=("Date", "count"),
    Innings=("Innings Played", "sum"),
    Runs=("Runs", "sum"),
    Balls=("Balls", "sum"),
    Fours=("4s", "sum"),
    Sixes=("6s", "sum"),
    Dots=("Dots", "sum"),
    NotOuts=("Not Out", "sum")
  ).reset_index()

  agg["Average"] = agg["Runs"] / (agg["Innings"] - agg["NotOuts"]).replace(0, 1)
  agg["Strike Rate"] = (agg["Runs"] / agg["Balls"]) * 100
  agg["Avg 4s+6s"] = (agg["Fours"] + agg["Sixes"]) / agg["Innings"]
  agg["Impact Score"] = agg["Runs"] + (2 * agg["Fours"]) + (3 * agg["Sixes"])

  tab1, tab2 = st.tabs(["ProT20", "Pro40"])

  def render_batting_tab(data, format_name):
    st.subheader(f"{format_name} Batting Stats")

    # Filters
    opponents = data["Opponent"].dropna().unique().tolist()
    selected_opponent = st.selectbox("Filter by Opponent", ["All"] + opponents, key=f"{format_name}_opp")
    if selected_opponent != "All":
      data = data[data["Opponent"] == selected_opponent]

    players = data["Player Name"].unique().tolist()
    selected_player = st.selectbox("Filter by Player", ["All"] + players, key=f"{format_name}_player")
    if selected_player != "All":
      data = data[data["Player Name"] == selected_player]

    st.dataframe(data)

    top_runs = data.groupby("Player Name")["Runs"].sum().sort_values(ascending=False).head(5).reset_index()
    fig1 = px.bar(top_runs, x="Player Name", y="Runs", title="🏆 Top 5 Run Scorers")
    st.plotly_chart(fig1, use_container_width=True)

    plot_data = agg[agg["Player Name"].isin(data["Player Name"].unique())]

    fig2 = px.scatter(plot_data, x="Strike Rate", y="Average", size="Runs", color="Player Name",
                      title="📊 Strike Rate vs Batting Average")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(plot_data, x="Dots", y="Runs", size="Fours", color="Player Name",
                      title="🎯 Runs vs Dot Balls")
    st.plotly_chart(fig3, use_container_width=True)

    boundary_df = plot_data[["Player Name", "Fours", "Sixes"]].melt(id_vars="Player Name", var_name="Boundary", value_name="Count")
    fig4 = px.bar(boundary_df, x="Player Name", y="Count", color="Boundary", barmode="group",
                  title="🔥 Boundary Breakdown (4s vs 6s)")
    st.plotly_chart(fig4, use_container_width=True)

    time_df = data.groupby(["Date", "Player Name"])["Runs"].sum().reset_index()
    fig5 = px.line(time_df, x="Date", y="Runs", color="Player Name", markers=True,
                   title="📈 Timeline Trend - Runs Over Time")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### 💥 Power Hitters (4s+6s > 3)")
    power_hitters = plot_data[plot_data["Avg 4s+6s"] >= 3].sort_values("Strike Rate", ascending=False)
    st.dataframe(power_hitters[["Player Name", "Runs", "Strike Rate", "Avg 4s+6s"]])

    st.markdown("### 🚀 Recommended Openers (SR > 100)")
    openers = plot_data[(plot_data["Strike Rate"] > 100)].sort_values("Strike Rate", ascending=False)
    st.dataframe(openers[["Player Name", "Runs", "Strike Rate", "Average"]])

  with tab1:
    prot20_df = batting_df[batting_df["Tournament"].str.contains("ProT20", na=False)]
    render_batting_tab(prot20_df, "ProT20")

  with tab2:
    pro40_df = batting_df[batting_df["Tournament"].str.contains("Pro40", na=False)]
    render_batting_tab(pro40_df, "Pro40")

  # Pie Chart: Dismissal Breakdown
  st.markdown("## 🥧 Dismissal Breakdown Per Player")
  player_select = st.selectbox("Select a Player", sorted(batting_df["Player Name"].unique()))
  dismissal_data = batting_df[
    (batting_df["Player Name"] == player_select) &
    (~batting_df["Dismissal"].str.lower().isin(["dnb", "not out"]))
    ]

  def classify_dismissal(dismissal):
    d = str(dismissal).lower()
    if "runout" in d:
      return "Run Out"
    elif "lbw" in d:
      return "LBW"
    elif "c.†" in d:
      return "Caught Behind"
    elif "c." in d:
      return "Caught"
    elif "b." in d and "c." not in d:
      return "Bowled"
    return "Other"

  dismissal_data["Dismissal Type"] = dismissal_data["Dismissal"].apply(classify_dismissal)
  dismissal_counts = dismissal_data["Dismissal Type"].value_counts().reset_index()
  dismissal_counts.columns = ["Dismissal Type", "Count"]
  fig6 = px.pie(dismissal_counts, names="Dismissal Type", values="Count",
                title=f"Dismissal Types for {player_select}", hole=0.4)
  st.plotly_chart(fig6, use_container_width=True)

# ================================
# 🎯 Bowling Dashboard
# ================================
with bowling_tab:
  st.subheader("🎯 Bowling Stats")

  if bowling_df.empty:
    st.warning("No bowling data found.")
  else:
    # Filter by Opponent
    opponent_filter = st.selectbox("Select Opponent", ["All"] + sorted(bowling_df["Opponent"].dropna().unique()))
    if opponent_filter != "All":
      filtered_bowl = bowling_df[bowling_df["Opponent"] == opponent_filter]
    else:
      filtered_bowl = bowling_df

    # Filter by Player
    player_filter = st.selectbox("Select Player", ["All"] + sorted(filtered_bowl["Player Name"].unique()))
    if player_filter != "All":
      filtered_bowl = filtered_bowl[filtered_bowl["Player Name"] == player_filter]

    # Ensure numeric types
    filtered_bowl["Overs"] = pd.to_numeric(filtered_bowl["Overs"], errors="coerce")
    filtered_bowl["Runs"] = pd.to_numeric(filtered_bowl["Runs"], errors="coerce")
    filtered_bowl["Wickets"] = pd.to_numeric(filtered_bowl["Wickets"], errors="coerce")
    filtered_bowl["Maidens"] = pd.to_numeric(filtered_bowl["Maidens"], errors="coerce")
    filtered_bowl["Dots"] = pd.to_numeric(filtered_bowl.get("Dots", 0), errors="coerce")  # Optional: if dot balls are in CSV

    # Show full raw data table after filters
    # st.markdown("### 📋 Match-wise Bowling Records")
    # st.dataframe(filtered_bowl)

    # Calculate Economy
    filtered_bowl["Economy"] = filtered_bowl["Runs"] / filtered_bowl["Overs"].replace(0, 0.1)

    # Aggregate Stats
    agg_bowling = filtered_bowl.groupby("Player Name").agg(
      Matches=("Date", "count"),
      Overs=("Overs", "sum"),
      Wickets=("Wickets", "sum"),
      RunsConceded=("Runs", "sum"),
      Maidens=("Maidens", "sum"),
      Dots=("Dots", "sum") if "Dots" in filtered_bowl.columns else ("Runs", lambda x: 0),
    ).reset_index()

    agg_bowling["Economy"] = agg_bowling["RunsConceded"] / agg_bowling["Overs"].replace(0, 0.1)

    # Best Economy
    best_economy = agg_bowling.sort_values("Economy").head(7)
    top_wickets = agg_bowling.sort_values("Wickets", ascending=False).head(5)

    # Show Summary Table
    st.markdown("### 📊 Summary by Player")
    st.dataframe(agg_bowling)

    # Charts
    fig1 = px.bar(top_wickets,
                  x="Player Name", y="Wickets",
                  title="🎯 Top Wicket Takers")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(agg_bowling, x="Economy", y="Wickets",
                      size="Overs", color="Player Name",
                      title="📊 Wickets vs Economy")
    st.plotly_chart(fig2, use_container_width=True)

    # Maidens and Dot Balls
    if "Dots" in agg_bowling.columns:
      st.markdown("### 💎 Control Bowlers (Maidens)")
      fig3 = px.bar(agg_bowling.sort_values("Maidens", ascending=False),
                    x="Player Name", y="Maidens", color="Maidens",
                    title="🛑 Dot Balls by Bowlers (Colored by Maidens)")
      st.plotly_chart(fig3, use_container_width=True)

    # Best Economy Chart
    st.markdown("### 🧊 Most Economical Bowlers")
    fig4 = px.bar(best_economy,
                  x="Player Name", y="Economy",
                  title="📉 Best Economy Rates")
    st.plotly_chart(fig4, use_container_width=True)
