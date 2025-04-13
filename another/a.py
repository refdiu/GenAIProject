import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import pandas as pd
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import requests
from create_project import render_create_project
from projects import render_projects
import os
import json
from pm_chatbot import render_pm_chatbot
# Load model and tokenizer
@st.cache_resource
def load_model():
    model_name = "Salesforce/codegen-350M-mono"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

code_gen = load_model()

# Initialize session state for storing tickets
if "tickets" not in st.session_state:
    try:
        with open("data/tickets.json", "r") as f:
            st.session_state.tickets = json.load(f)
    except FileNotFoundError:
        st.session_state.tickets = []

if 'ticket_id_counter' not in st.session_state:
    st.session_state.ticket_id_counter = 1

st.title("🧠 Agile Project Management Board")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create Project","Show Projects","Backlog", "Board", "Code Generator", "Reports", "PM Chatbot"])

if page == "Create Project":
    render_create_project()
elif page == "Show Projects":
    render_projects()
elif page=="PM Chatbot":
    render_pm_chatbot()
# Function definitions
def create_ticket(summary, description, priority, assignee, story_points):
    ticket_id = f"PROJ-{st.session_state.ticket_id_counter}"
    st.session_state.ticket_id_counter += 1

    created_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d")

    ticket = {
        "id": ticket_id,
        "summary": summary,
        "description": description,
        "status": "To Do",
        "priority": priority,
        "assignee": assignee,
        "reporter": "Current User",
        "created": created_date,
        "due": due_date,
        "story_points": story_points,
        "comments": []
    }

    st.session_state.tickets.append(ticket)
    # ✅ Save to file
    os.makedirs("data", exist_ok=True)
    with open("data/tickets.json", "w") as f:
        json.dump(st.session_state.tickets, f, indent=2)

    return ticket_id

# def generate_user_stories(reqs):
#     stories = []
#     for req in reqs:
#         story = f"As a user, I want to {req.lower()} so that I can accomplish my goal.\n"
#         story += "Acceptance Criteria:\n- Should be easy to use\n- Should be functional and responsive"
#         stories.append(story)
#     return stories
# Function definition (leave this as-is)
def generate_user_stories(reqs, project_id):
    # 1. Generate the user stories
    stories = []
    for req in reqs:
        story = f"As a user, I want to {req.lower()} so that I can accomplish my goal."
        story += "\nAcceptance Criteria:\n- Should be easy to use\n- Should be functional and responsive"
        stories.append(story)

    # 2. Load existing projects
    project_path = "data/projects.json"
    if not os.path.exists(project_path):
        print("Project file not found.")
        return

    with open(project_path, "r") as f:
        projects = json.load(f)

    # 3. Find the project by ID and update its user_stories
    for project in projects:
        if project["id"] == project_id:
            project["user_stories"] = stories
            break
    else:
        print("Project not found.")
        return

    # 4. Save the updated project list
    with open(project_path, "w") as f:
        json.dump(projects, f, indent=2)

    print(f"✅ User stories saved to project {project_id}")
    return stories


def smart_code_generation(user_story):
    prompt = f"Write a Python function based on the following user story:\n\n{user_story}\n\n# Python Code:\n"
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "codellama:7b",
        "prompt": prompt,
        "stream": False  # stream=True can be handled differently
    })

    try:
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        else:
            return f"❌ Error: Unexpected response format: {data}"
    except Exception as e:
        return f"❌ Exception while parsing Ollama response: {str(e)}"


# def generate_test_cases(user_story):
#     prompt = f"Write test cases in Python for the following user story:\n\n{user_story}\n\n# Test Cases:\n"
#     result = code_gen(prompt, max_new_tokens=200, do_sample=True, temperature=0.7)[0]['generated_text']
#     return result.split("# Test Cases:")[-1].strip()
def generate_test_cases(user_story):
    prompt = f"Write Python test cases for the following user story:\n\n{user_story}\n\n# Test Cases:\n"
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "codellama:7b",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"].strip()

# BACKLOG PAGE (same as you had before, omitted here for brevity)
if page == "Backlog":
    st.header("📝 Product Backlog")
    
    with st.expander("➕ Create New Issue", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            summary = st.text_input("Summary")
            description = st.text_area("Description")
            assignee = st.selectbox("Assignee", ["Unassigned", "John", "Sarah", "Mike", "Emma"])
        
        with col2:
            issue_type = st.selectbox("Issue Type", ["Story", "Task", "Bug", "Epic"])
            priority = st.selectbox("Priority", ["Highest", "High", "Medium", "Low", "Lowest"])
            story_points = st.number_input("Story Points", min_value=1, max_value=13, value=3)
        
        if st.button("Create Issue"):
            if summary and description:
                ticket_id = create_ticket(summary, description, priority, assignee, story_points)
                st.success(f"Created issue {ticket_id}")
            else:
                st.error("Summary and description are required")
        # Requirements to User Stories converter

    # with st.expander("🔄 Convert Requirements to User Stories", expanded=False):
    #     requirements_input = st.text_area("Requirements (comma-separated)", 
    #                                       "create tasks, view tasks, update tasks, delete tasks, download reports as PDF")
        
    #     generate = st.button("Generate Stories")
    
    # if generate:
    #     requirements = [r.strip() for r in requirements_input.split(',') if r.strip()]
    #     user_stories = generate_user_stories(requirements)
        
    #     for idx, story in enumerate(user_stories):
    #         with st.expander(f"📌 Story: {requirements[idx]}", expanded=True):
    #             st.text_area(f"User Story {idx+1}", story, height=150, key=f"story_{idx}")
                
    #             cols = st.columns(4)
    #             with cols[0]:
    #                 if st.button("Add to Backlog", key=f"add_{idx}"):
    #                     create_ticket(
    #                         f"User can {requirements[idx]}", 
    #                         story, 
    #                         "Medium", 
    #                         "Unassigned", 
    #                         3
    #                     )
    #                     st.success("Added to backlog!")
    project_path = "data/projects.json"
    with open(project_path, "r") as f:
        projects = json.load(f)
    
    # Step 1: Select Project
    project_titles = [f"{p['title']} ({p['id']})" for p in projects]
    project_ids = [p["id"] for p in projects]
    selected = st.selectbox("🎯 Select Project", project_titles)
    selected_project_id = project_ids[project_titles.index(selected)]
    
    with st.expander("🔄 Convert Requirements to User Stories", expanded=False):
        requirements_input = st.text_area("Requirements (comma-separated)", 
                                          "create tasks, view tasks, update tasks, delete tasks, download reports as PDF")
        
        generate = st.button("Generate Stories")
    
    if generate:
        requirements = [r.strip() for r in requirements_input.split(',') if r.strip()]
        
        # 🔥 Generate and SAVE user stories to selected project
        user_stories = generate_user_stories(requirements, selected_project_id)
    
        for idx, story in enumerate(user_stories):
            with st.expander(f"📌 Story: {requirements[idx]}", expanded=True):
                st.text_area(f"User Story {idx+1}", story, height=150, key=f"story_{idx}")
                
                cols = st.columns(4)
                with cols[0]:
                    if st.button("Add to Backlog", key=f"add_{idx}"):
                        # 🛠️ Update your create_ticket function to accept project_id
                        create_ticket(
                            f"User can {requirements[idx]}", 
                            story, 
                            "Medium", 
                            "Unassigned", 
                            3,
                            selected_project_id  # <-- Pass it here
                        )
                        st.success("Added to backlog! 💼")

    
    # Display backlog
    st.subheader("Current Backlog")
    if st.session_state.tickets:
        tickets_df = pd.DataFrame(st.session_state.tickets)
        st.dataframe(
            tickets_df[["id", "summary", "status", "priority", "assignee", "story_points"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No items in the backlog yet. Create some issues or generate from requirements.")

# BOARD PAGE (same as before, omitted)
elif page == "Board":
    st.header("📊 Agile Board")
    
    # Create columns for different statuses
    col1, col2, col3, col4 = st.columns(4)
    
    # Define the statuses
    statuses = {
        "To Do": col1,
        "In Progress": col2,
        "Review": col3,
        "Done": col4
    }
    
    # Display column headers
    for status, col in statuses.items():
        with col:
            st.subheader(status)
    
    # Organize tickets by status
    status_tickets = {status: [] for status in statuses}
    for ticket in st.session_state.tickets:
        status = ticket["status"]
        if status in status_tickets:
            status_tickets[status].append(ticket)
    
    # Display tickets in columns
    for status, tickets in status_tickets.items():
        with statuses[status]:
            for ticket in tickets:
                with st.container():
                    st.markdown(f"""
                    <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;'>
                        <strong>{ticket['id']}</strong>: {ticket['summary']}<br>
                        🔢 {ticket['story_points']} | 👤 {ticket['assignee']} | 🚨 {ticket['priority']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add buttons for status transitions
                    cols = st.columns(3)
                    if status != "Done":
                        next_status = {"To Do": "In Progress", "In Progress": "Review", "Review": "Done"}[status]
                        if cols[0].button(f"Move to {next_status}", key=f"move_{ticket['id']}"):
                            ticket["status"] = next_status
                            st.rerun()
                    
                    if cols[1].button("Edit", key=f"edit_{ticket['id']}"):
                        st.session_state.edit_ticket = ticket
                        st.rerun()
                    
                    if cols[2].button("Delete", key=f"delete_{ticket['id']}"):
                        st.session_state.tickets.remove(ticket)
                        with open("data/tickets.json", "w") as f:
                            json.dump(st.session_state.tickets, f, indent=2)
                        st.rerun()
    
    # Edit ticket modal (using expander as modal)
    if 'edit_ticket' in st.session_state and st.session_state.edit_ticket:
        with st.sidebar.expander("Edit Ticket", expanded=True):
            ticket = st.session_state.edit_ticket
            summary = st.text_input("Summary", ticket["summary"])
            description = st.text_area("Description", ticket["description"])
            status = st.selectbox("Status", list(statuses.keys()), index=list(statuses.keys()).index(ticket["status"]))
            priority = st.selectbox("Priority", ["Highest", "High", "Medium", "Low", "Lowest"], 
                                   index=["Highest", "High", "Medium", "Low", "Lowest"].index(ticket["priority"]))
            assignee = st.selectbox("Assignee", ["Unassigned", "John", "Sarah", "Mike", "Emma"],
                                   index=["Unassigned", "John", "Sarah", "Mike", "Emma"].index(ticket["assignee"]) 
                                   if ticket["assignee"] in ["Unassigned", "John", "Sarah", "Mike", "Emma"] else 0)
            story_points = st.number_input("Story Points", min_value=1, max_value=13, value=ticket["story_points"])
            
            if st.button("Save Changes"):
                ticket["summary"] = summary
                ticket["description"] = description
                ticket["status"] = status
                ticket["priority"] = priority
                ticket["assignee"] = assignee
                ticket["story_points"] = story_points
                with open("data/tickets.json", "w") as f:
                    json.dump(st.session_state.tickets, f, indent=2)
                del st.session_state.edit_ticket
                st.rerun()
            
            if st.button("Cancel"):
                del st.session_state.edit_ticket
                st.rerun()

# Code Generator page                
elif page == "Code Generator":
    st.header("💻 Code Generator")
    
    # Select a user story to generate code for
    if st.session_state.tickets:
        ticket_options = {f"{t['id']}: {t['summary']}": t for t in st.session_state.tickets}
        selected_ticket_str = st.selectbox("Select a ticket to generate code for", list(ticket_options.keys()))
        selected_ticket = ticket_options[selected_ticket_str]
        
        st.subheader("User Story")
        st.code(selected_ticket["description"], language="markdown")
        
        import streamlit as st

        # Assume `selected_ticket` is already defined elsewhere in the app
        if selected_ticket:
            # Row 1: Generated Code
            st.subheader("Generated Code")
            if st.button("Generate Code"):
                with st.spinner("Generating code..."):
                    code = smart_code_generation(selected_ticket["description"])
                    st.code(code, language="python")
            
            # Row 2: Test Cases
            st.subheader("Test Cases")
            if st.button("Generate Tests"):
                with st.spinner("Generating tests..."):
                    tests = generate_test_cases(selected_ticket["description"])
                    st.code(tests, language="python")
        
        else:
            st.info("No tickets available. Create some tickets in the Backlog first.")


# CODE GENERATOR PAGE (same as before, omitted)

# REPORTS PAGE
if page == "Reports":
    st.header("📈 Project Reports")

    if st.session_state.tickets:
        total_tickets = len(st.session_state.tickets)
        status_counts = {}
        done_points = 0
        total_points = 0

        for ticket in st.session_state.tickets:
            status = ticket["status"]
            points = ticket["story_points"]
            total_points += points
            if status == "Done":
                done_points += points
            status_counts[status] = status_counts.get(status, 0) + 1

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tickets", total_tickets)
        col2.metric("In Progress", status_counts.get("In Progress", 0))
        col3.metric("Done", status_counts.get("Done", 0))

        st.subheader("📉 Burndown Chart (Simulated)")
        days = [f"Day {i}" for i in range(1, 11)]
        ideal_burndown = [total_points - i * (total_points / 9) for i in range(10)]
        actual_burndown = [total_points - random.randint(0, total_points) * (i / 9) for i in range(10)]

        chart_data = pd.DataFrame({
            "Day": days,
            "Ideal": ideal_burndown,
            "Actual": actual_burndown
        })

        fig, ax = plt.subplots()
        ax.plot(chart_data["Day"], chart_data["Ideal"], label="Ideal", linestyle="--", marker="o")
        ax.plot(chart_data["Day"], chart_data["Actual"], label="Actual", linestyle="-", marker="o")
        ax.set_xlabel("Day")
        ax.set_ylabel("Story Points Remaining")
        ax.set_title("Burndown Chart")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)
    else:
        st.info("No data available yet. Please create tickets first.")
