import streamlit as st
import base64
import random


@st.cache_data
def initialize_game():
    doors = ['goat', 'goat', 'car']
    random.shuffle(doors)
    return doors

def initialize_history():
    return {"Switch Wins": 0, "Switch Losses": 0, "No Switch Wins": 0, "No Switch Losses": 0}

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay loop>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def home_page(history):
    st.title("Welcome to the Monty Hall Problem Simulator! 🚪🎮")
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/3f/Monty_open_door.svg", use_container_width=True)
    st.header("Understanding the Monty Hall Problem")
    st.markdown("""
    The Monty Hall Problem is a fascinating probability puzzle based on a game show:
    
    - **Step 1**: You choose one of three doors. Behind one is a car 🚗, and behind the other two are goats 🐐.
    - **Step 2**: The host, Monty Hall, reveals a goat behind one of the other two doors.
    - **Step 3**: You are given the choice to stick with your original door or switch to the remaining unopened door.
    """)
    with st.expander("Show Strategy"):
        st.markdown("""
        ### Why Switching is Better:
        - Initially, your door has a **1/3 chance of winning** (the car) and the other two doors collectively have **2/3 chance**.
        - Monty’s action of revealing a goat effectively transfers the **2/3 chance** to the remaining unopened door.
        - By switching, you capitalize on this **filtered probability**, giving you **2/3 odds of winning**.
        
        ### Visualizing with 100 Doors:

        Imagine there are 100 doors. You pick one at random, so your chance of winning is **1/100**. Monty opens 98 doors, all with goats. The last unopened door now has a **99/100 chance** of being the car! Switching clearly improves your odds.
        """)
        st.image("https://www.adit.io/imgs/montyhall/100doors_sheep_choice_nums.PNG", use_container_width=True)

    st.markdown("""
    ### How to Use This App
    - **Auto Mode**: Simulate multiple games to see win rates for switching vs. not switching.
    - **Player Mode**: Play interactively, one decision at a time!
    """)
    st.subheader("Game History")
    st.write(history)

def player_mode(history):
    st.title("Player Mode: Play Step-by-Step 🎮")

    # Initialize session state variables
    if "step" not in st.session_state:
        st.session_state.step = 1
        st.session_state.doors = initialize_game()
        st.session_state.initial_choice = None
        st.session_state.revealed_door = None
        st.session_state.final_result = None
        st.session_state.switch = None  # Initialize switch decision

    doors = st.session_state.doors

    if st.session_state.step == 1:
        st.subheader("Step 1: Choose a Door")
        st.write("Pick a door (1, 2, or 3).")
        st.session_state.initial_choice = st.radio("Your choice:", [1, 2, 3]) - 1  # Adjust for 0-based indexing
        if st.button("Confirm Choice"):
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.subheader("Step 2: Monty Reveals a Goat")
        initial_choice = st.session_state.initial_choice
        goat_doors = [i for i in range(3) if i != initial_choice and doors[i] == 'goat']
        st.session_state.revealed_door = random.choice(goat_doors)
        st.write(f"Monty opens Door {st.session_state.revealed_door + 1}, revealing a 🐐.")
        if st.button("Next"):
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        st.subheader("Step 3: Stick or Switch?")
        st.session_state.switch = st.radio("Do you want to switch doors?", ["Stick", "Switch"]) == "Switch"
        if st.button("Reveal Result"):
            st.session_state.step = 4
            st.rerun()

    elif st.session_state.step == 4:
        st.subheader("Result")
        switch = st.session_state.switch  # Retrieve the switch decision
        final_choice = (
            [i for i in range(3) if i != st.session_state.initial_choice and i != st.session_state.revealed_door][0]
            if switch else st.session_state.initial_choice
        )
        st.session_state.final_result = doors[final_choice]

        # Update history in session state
        if st.session_state.final_result == 'car':
            st.success("🎉 Congratulations! You won the car! 🚗")
            history["Switch Wins" if switch else "No Switch Wins"] += 1
        else:
            st.error("🐐 Sorry, you got a goat.")
            history["Switch Losses" if switch else "No Switch Losses"] += 1
            car_door = doors.index('car') + 1  # Find the door with the car
            st.write(f"The car was behind Door {car_door}.")

        st.write("**Game History:**")
        st.write(history)

        if st.button("Play Again"):
            # Reset the game state
            st.session_state.step = 1
            st.session_state.doors = initialize_game()
            st.session_state.initial_choice = None
            st.session_state.revealed_door = None
            st.session_state.final_result = None
            st.session_state.switch = None
            st.rerun()

# Auto Mode: Simulate Multiple Games
def auto_mode():
    st.title("Auto Mode: Simulate Multiple Games")
    num_games = st.slider("Number of games to simulate:", 1, 100000, 1000)
    switch_win_rate = simulate_games(num_games, switch=True)
    no_switch_win_rate = simulate_games(num_games, switch=False)
    st.metric("Win Rate (Switching)", f"{switch_win_rate:.2f}%")
    st.metric("Win Rate (Not Switching)", f"{no_switch_win_rate:.2f}%")
    
    with st.expander("Show Simulation Code (Python)"):
        st.code("""
def simulate_games(num_games, switch):
    wins = sum(monty_hall_game(random.randint(0, 2), switch) for _ in range(num_games))
    return (wins / num_games) * 100

def monty_hall_game(initial_choice, switch):
    doors = ['goat', 'goat', 'car']
    random.shuffle(doors)
    revealed_goat = random.choice([i for i in range(3) if i != initial_choice and doors[i] == 'goat'])
    final_choice = (
        [i for i in range(3) if i != initial_choice and i != revealed_goat][0]
        if switch else initial_choice
    )
    return doors[final_choice] == 'car'
""", language='python')
    st.image("https://www.advantexe.com/hubfs/digital-business-simulation.jpg", use_container_width=True)

# Simulation Function
def simulate_games(num_games, switch):
    wins = sum(monty_hall_game(random.randint(0, 2), switch) for _ in range(num_games))
    return (wins / num_games) * 100

# Monty Hall Game Logic
def monty_hall_game(initial_choice, switch):
    doors = ['goat', 'goat', 'car']
    random.shuffle(doors)
    revealed_goat = random.choice([i for i in range(3) if i != initial_choice and doors[i] == 'goat'])
    final_choice = (
        [i for i in range(3) if i != initial_choice and i != revealed_goat][0]
        if switch else initial_choice
    )
    return doors[final_choice] == 'car'

# Main App
def main():
    # Initialize history in session state
    if 'history' not in st.session_state:
        st.session_state.history = initialize_history()
    history = st.session_state.history

    if "music_paused" not in st.session_state:
        st.session_state["music_paused"] = False

    autoplay_audio("BackgroundMusic.mp3")

    st.sidebar.title("Monty Hall Simulator")
    mode = st.sidebar.radio("Select Mode", ["Home", "Auto", "Player"])
    if mode == "Home":
        home_page(history)
    elif mode == "Auto":
        auto_mode()
    elif mode == "Player":
        player_mode(history)

if __name__ == "__main__":
    main()



for i in range(5):
    st.write("")
# CSS for footer styling
footer_style = """
<style>
.footer {
    flex-shrink: 0;
    color: #999999;
    text-align: center;
    margin-top: 2em;
    font-size: 0.8em;
}
</style>
"""

# Add footer content
st.markdown(footer_style, unsafe_allow_html=True)
st.markdown('<div class="footer">The Monty Hall problem is a brain teaser based on the American television game show "Lets Make a Deal" and named after its original host, Monty Hall.</div>', unsafe_allow_html=True)
st.write("")
st.markdown('<div class="footer">A project by Kevin Chang</div>', unsafe_allow_html=True)