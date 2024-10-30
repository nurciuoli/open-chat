import streamlit as st
import streamlit.components.v1 as components


def show_home():
    
    # HTML and CSS code for the animated clock with enhanced styling and the dark-mode calendar
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body {{ font-family: Arial, sans-serif; background-color: {st.config.get_option("theme.backgroundColor")}; color: {st.config.get_option("theme.textColor")}; }}
    .clock-container {{ display: flex; justify-content: center; align-items: center; margin-bottom: 10px; }}
    .clock {{
        font-size: 36px;
        font-weight: bold;
        color: {st.config.get_option("theme.primaryColor")};
        text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.2);
        animation: pulse 1s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.005); }}
        100% {{ transform: scale(1); }}
    }}
    .calendar {{ display: flex; flex-direction: column; align-items: center; color: {st.config.get_option("theme.textColor")}; }}
    .month {{ font-size: 20px; font-weight: bold; color: {st.config.get_option("theme.primaryColor")}; }}
    .days {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }}
    .day {{ width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: {st.config.get_option("theme.textColor")}; background-color: {st.config.get_option("theme.secondaryBackgroundColor")}; border-radius: 5px; }}
    .day:hover {{ background-color: #44475a; }}
    .today {{ background-color: {st.config.get_option("theme.primaryColor")}; color: {st.config.get_option("theme.backgroundColor")}; border-radius: 5px; }}
    .day-label {{ font-weight: bold; color: {st.config.get_option("theme.primaryColor")}; }}
    </style>
    </head>
    <body>
    
    <!-- Centered and styled animated clock -->
    <div class="clock-container">
        <div class="clock" id="clock">Loading time...</div>
    </div>
    
    <!-- Calendar -->
    <div class="calendar">
        <div class="month" id="month-year"></div>
        <div class="days" id="calendar-days">
            <div class="day-label">Sun</div><div class="day-label">Mon</div><div class="day-label">Tue</div><div class="day-label">Wed</div><div class="day-label">Thu</div><div class="day-label">Fri</div><div class="day-label">Sat</div>
        </div>
    </div>
    
    <script>
    // Function for animated clock
    function updateClock() {{
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').textContent = hours + ":" + minutes + ":" + seconds;
    }}
    setInterval(updateClock, 1000); // Update every second
    
    // Function to create calendar
    function createCalendar() {{
        const now = new Date();
        const monthNames = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"];
        const month = now.getMonth();
        const year = now.getFullYear();
        const firstDay = new Date(year, month, 1).getDay();
        const lastDate = new Date(year, month + 1, 0).getDate();
        
        document.getElementById("month-year").textContent = monthNames[month] + " " + year;
        
        const calendarDays = document.getElementById("calendar-days");
        
        // Clear previous days
        calendarDays.innerHTML = '<div class="day-label">Sun</div><div class="day-label">Mon</div><div class="day-label">Tue</div><div class="day-label">Wed</div><div class="day-label">Thu</div><div class="day-label">Fri</div><div class="day-label">Sat</div>';
        
        // Add blank days until the first day of the month
        for (let i = 0; i < firstDay; i++) {{
            const blank = document.createElement("div");
            blank.className = "day";
            calendarDays.appendChild(blank);
        }}
        
        // Add the days of the current month
        for (let i = 1; i <= lastDate; i++) {{
            const day = document.createElement("div");
            day.className = "day";
            day.textContent = i;
            
            // Highlight today's date
            if (i === now.getDate()) {{
                day.classList.add("today");
            }}
            
            day.addEventListener("click", () => {{
                alert("You selected day " + i);
            }});
            calendarDays.appendChild(day);
        }}
    }}
    createCalendar();
    </script>
    </body>
    </html>
    """
    
    # Display the HTML in Streamlit with reduced space
    components.html(html_code, height=350)

    # To-Do List Section
    st.header("To-Do List")

    # Initialize a session state for storing to-do items
    if "todo_items" not in st.session_state:
        st.session_state.todo_items = []

    # Input box to add new items
    new_task = st.text_input("Add a new task:", "")

    # Button to add the task
    if st.button("Add Task"):
        if new_task:
            st.session_state.todo_items.append(new_task)
            st.success(f"Added: {new_task}")
        else:
            st.warning("Please enter a task.")
        
    # Display the list of tasks with checkboxes
    for i, task in enumerate(st.session_state.todo_items):
        if st.checkbox(task, key=f"task_{i}"):
            # Remove task from the list if checked
            st.session_state.todo_items.pop(i)
            st.rerun()  # Rerun to update the list immediately

    # Add the Scratch Notes with reduced space above it
    st.text_area(label='Scratch Notes', height=150)
