# agents/agent_manager.py
from langchain.agents import Tool
from langchain.agents import AgentExecutor
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from crewai import Agent, Task, Crew

from .business_analyst import BusinessAnalystAgent
from .developer import DeveloperAgent
from .tester import TesterAgent
from .project_manager import ProjectManagerAgent
from database.db_manager import DatabaseManager



class AgentManager:
    def __init__(self):
        self.llm_model="facebook/opt-125m"
        self.llm = pipeline("text-generation", model=self.llm_model)
        self.db_manager = DatabaseManager()
        
        # Initialize agents
        self.ba_agent = BusinessAnalystAgent(self.llm, self.db_manager)
        self.dev_agent = DeveloperAgent(self.llm, self.db_manager)
        self.test_agent = TesterAgent(self.llm, self.db_manager)
        self.pm_agent = ProjectManagerAgent(self.llm_model, self.db_manager)
        
    def process_business_requirements(self, requirements):
        """Process initial business requirements and generate user stories"""
        return self.ba_agent.generate_user_stories(requirements)
    
    def develop_code(self, user_stories):
        """Develop code based on user stories"""
        return self.dev_agent.generate_code(user_stories)
    
    def create_test_cases(self, user_stories, code):
        """Create test cases based on user stories and code"""
        return self.test_agent.generate_test_cases(user_stories, code)
    
    def execute_tests(self, code, test_cases):
        """Execute tests against the code"""
        return self.test_agent.execute_tests(code, test_cases)
    
    def get_project_status(self, query):
        """Get project status based on PM query"""
        return self.pm_agent.get_status(query)
    
    def setup_crew(self):
        """Set up CrewAI crew for sequential execution"""
        # Define CrewAI agents
        ba = Agent(
            role="Business Analyst",
            goal="Create clear and concise user stories from business requirements",
            backstory="Experienced in translating business needs into technical requirements",
            verbose=True,
            llm=self.llm
        )
        
        developer = Agent(
            role="Developer",
            goal="Write high-quality code that meets user story requirements",
            backstory="Expert programmer who values clean, efficient code",
            verbose=True,
            llm=self.llm
        )
        
        tester = Agent(
            role="QA Tester",
            goal="Ensure the code works as expected through thorough testing",
            backstory="Detail-oriented tester with a knack for finding edge cases",
            verbose=True,
            llm=self.llm
        )
        
        # Define tasks
        task1 = Task(
            description="Generate user stories from the business requirements",
            agent=ba,
            expected_output="A list of well-defined user stories"
        )
        
        task2 = Task(
            description="Develop code based on the user stories",
            agent=developer,
            expected_output="Working code that implements the user stories",
            context=[task1]
        )
        
        task3 = Task(
            description="Create and execute test cases for the developed code",
            agent=tester,
            expected_output="Test results showing code functionality",
            context=[task1, task2]
        )
        
        # Create the crew
        crew = Crew(
            agents=[ba, developer, tester],
            tasks=[task1, task2, task3],
            verbose=2
        )
        
        return crew
    
    def run_full_project(self, business_requirements):
        """Run the entire project lifecycle"""
        crew = self.setup_crew()
        result = crew.kickoff(inputs={"business_requirements": business_requirements})
        return result