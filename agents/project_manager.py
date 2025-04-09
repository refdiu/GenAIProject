# # agents/project_manager.py
# from langchain.prompts import PromptTemplate
# from langchain.agents import Tool
# from langchain.agents import AgentExecutor
# from langchain.agents.format_scratchpad import format_to_openai_function_messages
# from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
# from langchain_core.output_parsers import StrOutputParser
# import json

# class ProjectManagerAgent:
#     def __init__(self, llm, db_manager):
#         self.llm = llm
#         self.db_manager = db_manager
        
#     def get_status(self, query):
#         """Get project status based on PM query"""
#         # Define tools for the PM agent to use
#         tools = [
#             Tool(
#                 name="retrieve_user_stories",
#                 func=self._retrieve_user_stories,
#                 description="Retrieve user stories from the project repository"
#             ),
#             Tool(
#                 name="retrieve_code",
#                 func=self._retrieve_code,
#                 description="Retrieve code artifacts from the project repository"
#             ),
#             Tool(
#                 name="retrieve_test_cases",
#                 func=self._retrieve_test_cases,
#                 description="Retrieve test cases from the project repository"
#             ),
#             Tool(
#                 name="retrieve_test_results",
#                 func=self._retrieve_test_results,
#                 description="Retrieve test execution results from the project repository"
#             ),
#             Tool(
#                 name="search_artifacts",
#                 func=self._search_artifacts,
#                 description="Search through all project artifacts based on query"
#             )
#         ]
        
#         # Create the PM agent
#         prompt = PromptTemplate(
#             template="""
#             You are a Project Manager overseeing a software development project. Your team consists of 
#             Business Analysts, Developers, and QA Testers. 
            
#             Your task is to provide status updates and answer questions about the project artifacts and progress.
            
#             Query: {query}
            
#             Use the tools available to you to retrieve information from the project repository and provide 
#             a comprehensive response to the query.
            
#             Make sure to:
#             1. Be precise in your response
#             2. Only provide information that is relevant to the query
#             3. If relevant information is not available, acknowledge this and explain what is missing
            
#             {agent_scratchpad}
#             """,
#             input_variables=["query", "agent_scratchpad"]
#         )
        
#         agent = (
#             {
#                 "query": lambda x: x,
#                 "agent_scratchpad": lambda x: format_to_openai_function_messages(x)
#             }
#             | prompt
#             | self.llm.bind_functions(tools)
#             | OpenAIFunctionsAgentOutputParser()
#         )
        
#         agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
#         result = agent_executor.invoke({"query": query})
        
#         return result["output"]
    
#     def _retrieve_user_stories(self):
#         """Retrieve all user stories from the database"""
#         user_stories = self.db_manager.retrieve_artifacts_by_type("user_story")
#         return json.dumps(user_stories, indent=2)
    
#     def _retrieve_code(self):
#         """Retrieve all code artifacts from the database"""
#         code_artifacts = self.db_manager.retrieve_artifacts_by_type("code")
#         return json.dumps(code_artifacts, indent=2)
    
#     def _retrieve_test_cases(self):
#         """Retrieve all test cases from the database"""
#         test_cases = self.db_manager.retrieve_artifacts_by_type("test_case")
#         return json.dumps(test_cases, indent=2)
    
#     def _retrieve_test_results(self):
#         """Retrieve test execution results from the database"""
#         test_results = self.db_manager.retrieve_artifacts_by_type("test_results")
#         return json.dumps(test_results, indent=2)
    
#     def _search_artifacts(self, query):
#         """Search for artifacts based on query"""
#         artifacts = self.db_manager.search_artifacts(query)
#         return json.dumps(artifacts, indent=2)



# from langchain.prompts import PromptTemplate
# from langchain.agents import Tool
# from langchain.agents import AgentExecutor
# from langchain_core.output_parsers import StrOutputParser
# from langchain_community.llms import HuggingFacePipeline
# from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
# import json

# class ProjectManagerAgent:
#     def __init__(self, llm_model, db_manager=None):
#         if not isinstance(llm_model, str):
#             raise ValueError(f"llm_model must be a string! Got: {type(llm_model)}")

#         print(f"✅ Loading Hugging Face model: {llm_model}")

#         tokenizer = AutoTokenizer.from_pretrained(llm_model)
#         model = AutoModelForCausalLM.from_pretrained(llm_model)

#         self.llm = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
#         self.db_manager = db_manager


#     def get_status(self, query):
#         """Get project status based on PM query."""
#         tools = [
#             Tool(name="retrieve_user_stories", func=self._retrieve_user_stories,
#                  description="Retrieve user stories from the project repository"),
#             Tool(name="retrieve_code", func=self._retrieve_code,
#                  description="Retrieve code artifacts from the project repository"),
#             Tool(name="retrieve_test_cases", func=self._retrieve_test_cases,
#                  description="Retrieve test cases from the project repository"),
#             Tool(name="retrieve_test_results", func=self._retrieve_test_results,
#                  description="Retrieve test execution results from the project repository"),
#             Tool(name="search_artifacts", func=self._search_artifacts,
#                  description="Search through all project artifacts based on query")
#         ]

#         prompt = PromptTemplate(
#             template="""
#             You are a Project Manager overseeing a software development project. Your team consists of 
#             Business Analysts, Developers, and QA Testers. 

#             Your task is to provide status updates and answer questions about the project artifacts and progress.

#             Query: {query}

#             Use the tools available to retrieve information and provide a precise response.

#             {agent_scratchpad}
#             """,
#             input_variables=["query", "agent_scratchpad"]
#         )

#         agent = ({"query": lambda x: x} | prompt | self.llm | StrOutputParser())

#         agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
#         result = agent_executor.invoke({"query": query})

#         return result

#     def _retrieve_user_stories(self):
#         """Retrieve all user stories from the database."""
#         user_stories = self.db_manager.retrieve_artifacts_by_type("user_story")
#         return json.dumps(user_stories, indent=2)

#     def _retrieve_code(self):
#         """Retrieve all code artifacts from the database."""
#         code_artifacts = self.db_manager.retrieve_artifacts_by_type("code")
#         return json.dumps(code_artifacts, indent=2)

#     def _retrieve_test_cases(self):
#         """Retrieve all test cases from the database."""
#         test_cases = self.db_manager.retrieve_artifacts_by_type("test_case")
#         return json.dumps(test_cases, indent=2)

#     def _retrieve_test_results(self):
#         """Retrieve test execution results from the database."""
#         test_results = self.db_manager.retrieve_artifacts_by_type("test_results")
#         return json.dumps(test_results, indent=2)

#     def _search_artifacts(self, query):
#         """Search for artifacts based on query."""
#         artifacts = self.db_manager.search_artifacts(query)
#         return json.dumps(artifacts, indent=2)



from langchain.prompts import PromptTemplate
from langchain.agents import Tool
from langchain.agents import AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import json

class ProjectManagerAgent:
    def __init__(self, llm_model, db_manager=None):
        if not isinstance(llm_model, str):
            raise ValueError(f"llm_model must be a string! Got: {type(llm_model)}")
        
        print(f"✅ Loading Hugging Face model: {llm_model}")
        
        tokenizer = AutoTokenizer.from_pretrained(llm_model)
        model = AutoModelForCausalLM.from_pretrained(llm_model)
        
        self.hf_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
        # Create a HuggingFacePipeline wrapper for use with LangChain
        self.llm = HuggingFacePipeline(pipeline=self.hf_pipeline)
        self.db_manager = db_manager
    
    def get_status(self, query):
        """Get project status based on PM query."""
        tools = [
            Tool(name="retrieve_user_stories", func=self._retrieve_user_stories,
                 description="Retrieve user stories from the project repository"),
            Tool(name="retrieve_code", func=self._retrieve_code,
                 description="Retrieve code artifacts from the project repository"),
            Tool(name="retrieve_test_cases", func=self._retrieve_test_cases,
                 description="Retrieve test cases from the project repository"),
            Tool(name="retrieve_test_results", func=self._retrieve_test_results,
                 description="Retrieve test execution results from the project repository"),
            Tool(name="search_artifacts", func=self._search_artifacts,
                 description="Search through all project artifacts based on query")
        ]
        
        prompt = PromptTemplate(
            template="""
            You are a Project Manager overseeing a software development project. Your team consists of 
            Business Analysts, Developers, and QA Testers.
            
            Your task is to provide status updates and answer questions about the project artifacts and progress.
            
            Query: {query}
            
            Use the tools available to retrieve information and provide a precise response.
            {agent_scratchpad}
            """,
            input_variables=["query", "agent_scratchpad"]
        )
        
        # For direct usage without tools, use this simplified approach
        if query.lower().strip() in ["summary", "overview", "help"]:
            formatted_prompt = prompt.format(
                query=query,
                agent_scratchpad=""
            )
            response = self.hf_pipeline(formatted_prompt)[0]['generated_text']
            # Strip the original prompt if it's in the response
            if formatted_prompt in response:
                response = response.replace(formatted_prompt, "").strip()
            return response
        
        # For more complex queries, use the agent approach
        try:
            # Create the agent using the HuggingFacePipeline wrapper for LangChain compatibility
            agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.llm,
                tools=tools,
                verbose=True
            )
            
            result = agent_executor.run(query)
            return result
        except Exception as e:
            # Fallback if agent execution fails
            print(f"Agent execution failed: {e}")
            formatted_prompt = f"""
            You are a Project Manager. Please provide a general response to this query 
            without using external tools: {query}
            """
            response = self.hf_pipeline(formatted_prompt)[0]['generated_text']
            if formatted_prompt in response:
                response = response.replace(formatted_prompt, "").strip()
            return f"I had some difficulty processing that with my tools, but here's what I can tell you:\n\n{response}"
    
    def _retrieve_user_stories(self):
        """Retrieve all user stories from the database."""
        user_stories = self.db_manager.retrieve_artifacts_by_type("user_story")
        return json.dumps(user_stories, indent=2)
    
    def _retrieve_code(self):
        """Retrieve all code artifacts from the database."""
        code_artifacts = self.db_manager.retrieve_artifacts_by_type("code")
        return json.dumps(code_artifacts, indent=2)
    
    def _retrieve_test_cases(self):
        """Retrieve all test cases from the database."""
        test_cases = self.db_manager.retrieve_artifacts_by_type("test_case")
        return json.dumps(test_cases, indent=2)
    
    def _retrieve_test_results(self):
        """Retrieve test execution results from the database."""
        test_results = self.db_manager.retrieve_artifacts_by_type("test_results")
        return json.dumps(test_results, indent=2)
    
    def _search_artifacts(self, query):
        """Search for artifacts based on query."""
        artifacts = self.db_manager.search_artifacts(query)
        return json.dumps(artifacts, indent=2)