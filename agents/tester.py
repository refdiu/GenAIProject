# # agents/tester.py
# from langchain.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# import json
# import os
# import re

# class TesterAgent:
#     def __init__(self, llm, db_manager):
#         self.llm = llm
#         self.db_manager = db_manager
    
#     def _extract_code_blocks(self, text):
#         """Extract code blocks from markdown text"""
#         code_blocks = []
#         pattern = r"```(?:python)?\s*(.*?)```"
#         matches = re.findall(pattern, text, re.DOTALL)
        
#         for match in matches:
#             code_blocks.append(match.strip())
        
#         return code_blocks
    
#     def generate_test_cases(self, user_stories, code):
#         """Generate test cases based on user stories and code"""
#         # Load test case template
#         template_path = "database/templates/test_case.md"
#         with open(template_path, "r") as f:
#             template_content = f.read()
        
#         if isinstance(user_stories, str):
#             try:
#                 user_stories = json.loads(user_stories)
#             except json.JSONDecodeError:
#                 user_stories = [{"title": "Parsed from text", "description": user_stories}]
        
#         if isinstance(code, list):
#             code_content = "\n\n".join([c.get("content", "") for c in code])
#         else:
#             code_content = code
        
#         # Create prompt for generating test cases
#         prompt = PromptTemplate(
#             template="""
#             You are an experienced QA Tester. Your task is to create comprehensive test cases 
#             for the following code based on the user stories.
            
#             User Stories:
#             {user_stories}
            
#             Code to Test:
#             {code}
            
#             Test Case Template:
#             {template}
            
#             For each user story:
#             1. Create at least 3 test cases covering different scenarios (happy path, edge cases, error cases)
#             2. Make sure each test case includes a clear description, preconditions, steps, expected results, and status
#             3. Use pytest for the test implementation
#             4. Return the test cases as Python code inside markdown code blocks
            
#             Ensure your test cases thoroughly validate the acceptance criteria from the user stories.
#             """,
#             input_variables=["user_stories", "code", "template"]
#         )
        
#         # Generate test cases using LLM
#         chain = prompt | self.llm | StrOutputParser()
#         result = chain.invoke({
#             "user_stories": json.dumps(user_stories, indent=2),
#             "code": code_content,
#             "template": template_content
#         })
        
#         # Extract test code blocks from the result
#         test_code_blocks = self._extract_code_blocks(result)
        
#         # Save the generated test cases
#         os.makedirs("artifacts/test_cases", exist_ok=True)
        
#         test_artifacts = []
#         for idx, test_code in enumerate(test_code_blocks):
#             test_id = f"test_case_{idx+1}"
            
#             # Save to ChromaDB
#             self.db_manager.store_artifact(
#                 artifact_id=test_id,
#                 content=test_code,
#                 metadata={
#                     "type": "test_case",
#                     "language": "python",
#                     "framework": "pytest",
#                     "user_story_ids": [f"user_story_{i+1}" for i in range(len(user_stories))]
#                 }
#             )
            
#             # Save to file system
#             file_path = f"artifacts/test_cases/{test_id}.py"
#             with open(file_path, "w") as f:
#                 f.write(test_code)
            
#             test_artifacts.append({
#                 "id": test_id,
#                 "path": file_path,
#                 "content": test_code
#             })
        
#         # If no test blocks were extracted, save the raw output
#         if not test_code_blocks:
#             test_id = "test_case_raw"
#             file_path = f"artifacts/test_cases/{test_id}.txt"
#             with open(file_path, "w") as f:
#                 f.write(result)
            
#             self.db_manager.store_artifact(
#                 artifact_id=test_id,
#                 content=result,
#                 metadata={
#                     "type": "test_case_raw",
#                     "user_story_ids": [f"user_story_{i+1}" for i in range(len(user_stories))]
#                 }
#             )
            
#             test_artifacts.append({
#                 "id": test_id,
#                 "path": file_path,
#                 "content": result
#             })
        
#         return test_artifacts
    
#     def execute_tests(self, code, test_cases):
#         """Simulate execution of tests against the code"""
#         # In a real app, you'd actually run the tests
#         # Here we'll simulate by having the LLM analyze if tests would pass
        
#         if isinstance(code, list):
#             code_content = "\n\n".join([c.get("content", "") for c in code])
#         else:
#             code_content = code
            
#         if isinstance(test_cases, list):
#             test_content = "\n\n".join([t.get("content", "") for t in test_cases])
#         else:
#             test_content = test_cases
        
#         prompt = PromptTemplate(
#             template="""
#             You are an experienced QA Test Executor. Your task is to analyze the following code and test cases 
#             and determine which tests would pass and which would fail.
            
#             Code:
#             {code}
            
#             Test Cases:
#             {test_cases}
            
#             For each test case:
#             1. Determine if it would pass or fail based on the implementation
#             2. Provide a brief explanation of why it would pass or fail
#             3. If it would fail, suggest how to fix either the code or the test
            
#             Return your analysis as a JSON array where each object has the following structure:
#             {{
#                 "test_id": "Name or identifier of the test",
#                 "result": "PASS" or "FAIL",
#                 "explanation": "Why it passed or failed",
#                 "fix_suggestion": "How to fix it (if failed)"
#             }}
#             """,
#             input_variables=["code", "test_cases"]
#         )
        
#         # Analyze tests using LLM
#         chain = prompt | self.llm | StrOutputParser()
#         result = chain.invoke({
#             "code": code_content,
#             "test_cases": test_content
#         })
        
#         # Try to parse the result as JSON
#         try:
#             test_results = json.loads(result)
#         except json.JSONDecodeError:
#             # Fallback if the output isn't proper JSON
#             test_results = [{
#                 "test_id": "Error parsing test results",
#                 "result": "UNKNOWN",
#                 "explanation": result,
#                 "fix_suggestion": "N/A"
#             }]
        
#         # Save test results
#         os.makedirs("artifacts/test_cases", exist_ok=True)
#         with open("artifacts/test_cases/test_results.json", "w") as f:
#             json.dump(test_results, f, indent=2)
        
#         # Save to ChromaDB
#         self.db_manager.store_artifact(
#             artifact_id="test_results",
#             content=json.dumps(test_results),
#             metadata={
#                 "type": "test_results"
#             }
#         )
        
#         return test_results

# agents/tester.py
from transformers import pipeline
import json
import os
import re

class TesterAgent:
    def __init__(self, model=None, db_manager=None):
        """
        Initialize the TesterAgent with a Hugging Face pipeline
        
        Args:
            model: The model to use (can be a string model name or a pre-initialized model)
            db_manager: Database manager for storing artifacts
        """
        # Initialize the pipeline correctly
        if model is None:
            # Create a default text-generation pipeline if no model is provided
            self.pipeline = pipeline(task="text-generation")
        elif isinstance(model, str):
            # If a string is provided, treat it as a model name
            self.pipeline = pipeline(task="text-generation", model=model)
        else:
            # If an object is provided, use it directly as the model
            self.pipeline = model
            
        self.db_manager = db_manager
    
    def _extract_code_blocks(self, text):
        """Extract code blocks from markdown text"""
        code_blocks = []
        pattern = r"```(?:python)?\s*(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            code_blocks.append(match.strip())
        
        return code_blocks
    
    def generate_test_cases(self, user_stories, code):
        """Generate test cases based on user stories and code"""
        # Load test case template
        template_path = "database/templates/test_case.md"
        with open(template_path, "r") as f:
            template_content = f.read()
        
        if isinstance(user_stories, str):
            try:
                user_stories = json.loads(user_stories)
            except json.JSONDecodeError:
                user_stories = [{"title": "Parsed from text", "description": user_stories}]
        
        if isinstance(code, list):
            code_content = "\n\n".join([c.get("content", "") for c in code])
        else:
            code_content = code
        
        # Create prompt for generating test cases
        prompt = f"""
        You are an experienced QA Tester. Your task is to create comprehensive test cases 
        for the following code based on the user stories.
        
        User Stories:
        {json.dumps(user_stories, indent=2)}
        
        Code to Test:
        {code_content}
        
        Test Case Template:
        {template_content}
        
        For each user story:
        1. Create at least 3 test cases covering different scenarios (happy path, edge cases, error cases)
        2. Make sure each test case includes a clear description, preconditions, steps, expected results, and status
        3. Use pytest for the test implementation
        4. Return the test cases as Python code inside markdown code blocks
        
        Ensure your test cases thoroughly validate the acceptance criteria from the user stories.
        """
        
        # Generate test cases using HF pipeline
        generation_kwargs = {
            "max_length": 2048,
            "do_sample": True,
            "temperature": 0.7
        }
        # Adjust based on pipeline type
        if hasattr(self.pipeline, "generate"):
            # For newer pipeline versions or language models
            result = self.pipeline(prompt, **generation_kwargs)[0]['generated_text']
        else:
            # For text2text or chat models which might have different APIs
            result = self.pipeline(prompt)
            # Handle different return formats
            if isinstance(result, str):
                pass  # Already a string
            elif isinstance(result, list) and isinstance(result[0], dict):
                result = result[0].get('generated_text', str(result))
            elif isinstance(result, dict):
                result = result.get('generated_text', str(result))
            else:
                result = str(result)  # Fallback
        
        # Extract test code blocks from the result
        test_code_blocks = self._extract_code_blocks(result)
        
        # Save the generated test cases
        os.makedirs("artifacts/test_cases", exist_ok=True)
        
        test_artifacts = []
        for idx, test_code in enumerate(test_code_blocks):
            test_id = f"test_case_{idx+1}"
            
            # Save to ChromaDB if db_manager is available
            if self.db_manager:
                self.db_manager.store_artifact(
                    artifact_id=test_id,
                    content=test_code,
                    metadata={
                        "type": "test_case",
                        "language": "python",
                        "framework": "pytest",
                        "user_story_ids": [f"user_story_{i+1}" for i in range(len(user_stories))]
                    }
                )
            
            # Save to file system
            file_path = f"artifacts/test_cases/{test_id}.py"
            with open(file_path, "w") as f:
                f.write(test_code)
            
            test_artifacts.append({
                "id": test_id,
                "path": file_path,
                "content": test_code
            })
        
        # If no test blocks were extracted, save the raw output
        if not test_code_blocks:
            test_id = "test_case_raw"
            file_path = f"artifacts/test_cases/{test_id}.txt"
            with open(file_path, "w") as f:
                f.write(result)
            
            if self.db_manager:
                self.db_manager.store_artifact(
                    artifact_id=test_id,
                    content=result,
                    metadata={
                        "type": "test_case_raw",
                        "user_story_ids": [f"user_story_{i+1}" for i in range(len(user_stories))]
                    }
                )
            
            test_artifacts.append({
                "id": test_id,
                "path": file_path,
                "content": result
            })
        
        return test_artifacts
    
    def execute_tests(self, code, test_cases):
        """Simulate execution of tests against the code"""
        # In a real app, you'd actually run the tests
        # Here we'll simulate by having the model analyze if tests would pass
        
        if isinstance(code, list):
            code_content = "\n\n".join([c.get("content", "") for c in code])
        else:
            code_content = code
            
        if isinstance(test_cases, list):
            test_content = "\n\n".join([t.get("content", "") for t in test_cases])
        else:
            test_content = test_cases
        
        prompt = f"""
        You are an experienced QA Test Executor. Your task is to analyze the following code and test cases 
        and determine which tests would pass and which would fail.
        
        Code:
        {code_content}
        
        Test Cases:
        {test_content}
        
        For each test case:
        1. Determine if it would pass or fail based on the implementation
        2. Provide a brief explanation of why it would pass or fail
        3. If it would fail, suggest how to fix either the code or the test
        
        Return your analysis as a JSON array where each object has the following structure:
        {{
            "test_id": "Name or identifier of the test",
            "result": "PASS" or "FAIL",
            "explanation": "Why it passed or failed",
            "fix_suggestion": "How to fix it (if failed)"
        }}
        """
        
        # Analyze tests using HF pipeline
        generation_kwargs = {
            "max_length": 2048,
            "do_sample": False
        }
        
        # Adjust based on pipeline type
        if hasattr(self.pipeline, "generate"):
            # For newer pipeline versions or language models
            result = self.pipeline(prompt, **generation_kwargs)[0]['generated_text']
        else:
            # For text2text or chat models which might have different APIs
            result = self.pipeline(prompt)
            # Handle different return formats
            if isinstance(result, str):
                pass  # Already a string
            elif isinstance(result, list) and isinstance(result[0], dict):
                result = result[0].get('generated_text', str(result))
            elif isinstance(result, dict):
                result = result.get('generated_text', str(result))
            else:
                result = str(result)  # Fallback
        
        # Try to parse the result as JSON
        try:
            # Find JSON in the response (it might contain explanatory text)
            json_match = re.search(r'\[\s*{.*}\s*\]', result, re.DOTALL)
            if json_match:
                test_results = json.loads(json_match.group(0))
            else:
                raise json.JSONDecodeError("No JSON found", result, 0)
        except json.JSONDecodeError:
            # Fallback if the output isn't proper JSON
            test_results = [{
                "test_id": "Error parsing test results",
                "result": "UNKNOWN",
                "explanation": result,
                "fix_suggestion": "N/A"
            }]
        
        # Save test results
        os.makedirs("artifacts/test_cases", exist_ok=True)
        with open("artifacts/test_cases/test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        # Save to ChromaDB if available
        if self.db_manager:
            self.db_manager.store_artifact(
                artifact_id="test_results",
                content=json.dumps(test_results),
                metadata={
                    "type": "test_results"
                }
            )
        
        return test_results