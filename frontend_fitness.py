import streamlit as st
import pandas as pd
from backend_fitness import DatabaseManager
from datetime import datetime

# Initialize database manager (replace with your actual credentials)
db = DatabaseManager(
    dbname="FITNESS TRACKER_30221",
    user="Postgres",
    password="Vaishnavi",
    host="localhost"
)

def main():
    st.title("💪 Fitness Tracker")

    if not db.connect():
        st.error("Could not connect to the database. Please check your credentials.")
        return

    # User Login/Profile (Simplified)
    st.sidebar.header("User Profile")
    user_email = st.sidebar.text_input("Enter your email:")
    user_data = None
    if user_email:
        user_data = db.get_user_by_email(user_email)
        if not user_data:
            st.warning("User not found. Please create a new profile.")
            name = st.sidebar.text_input("Name:")
            goal = st.sidebar.text_area("Your Fitness Goal:")
            if st.sidebar.button("Create Profile"):
                user_id = db.create_user(name, user_email, goal)
                if user_id:
                    st.sidebar.success(f"Profile created for {name}!")
                    user_data = (user_id, name, user_email, goal)
                else:
                    st.sidebar.error("Failed to create profile.")
        
        if user_data:
            st.sidebar.info(f"Welcome, {user_data[1]}!")
            st.session_state['user_id'] = user_data[0]
        else:
            st.sidebar.warning("Please enter your email to proceed.")
            return
    else:
        st.sidebar.warning("Please enter your email to proceed.")
        return
        
    st.markdown("---")
    
    # Navigation
    menu = ["Log Workout", "Workout History", "Leaderboard"]
    choice = st.sidebar.selectbox("Menu:", menu)

    if choice == "Log Workout":
        st.header("🏋️ Log a New Workout")
        with st.form("workout_form"):
            workout_date = st.date_input("Date", datetime.now())
            duration = st.number_input("Duration (minutes)", min_value=1)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Log Workout")

            if submitted:
                workout_id = db.create_workout(st.session_state['user_id'], workout_date, duration, notes)
                if workout_id:
                    st.success("Workout logged successfully!")
                    
                    st.subheader("Add Exercises")
                    num_exercises = st.number_input("How many exercises did you do?", min_value=1, value=1)
                    
                    for i in range(num_exercises):
                        with st.expander(f"Exercise #{i+1}"):
                            exercise_name = st.text_input("Exercise Name", key=f"ex_name_{i}")
                            sets = st.number_input("Sets", min_value=1, key=f"sets_{i}")
                            reps = st.number_input("Reps", min_value=1, key=f"reps_{i}")
                            weight = st.number_input("Weight (kg)", min_value=0.0, key=f"weight_{i}")
                            
                            if st.button("Add Exercise", key=f"add_ex_{i}"):
                                if db.create_exercise(workout_id, exercise_name, sets, reps, weight):
                                    st.success(f"Exercise '{exercise_name}' added!")
                                else:
                                    st.error("Failed to add exercise.")
                else:
                    st.error("Failed to log workout.")
                    
    elif choice == "Workout History":
        st.header("📅 My Workout History")
        
        # User Stats
        stats = db.get_workout_stats(st.session_state['user_id'])
        if stats:
            st.subheader("Your Progress")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Workouts", stats['total_workouts'])
            with col2:
                st.metric("Total Duration", f"{stats['total_duration']} min")
            with col3:
                st.metric("Avg. Duration", f"{stats['avg_duration']:.2f} min")
            with col4:
                st.metric("Max Duration", f"{stats['max_duration']} min")
            with col5:
                st.metric("Min Duration", f"{stats['min_duration']} min")
        
        st.markdown("---")
        
        workouts = db.get_user_workouts(st.session_state['user_id'])
        if workouts:
            st.subheader("Log Details")
            for workout in workouts:
                workout_id, user_id, workout_date, duration, notes = workout
                st.write(f"**Date:** {workout_date} | **Duration:** {duration} minutes")
                if notes:
                    st.write(f"**Notes:** {notes}")
                
                exercises = db.get_exercises_for_workout(workout_id)
                if exercises:
                    df_exercises = pd.DataFrame(exercises, columns=['Exercise', 'Sets', 'Reps', 'Weight (kg)'])
                    st.dataframe(df_exercises)
                else:
                    st.write("No exercises logged for this workout.")
                st.markdown("---")
        else:
            st.info("You haven't logged any workouts yet.")
            
    elif choice == "Leaderboard":
        st.header("🏆 Weekly Leaderboard")
        st.info("Ranking based on total workout duration this week.")
        
        leaderboard_data = db.get_weekly_leaderboard()
        if leaderboard_data:
            df_leaderboard = pd.DataFrame(leaderboard_data, columns=['Name', 'Total Duration (min)'])
            df_leaderboard.index = range(1, len(df_leaderboard) + 1)
            st.table(df_leaderboard)
        else:
            st.info("No one has logged a workout this week yet.")

    db.disconnect()

if __name__ == '__main__':
    main()
