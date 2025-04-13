# app.py
import streamlit as st
import json
import os
from dotenv import load_dotenv
import time
import ast
import inspect
# from another import a

import sys
sys.path.append('C:/Users/basad/Downloads/PROJECT/COLLEGE_PROJECT/demo')

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
        "Select Ollama Model",
        # ["llama3", "codellama", "llama2"],
        ["codellama:7b"],
        index=0,
        help="Select which Ollama model to use for the agents"
    )
    
    # Display model information
    st.info(f"""
    Using Ollama models:
    - Business Analyst: {model_option}
    - Developer: codellama (recommended for code)
    - QA Tester: codellama (recommended for tests)
    - Project Manager: {model_option}
    """)
    
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

# Status indicator for Ollama connection
ollama_status_container = st.empty()
try:
    # Update the agent_manager with the selected model
    agent_manager.llm_model = model_option
    agent_manager.llm = agent_manager.llm.__class__(
        model=model_option,
        base_url="http://localhost:11434"
    )
    ollama_status_container.success("✅ Connected to Ollama service")
except Exception as e:
    ollama_status_container.error(f"❌ Could not connect to Ollama service: {str(e)}")
    st.info("""
    To use this application, you need to have Ollama installed and running.
    Visit https://ollama.com/ to download and install Ollama.
    
    Make sure to run the following commands to get the required models:
    ```
    ollama pull llama3
    ollama pull codellama
    ```
    """)

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
            # Add a progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing Business Analyst agent...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text("Processing requirements...")
            progress_bar.progress(30)
            
            # Call the BA agent to generate user stories
            st.session_state.user_stories = agent_manager.process_business_requirements(
                st.session_state.business_requirements
            )
            
            progress_bar.progress(90)
            status_text.text("Finalizing user stories...")
            time.sleep(0.5)
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"Generated {len(st.session_state.user_stories)} user stories!")

if run_all or run_dev:
    if not st.session_state.user_stories:
        st.error("Please generate user stories first.")
    else:
        with st.spinner("Developer is writing code..."):
            # Add a progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing Developer agent...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text("Analyzing user stories...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.text("Writing code...")
            progress_bar.progress(50)
            
            # Call the Dev agent to generate code
            st.session_state.code_artifacts = agent_manager.develop_code(
                st.session_state.user_stories
            )
            
            progress_bar.progress(90)
            status_text.text("Optimizing code...")
            time.sleep(0.5)
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"Generated {len(st.session_state.code_artifacts)} code artifacts!")

if run_all or run_test:
    if not st.session_state.user_stories or not st.session_state.code_artifacts:
        st.error("Please generate user stories and code first.")
    else:
        with st.spinner("QA Tester is creating test cases..."):
            # Add a progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing QA Tester agent...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text("Analyzing code and requirements...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.text("Designing test cases...")
            progress_bar.progress(50)
            
            # Call the Test agent to generate test cases
            st.session_state.test_artifacts = agent_manager.create_test_cases(
                st.session_state.user_stories, 
                st.session_state.code_artifacts
            )
            
            progress_bar.progress(90)
            status_text.text("Finalizing test cases...")
            time.sleep(0.5)
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"Generated {len(st.session_state.test_artifacts)} test cases!")

if run_all or run_execute:
    if not st.session_state.code_artifacts or not st.session_state.test_artifacts:
        st.error("Please generate code and test cases first.")
    else:
        with st.spinner("QA Tester is executing tests..."):
            # Add a progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing test execution...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text("Setting up test environment...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.text("Running tests...")
            progress_bar.progress(50)
            
            # Call the Test agent to execute tests
            st.session_state.test_results = agent_manager.execute_tests(
                st.session_state.code_artifacts, 
                st.session_state.test_artifacts
            )
            
            progress_bar.progress(80)
            status_text.text("Analyzing test results...")
            time.sleep(0.5)
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            
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
                for criterion in story.get('acceptanceCriteria', []):
                    st.markdown(f"- {criterion}")
                st.markdown(f"**Priority:** {story.get('priority', 'Medium')}")
    else:
        st.info("No user stories generated yet. Run the Business Analyst phase to generate user stories.")

with tab2:
    # st.header("Code")
    
    # if st.session_state.code_artifacts:
    #     for i, code in enumerate(st.session_state.code_artifacts):
    #         with st.expander(f"Code Artifact {i+1}"):
    #             st.code(code.get('content', ''), language="python")
    # else:
    #     st.info("No code generated yet. Run the Developer phase to generate code.")
    

# Initialize session state if not already initialized
    if 'code_artifacts' not in st.session_state:
        st.session_state.code_artifacts = []
    
    # Creating tab layout (assuming you are using st.beta_expander or tab structure for tab2)
    with st.expander("Code", expanded=True):  # or use st.tab('Code') depending on your tab layout
        st.header("Code")
        
        # File uploader widget for user to upload their Python or Text file
        uploaded_file = st.file_uploader("Choose a Python or Text file", type=["py", "txt"])
    
        if uploaded_file is not None:
            # Read the file content
            code_content = uploaded_file.read().decode("utf-8")
            
            # Display the code content in the app
            st.code(code_content, language='python')  # 'python' for .py files, change for other languages
        else:
            st.write("Please upload a Python or Text file.")
        
        # Check if code artifacts exist in session state
        if st.session_state.code_artifacts:
            for i, code in enumerate(st.session_state.code_artifacts):
                with st.expander(f"Code Artifact {i+1}"):
                    st.code(code.get('content', ''), language="python")
        else:
            st.info("No code generated yet. Run the Developer phase to generate code.")


# with tab3:
#     st.header("Test Cases")
#     if st.session_state.test_artifacts:
#         for i, test in enumerate(st.session_state.test_artifacts):
#             with st.expander(f"Test Case {i+1}"):
#                 st.code(test.get('content', ''), language="python")
#     else:
#         st.info("No test cases generated yet. Run the Tester phase to generate test cases.")


# # Initialize session state if not already initialized
# if 'code_artifacts' not in st.session_state:
#     st.session_state.code_artifacts = []

# Function to generate test cases
with tab3:

    def generate_test_cases(code):
        try:
            # Parse the Python code into an AST (Abstract Syntax Tree)
            tree = ast.parse(code)
            
            test_cases = []
            
            # Loop through all nodes in the AST and find function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function name and arguments
                    function_name = node.name
                    args = [arg.arg for arg in node.args.args]
                    
                    # Generate basic test case for the function
                    test_case = f"""
    def test_{function_name}():
        # Test function {function_name} with sample arguments
        result = {function_name}({', '.join(['None' for _ in args])})
        assert result is not None  # Example check, adjust according to function's behavior
                    """
                    test_cases.append(test_case)
            
            return test_cases
    
        except Exception as e:
            st.error(f"Error generating test cases: {str(e)}")
            return []
    
    # File uploader widget for user to upload their Python or Text file
    uploaded_file = st.file_uploader("Choose a Python file to generate test cases", type=["py"])
    
    if uploaded_file is not None:
        # Read the file content
        code_content = uploaded_file.read().decode("utf-8")
        
        # Display the code content in the app
        st.code(code_content, language='python')
        
        # Generate test cases from the code
        test_cases = generate_test_cases(code_content)
        
        if test_cases:
            st.subheader("Generated Test Cases")
            for test_case in test_cases:
                st.code(test_case, language='python')
        else:
            st.write("No test cases generated.")
    else:
        st.write("Please upload a Python file to generate test cases.")

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
    st.header("PM Chat")
    st.markdown("""
    Ask the Project Manager about the status of your project. Example queries:
    - What user stories do we have?
    - Show me the code for the task creation feature
    - Are there any failing tests?
    - What's the overall project status?
    """)
    
    # Display chat history
    # chat_container = st.container()
    # with chat_container:
    #     for message in st.session_state.conversation_history:
    #         if message["role"] == "user":
    #             st.markdown(f"**You:** {message['content']}")
    #         else:
    #             st.markdown(f"**Project Manager:** {message['content']}")
    
    # Chat input
    # # Check if the conversation history exists, if not, initialize it
    # if 'conversation_history' not in st.session_state:
    #     st.session_state.conversation_history = []
    
    # # Check if the query has already been processed
    # if 'processed_query' not in st.session_state:
    #     st.session_state.processed_query = False
    
    # Chat input
    # Initialize session state if needed
    if 'processed_query' not in st.session_state:
        st.session_state.processed_query = False
    
    # Input and logic for first or subsequent queries
    if not st.session_state.processed_query:
        pm_query = st.text_input("Ask the Project Manager:", key="pm_query")
    
        if pm_query:
            with st.spinner("Project Manager is thinking..."):
                response = agent_manager.get_project_status(pm_query)
    
            st.markdown(f"**🧑 You:** {pm_query}**")
            st.markdown(f"**🤖 Assistant:** {response}**")
    
            st.session_state.processed_query = True
    else:
        # Reset input, and capture the new query
        new_query = st.text_input("Ask the Project Manager:", key="pm_query_reset")
    
        if new_query:
            with st.spinner("Project Manager is thinking..."):
                response = agent_manager.get_project_status(new_query)
    
            st.markdown(f"**🧑 You:** {new_query}**")
            st.markdown(f"**🤖 Assistant:** {response}**")
    
            # Reset the cycle for next input
            st.session_state.processed_query = False
    
        

    
# Ollama status monitor
st.sidebar.markdown("---")
with st.sidebar.expander("Ollama Status"):
    if st.button("Check Ollama Connection"):
        try:
            # Try to call a simple prompt to check if Ollama is responding
            from langchain_community.llms import Ollama
            test_ollama = Ollama(model=model_option, base_url="http://localhost:11434")
            result = test_ollama.invoke("Hello")
            st.success(f"✅ Connected to Ollama service\nModel: {model_option}\nResponse: {result[:50]}...")
        except Exception as e:
            st.error(f"❌ Could not connect to Ollama service: {str(e)}")
            st.info("Make sure Ollama is running and the models are installed.")
    
    st.markdown("""
    ### Ollama Commands
    ```bash
    # Start Ollama server (if not running)
    ollama serve
    
    # Pull models
    ollama pull llama3
    ollama pull codellama
    
    # List installed models
    ollama list
    ```
    """)

# Footer
st.markdown("---")
st.markdown("🚀 Project Team Simulation | Powered by Ollama, Streamlit, and ChromaDB")
