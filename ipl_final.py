import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "kavya"
DB_PORT = "5432"


def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def query_data(query):
    conn = get_connection()
    if conn is not None:
        try:
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return None
    else:
        return None
    
st.set_page_config(
    page_title="IPL Player Comparison",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

data1 = load_data(r"C:\Users\Administrator\pythonn\ipl_Dataset.csv").copy()
data2 = load_data(r"C:\Users\Administrator\pythonn\team_performance_dataset_2008to2024.csv").copy()

st.title("IPL Player Comparison")
st.sidebar.header("Select Players to Compare")

# Combine unique players from 'Striker' and 'Bowler' columns
players = pd.concat([data1['Striker'], data1['Bowler']]).unique()

Player1 = st.sidebar.selectbox("Select First Player:", players)
Player2 = st.sidebar.selectbox("Select Second Player:", players)

if Player1 != Player2:
    st.header(f"Comparing {Player1} and {Player2}")

    Player1_data_bat = data1[data1['Striker'] == Player1]
    Player2_data_bat = data1[data1['Striker'] == Player2]
    Player1_data_bowl = data1[data1['Bowler'] == Player1]
    Player2_data_bowl = data1[data1['Bowler'] == Player2]

    # Define the metrics to compare
    batting_metrics = ['runs_scored']
    bowling_metrics = ['wicket_confirmation']

    player_of_match_counts = data2['Player_of_Match'].value_counts()

    # Adding Player of the Match comparison
    Player1_pom_count = player_of_match_counts.get(Player1, 0)
    Player2_pom_count = player_of_match_counts.get(Player2, 0)

    st.write(f"### Player of the Match Awards")
    st.write(f"{Player1}: {Player1_pom_count}")
    st.write(f"{Player2}: {Player2_pom_count}")

    fig, ax = plt.subplots()
    ax.bar([Player1, Player2], [Player1_pom_count, Player2_pom_count], color=['blue', 'green'])
    ax.set_ylabel('Player of the Match Count')
    ax.set_title('Player of the Match Comparison')
    st.pyplot(fig)

    # Batting metrics comparison
    for metric in batting_metrics:
        if metric in data1.columns:
            Player1_metric = Player1_data_bat[metric].sum()
            Player2_metric = Player2_data_bat[metric].sum()

            st.write(f"### {metric}")
            st.write(f"{Player1}: {Player1_metric}")
            st.write(f"{Player2}: {Player2_metric}")

            fig, ax = plt.subplots()
            ax.bar([Player1, Player2], [Player1_metric, Player2_metric], color=['blue', 'green'])
            ax.set_ylabel(metric)
            ax.set_title(f"{metric} Comparison")
            st.pyplot(fig)
        else:
            st.error(f"Column '{metric}' does not exist in the dataset.")

    # Adding strike rate comparison
    query_player1_sr = f"""
    SELECT (CAST(SUM(runs_scored) AS float) / COUNT(ball_no)) * 100 AS strike_rate
    FROM ipl_final
    WHERE Striker = '{Player1}';
    """

    query_player2_sr = f"""
    SELECT (CAST(SUM(runs_scored) AS float) / COUNT(ball_no)) * 100 AS strike_rate
    FROM ipl_final
    WHERE Striker = '{Player2}';
    """

    Player1_strike_rate = query_data(query_player1_sr)
    Player2_strike_rate = query_data(query_player2_sr)

    if Player1_strike_rate is not None and Player2_strike_rate is not None:
        Player1_sr = Player1_strike_rate.iloc[0]['strike_rate']
        Player2_sr = Player2_strike_rate.iloc[0]['strike_rate']

        st.write(f"### Strike Rate Comparison")
        st.write(f"{Player1}: {Player1_sr:.2f}" if Player1_sr is not None else f"{Player1}: N/A")
        st.write(f"{Player2}: {Player2_sr:.2f}" if Player2_sr is not None else f"{Player2}: N/A")

        fig, ax = plt.subplots()
        ax.bar([Player1, Player2], [Player1_sr, Player2_sr], color=['blue', 'green'])
        ax.set_ylabel('Strike Rate')
        ax.set_title('Strike Rate Comparison')
        st.pyplot(fig)

    # Adding batting average comparison
    query_player1_ba = f"""
    SELECT (CAST(SUM(runs_scored) AS float) / NULLIF(COUNT(CASE WHEN wicket_confirmation = '1' THEN 1 END), 0)) AS batting_average
    FROM ipl_final
    WHERE Striker = '{Player1}';
    """

    query_player2_ba = f"""
    SELECT (CAST(SUM(runs_scored) AS float) / NULLIF(COUNT(CASE WHEN wicket_confirmation = '1' THEN 1 END), 0)) AS batting_average
    FROM ipl_final
    WHERE Striker = '{Player2}';
    """

    Player1_batting_average = query_data(query_player1_ba)
    Player2_batting_average = query_data(query_player2_ba)

    if Player1_batting_average is not None and Player2_batting_average is not None:
        Player1_ba = Player1_batting_average.iloc[0]['batting_average']
        Player2_ba = Player2_batting_average.iloc[0]['batting_average']

        st.write(f"### Batting Average Comparison")
        st.write(f"{Player1}: {Player1_ba:.2f}" if Player1_ba is not None else f"{Player1}: N/A")
        st.write(f"{Player2}: {Player2_ba:.2f}" if Player2_ba is not None else f"{Player2}: N/A")

        fig, ax = plt.subplots()
        ax.bar([Player1, Player2], [Player1_ba, Player2_ba], color=['blue', 'green'])
        ax.set_ylabel('Batting Average')
        ax.set_title('Batting Average Comparison')
        st.pyplot(fig)

    # Adding economy rate comparison if both are bowlers
    if Player1_data_bowl.shape[0] > 0 and Player2_data_bowl.shape[0] > 0:
        query_player1_er = f"""
        SELECT (CAST(SUM(runs_scored) AS float) / (COUNT(ball_no) / 6.0)) AS economy_rate
        FROM ipl_final
        WHERE Bowler = '{Player1}';
        """

        query_player2_er = f"""
        SELECT (CAST(SUM(runs_scored) AS float) / (COUNT(ball_no) / 6.0)) AS economy_rate
        FROM ipl_final
        WHERE Bowler = '{Player2}';
        """

        Player1_economy_rate = query_data(query_player1_er)
        Player2_economy_rate = query_data(query_player2_er)

        if Player1_economy_rate is not None and Player2_economy_rate is not None:
            Player1_er = Player1_economy_rate.iloc[0]['economy_rate']
            Player2_er = Player2_economy_rate.iloc[0]['economy_rate']

            st.write(f"### Economy Rate Comparison")
            st.write(f"{Player1}: {Player1_er:.2f}" if Player1_er is not None else f"{Player1}: N/A")
            st.write(f"{Player2}: {Player2_er:.2f}" if Player2_er is not None else f"{Player2}: N/A")

            fig, ax = plt.subplots()
            ax.bar([Player1, Player2], [Player1_er, Player2_er], color=['blue', 'green'])
            ax.set_ylabel('Economy Rate')
            ax.set_title('Economy Rate Comparison')
            st.pyplot(fig)
        else:
            st.error("Error fetching economy rate data.")
    else:
        st.warning("Select two bowlers to compare economy rates.")

else:
    st.write("Please select two different players for comparison.")

st.sidebar.write("Powered by IPL Data Analysis")
