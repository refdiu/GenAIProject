# create_project.py
import streamlit as st
import json
import os
import uuid

def render_create_project():
    st.title("🛠️ Create a New Project")

    project_title = st.text_input("Project Title")
    team_members = st.text_area("Team Members (comma separated)")
    total_story_points = st.number_input("Total Story Points", min_value=0)
    deadline = st.date_input("Deadline")

    if st.button("Create Project"):
        if not project_title:
            st.error("Please enter a project title.")
            return

        project_data = {
            "id": str(uuid.uuid4()),
            "title": project_title,
            "team": [member.strip() for member in team_members.split(",") if member.strip()],
            "story_points": total_story_points,
            "deadline": str(deadline),
            "user_stories": [],
            "status": "Not Started"
        }

        os.makedirs("data", exist_ok=True)
        file_path = "data/projects.json"

        # Load existing data
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                projects = json.load(f)
        else:
            projects = []

        projects.append(project_data)

        with open(file_path, "w") as f:
            json.dump(projects, f, indent=2)

        st.success("🎉 Project created successfully!")
