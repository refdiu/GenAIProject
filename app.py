
# app.py
import streamlit as st
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Import our project modules
from agents.agent_manager import AgentManager
from database.db_manager import DatabaseManager

# Initialize the managers
db_manager = DatabaseManager()
agent_manager = AgentManager()

# Set page config
st.set_page_config(
    page_title="Project Team Simulation",
    page_icon="🚀",
    layout="wide"
)

# App title and description
st.title("🚀 Project Team Simulation")
st.markdown("""
This application simulates an IT project team with multiple roles working on a software project.
You can provide business requirements and interact with the Project Manager to track progress.
""")

# Sidebar for inputs and controls
with st.sidebar:
    st.header("Project Controls")
    
    # Model selection
    model_option = st.selectbox(
        "Select LLM Model",
        ["facebook/opt-125m"],
        index=0
    )
    
    # Project phase selection
    st.subheader("Project Phases")
    
    run_all = st.button("Run Full Project Lifecycle")
    
    col1, col2 = st.columns(2)
    with col1:
        run_ba = st.button("1. Generate User Stories")
        run_dev = st.button("2. Develop Code")
    with col2:
        run_test = st.button("3. Create Test Cases")
        run_execute = st.button("4. Execute Tests")
    
    # Example requirements
    st.subheader("Example Requirements")
    if st.button("Load Example Requirements"):
        example_req = """
        Create a task management system with the following features:
        1. Users can create, view, update, and delete tasks
        2. Each task has a title, description, due date, priority, and status
        3. Users can filter tasks by status and priority
        4. Users can mark tasks as complete
        5. The system should send email reminders for upcoming tasks
        """
        st.session_state.business_requirements = example_req

# Initialize session state variables
if "business_requirements" not in st.session_state:
    st.session_state.business_requirements = ""
    
if "user_stories" not in st.session_state:
    st.session_state.user_stories = []
    
if "code_artifacts" not in st.session_state:
    st.session_state.code_artifacts = []
    
if "test_artifacts" not in st.session_state:
    st.session_state.test_artifacts = []
    
if "test_results" not in st.session_state:
    st.session_state.test_results = []
    
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Business Requirements Input
st.header("Business Requirements")
business_requirements = st.text_area(
    "Enter the business requirements for your project:",
    value=st.session_state.business_requirements,
    height=150
)

if business_requirements != st.session_state.business_requirements:
    st.session_state.business_requirements = business_requirements

# Run the project phases
if run_all or run_ba:
    if not st.session_state.business_requirements:
        st.error("Please enter business requirements first.")
    else:
        with st.spinner("Business Analyst is generating user stories..."):
            # Call the BA agent to generate user stories
            st.session_state.user_stories = agent_manager.process_business_requirements(
                st.session_state.business_requirements
            )
            st.success(f"Generated {len(st.session_state.user_stories)} user stories!")

if run_all or run_dev:
    if not st.session_state.user_stories:
        st.error("Please generate user stories first.")
    else:
        with st.spinner("Developer is writing code..."):
            # Call the Dev agent to generate code
            st.session_state.code_artifacts = agent_manager.develop_code(
                st.session_state.user_stories
            )
            st.success(f"Generated {len(st.session_state.code_artifacts)} code artifacts!")

if run_all or run_test:
    if not st.session_state.user_stories or not st.session_state.code_artifacts:
        st.error("Please generate user stories and code first.")
    else:
        with st.spinner("QA Tester is creating test cases..."):
            # Call the Test agent to generate test cases
            st.session_state.test_artifacts = agent_manager.create_test_cases(
                st.session_state.user_stories, 
                st.session_state.code_artifacts
            )
            st.success(f"Generated {len(st.session_state.test_artifacts)} test cases!")

if run_all or run_execute:
    if not st.session_state.code_artifacts or not st.session_state.test_artifacts:
        st.error("Please generate code and test cases first.")
    else:
        with st.spinner("QA Tester is executing tests..."):
            # Call the Test agent to execute tests
            st.session_state.test_results = agent_manager.execute_tests(
                st.session_state.code_artifacts, 
                st.session_state.test_artifacts
            )
            st.success(f"Executed {len(st.session_state.test_results)} tests!")

# Display project artifacts
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "User Stories", "Code", "Test Cases", "Test Results", "PM Chat"
])

with tab1:
    st.header("User Stories")
    if st.session_state.user_stories:
        for i, story in enumerate(st.session_state.user_stories):
            with st.expander(f"User Story {i+1}: {story.get('title', 'Untitled')}"):
                st.markdown(f"**Description:** {story.get('description', 'No description')}")
                st.markdown("**Acceptance Criteria:**")
                for criterion in story.get('acceptance_criteria', []):
                    st.markdown(f"- {criterion}")
                st.markdown(f"**Priority:** {story.get('priority', 'Medium')}")
    else:
        st.info("No user stories generated yet. Run the Business Analyst phase to generate user stories.")

with tab2:
    st.header("Code")
    if st.session_state.code_artifacts:
        for i, code in enumerate(st.session_state.code_artifacts):
            with st.expander(f"Code Artifact {i+1}"):
                st.code(code.get('content', ''), language="python")
    else:
        st.info("No code generated yet. Run the Developer phase to generate code.")

with tab3:
    st.header("Test Cases")
    if st.session_state.test_artifacts:
        for i, test in enumerate(st.session_state.test_artifacts):
            with st.expander(f"Test Case {i+1}"):
                st.code(test.get('content', ''), language="python")
    else:
        st.info("No test cases generated yet. Run the Tester phase to generate test cases.")

with tab4:
    st.header("Test Results")
    if st.session_state.test_results:
        # Summary stats
        pass_count = sum(1 for result in st.session_state.test_results if result.get('result') == 'PASS')
        fail_count = sum(1 for result in st.session_state.test_results if result.get('result') == 'FAIL')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tests", len(st.session_state.test_results))
        col2.metric("Passed", pass_count)
        col3.metric("Failed", fail_count)
        
        # Detailed results
        for i, result in enumerate(st.session_state.test_results):
            result_status = result.get('result', 'UNKNOWN')
            expander_title = f"Test {i+1}: {result.get('test_id', 'Unknown')} - {result_status}"
            
            if result_status == 'PASS':
                with st.expander(expander_title):
                    st.success(f"**Status:** {result_status}")
                    st.markdown(f"**Explanation:** {result.get('explanation', 'No explanation provided')}")
            elif result_status == 'FAIL':
                with st.expander(expander_title):
                    st.error(f"**Status:** {result_status}")
                    st.markdown(f"**Explanation:** {result.get('explanation', 'No explanation provided')}")
                    st.markdown(f"**Fix Suggestion:** {result.get('fix_suggestion', 'No suggestions provided')}")
            else:
                with st.expander(expander_title):
                    st.warning(f"**Status:** {result_status}")
                    st.markdown(f"**Explanation:** {result.get('explanation', 'No explanation provided')}")
    else:
        st.info("No test results generated yet. Run the Test Execution phase to generate results.")

with tab5:
    st.header("Project Manager Chat")
    st.markdown("""
    Ask the Project Manager about the status of your project. Example queries:
    - What user stories do we have?
    - Show me the code for the task creation feature
    - Are there any failing tests?
    - What's the overall project status?
    """)
    
    # Display chat history
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Project Manager:** {message['content']}")
    
    # Chat input
    pm_query = st.text_input("Ask the Project Manager:")
    
    if pm_query:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": pm_query
        })
        
        with st.spinner("Project Manager is responding..."):
            # Get response from PM agent
            response = agent_manager.get_project_status(pm_query)
            
            # Add PM response to history
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response
            })
        
        # Clear the input box
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("🚀 Project Team Simulation | Created with Streamlit, LangChain, and ChromaDB")