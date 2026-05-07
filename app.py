from ai_recommendations import get_ai_coaching, analyze_weak_topics, get_daily_challenge
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Initialize database
def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        created_at TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        problem_name TEXT,
        platform TEXT,
        difficulty TEXT,
        topic TEXT,
        time_taken INTEGER,
        solved_date DATE,
        notes TEXT
    )''')
    conn.commit()
    conn.close()

# Initialize
init_db()

# Page config
st.set_page_config(page_title="CodeTrack AI", page_icon="📊", layout="wide")

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Title
st.title("📊 CodeTrack AI")
st.markdown("*AI-Powered Coding Practice Tracker for B.Tech CSE Students*")
st.markdown("---")

# Sidebar for login/signup
with st.sidebar:
    st.markdown("## 🔐 Account")
    if not st.session_state.logged_in:
        option = st.radio("Choose Option", ["Login", "Signup"])
        
        if option == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", width='stretch'):
                conn = sqlite3.connect('data/tracker.db')
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                user = c.fetchone()
                conn.close()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = user[0]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            if st.button("Sign Up", width='stretch'):
                if new_username and new_password:
                    conn = sqlite3.connect('data/tracker.db')
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                                 (new_username, new_password, datetime.now()))
                        conn.commit()
                        st.success("Account created! Please login.")
                        st.balloons()
                    except:
                        st.error("Username already exists")
                    conn.close()
                else:
                    st.warning("Please fill all fields")
    else:
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        if st.button("Logout", width='stretch'):
            st.session_state.logged_in = False
            st.rerun()

# Main content when logged in
if st.session_state.logged_in:
    tabs = st.tabs(["📊 Dashboard", "➕ Add Problem", "📈 Analytics", "📝 My Problems", "🤖 AI Coach"])
    
    with tabs[0]:
        st.header("Your Coding Dashboard")
        conn = sqlite3.connect('data/tracker.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM problems WHERE user_id=?", (st.session_state.user_id,))
        total = c.fetchone()[0]
        c.execute("SELECT difficulty, COUNT(*) FROM problems WHERE user_id=? GROUP BY difficulty", (st.session_state.user_id,))
        diff_stats = dict(c.fetchall())
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Total Solved", total)
        with col2:
            st.metric("✅ Easy", diff_stats.get('Easy', 0))
        with col3:
            st.metric("⚡ Medium", diff_stats.get('Medium', 0))
        with col4:
            st.metric("🔥 Hard", diff_stats.get('Hard', 0))
        
        if total > 0:
            st.markdown("---")
            st.subheader("📊 Problem Distribution")
            if diff_stats:
                st.bar_chart(diff_stats)
        else:
            st.info("No problems added yet. Start by adding your first problem!")
    
    with tabs[1]:
        st.header("➕ Log a Solved Problem")
        with st.form("add_problem_form"):
            col1, col2 = st.columns(2)
            with col1:
                problem_name = st.text_input("Problem Name *")
                platform = st.selectbox("Platform", ["LeetCode", "Codeforces", "HackerRank", "GeeksforGeeks", "Other"])
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            with col2:
                topic = st.selectbox("Topic", ["Arrays", "Strings", "Hash Table", "Dynamic Programming", "Graphs", "Trees", "Sorting", "Others"])
                time_taken = st.number_input("Time Taken (minutes)", min_value=1, max_value=300, value=30)
                solved_date = st.date_input("Date Solved", datetime.now())
            notes = st.text_area("Notes (optional)", placeholder="What did you learn?")
            submitted = st.form_submit_button("💾 Save Problem", width='stretch')
            if submitted and problem_name:
                conn = sqlite3.connect('data/tracker.db')
                c = conn.cursor()
                c.execute('''INSERT INTO problems (user_id, problem_name, platform, difficulty, topic, time_taken, solved_date, notes)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (st.session_state.user_id, problem_name, platform, difficulty, topic, time_taken, solved_date, notes))
                conn.commit()
                conn.close()
                st.success(f"✅ Added '{problem_name}' successfully!")
                st.rerun()
            elif submitted:
                st.warning("Please enter the problem name")
    
    with tabs[2]:
        st.header("📈 Analytics")
        conn = sqlite3.connect('data/tracker.db')
        df = pd.read_sql_query(f"SELECT * FROM problems WHERE user_id={st.session_state.user_id}", conn)
        conn.close()
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Difficulty Breakdown")
                diff_data = df['difficulty'].value_counts()
                st.bar_chart(diff_data)
            with col2:
                st.subheader("Top Topics")
                topic_data = df['topic'].value_counts().head(5)
                st.bar_chart(topic_data)
            st.markdown("---")
            st.subheader("Problems Over Time")
            df['solved_date'] = pd.to_datetime(df['solved_date'])
            daily_counts = df.groupby('solved_date').size()
            st.line_chart(daily_counts)
        else:
            st.info("Add some problems to see analytics!")
    
    with tabs[3]:
        st.header("📝 Your Problem Log")
        conn = sqlite3.connect('data/tracker.db')
        problems_df = pd.read_sql_query(f"SELECT problem_name, platform, difficulty, topic, time_taken, solved_date FROM problems WHERE user_id={st.session_state.user_id} ORDER BY solved_date DESC", conn)
        conn.close()
        if not problems_df.empty:
            st.dataframe(problems_df, use_container_width=True)
            csv = problems_df.to_csv(index=False)
            st.download_button("📥 Download as CSV", csv, "my_coding_progress.csv", "text/csv")
        else:
            st.info("No problems logged yet. Add your first problem!")
    
    with tabs[4]:
        st.header("🤖 Your AI Coding Coach")
        st.markdown("Personalized recommendations powered by Google Gemini AI")
        
        # Get user stats for AI
        conn = sqlite3.connect('data/tracker.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM problems WHERE user_id=?", (st.session_state.user_id,))
        total_solved = c.fetchone()[0]
        
        # Get streak (simplified for now)
        streak_days = 1 if total_solved > 0 else 0
        
        # Get topic counts - FIXED VERSION
        topic_query = "SELECT topic, COUNT(*) as problem_count FROM problems WHERE user_id=? GROUP BY topic"
        topic_df = pd.read_sql_query(topic_query, conn, params=(st.session_state.user_id,))
        conn.close()
        
        # Create topic counts dictionary safely
        if not topic_df.empty:
            topic_counts = dict(zip(topic_df['topic'], topic_df['problem_count']))
        else:
            topic_counts = {}
        
        # Create tabs for different AI features
        ai_tab1, ai_tab2, ai_tab3 = st.tabs(["🎯 Coaching", "📊 Weakness Analysis", "🎲 Daily Challenge"])
        
        with ai_tab1:
            st.subheader("Your AI Coach Says...")
            with st.spinner("Getting AI insights..."):
                weak_topics = list(topic_counts.keys()) if topic_counts else []
                coaching = get_ai_coaching(weak_topics, total_solved, streak_days)
                st.markdown(f"💡 {coaching}")
        
        with ai_tab2:
            st.subheader("Topic Weakness Analysis")
            with st.spinner("Analyzing your performance..."):
                analysis = analyze_weak_topics(topic_counts)
                st.markdown(analysis)
            
            if topic_counts:
                st.subheader("📊 Your Topic Distribution")
                # Convert to DataFrame for better display
                topic_df_display = pd.DataFrame(list(topic_counts.items()), columns=['Topic', 'Problems Solved'])
                st.bar_chart(topic_df_display.set_index('Topic'))
        
        with ai_tab3:
            st.subheader("Today's Personalized Challenge")
            if st.button("🎲 Generate New Challenge", width='stretch'):
                with st.spinner("Creating your challenge..."):
                    challenge = get_daily_challenge(topic_counts, total_solved)
                    st.markdown(challenge)
            else:
                # Show default challenge
                challenge = get_daily_challenge(topic_counts, total_solved)
                st.markdown(challenge)