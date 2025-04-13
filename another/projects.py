# # projects.py
# import streamlit as st
# import json
# import os
# from datetime import datetime

# def render_projects():
#     st.title("📊 Project Dashboard")

#     file_path = "data/projects.json"
#     if not os.path.exists(file_path):
#         st.info("No projects found. Go create one first!")
#         return

#     with open(file_path, "r") as f:
#         projects = json.load(f)

#     for i, project in enumerate(projects):
#         with st.expander(f"🔧 {project['title']}"):
#             st.write("👥 Team:", ", ".join(project["team"]))
#             st.write("🗓️ Deadline:", project["deadline"])
#             st.write("💎 Story Points:", project["story_points"])
#             st.write("🚦 Status:", project["status"])
            
#             # Progress bar
#             completed = sum(1 for s in project["user_stories"] if s.get("status") == "Done")
#             total = len(project["user_stories"]) or 1  # avoid division by zero
#             st.progress(completed / total)

#             # List user stories
#             st.subheader("📜 User Stories")
#             if not project["user_stories"]:
#                 st.write("No user stories yet.")
#             else:
#                 for us in project["user_stories"]:
#                     st.write(f"- **{us['title']}** ({us['status']})")

#             # Remaining days
#             try:
#                 deadline = datetime.strptime(project["deadline"], "%Y-%m-%d")
#                 remaining = (deadline - datetime.today()).days
#                 st.info(f"⏳ {remaining} days remaining")
#             except Exception as e:
#                 st.warning("❌ Couldn't parse deadline date.")

import streamlit as st
import json
import os
from datetime import datetime

def render_projects():
    st.title("📊 Project Dashboard")

    project_path = "data/projects.json"
    ticket_path = "data/tickets.json"

    if not os.path.exists(project_path):
        st.info("No projects found. Go create one first!")
        return

    # Load projects
    with open(project_path, "r") as f:
        projects = json.load(f)

    # Load tickets (if exists)
    tickets = []
    if os.path.exists(ticket_path):
        with open(ticket_path, "r") as f:
            tickets = json.load(f)

    for i, project in enumerate(projects):
        project_id = project["id"]
        
        # Filter tickets for this project
        project_tickets = [t for t in tickets if t.get("project_id") == project_id]

        with st.expander(f"🔧 {project['title']}"):
            st.write("👥 Team:", ", ".join(project["team"]))
            st.write("🗓️ Deadline:", project["deadline"])
            st.write("💎 Story Points:", project["story_points"])
            st.write("🚦 Status:", project["status"])

            # Progress bar from ticket status
            done = sum(1 for t in project_tickets if t.get("status") == "Done")
            total = len(project_tickets) or 1
            st.progress(done / total)

            # if not project_tickets:
            #     st.write("No user stories yet.")
            # else:
            #     for t in project_tickets:
            #         st.write(f"- **{t['title']}** ({t['status']})")
            st.subheader("📜 User Stories")
            if not project.get("user_stories"):
                st.write("No user stories found in the project.")
            else:
                for i, story in enumerate(project["user_stories"], 1):
                    st.markdown(f"**📌 Story {i}:**  \n{story.replace(chr(10), '  \n')}")
                    st.markdown("---")
            
            # Remaining days
            try:
                deadline = datetime.strptime(project["deadline"], "%Y-%m-%d")
                remaining = (deadline - datetime.today()).days
                st.info(f"⏳ {remaining} days remaining")
            except:
                st.warning("❌ Couldn't parse deadline.")
