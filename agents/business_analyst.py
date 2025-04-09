from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import os
import re
import time
from typing import List, Dict, Any

class BusinessAnalystAgent:
    def __init__(self, llm, db_manager):
        self.llm = llm
        self.db_manager = db_manager
        
    def generate_user_stories(self, business_requirements):
        """Generate user stories from business requirements"""
        # Load user story template
        template_path = "database/templates/user_story.md"
        with open(template_path, "r") as f:
            template_content = f.read()
        
        # Create the prompt string directly
        formatted_prompt = f"""
        You are an experienced Business Analyst. Your task is to convert the following business 
        requirements into well-structured user stories.
        
        Business Requirements:
        {business_requirements}
        
        User Story Template:
        {template_content}
        
        Generate at least 5 detailed user stories following the template format. 
        Each user story should include a clear title, description, acceptance criteria, 
        and priority level.
        
        Return the user stories ONLY as a valid JSON array where each object represents one user story.
        Do not include any explanatory text before or after the JSON. The response should be parseable by json.loads().
        """
        
        # Generate user stories using HuggingFace pipeline directly
        try:
            # Option 1: If pipeline accepts keyword arguments directly
            generated_output = self.llm(
                formatted_prompt, 
                max_new_tokens=1024,         # Generate up to 1024 new tokens 
                do_sample=True,              # Enable sampling for more diverse outputs
                temperature=0.7,             # Control randomness
                top_p=0.95                   # Nucleus sampling parameter
            )
        except TypeError as e:
            # Option 2: If pipeline requires specific format
            print(f"Adjusting generation parameters: {e}")
            try:
                # Some pipelines expect a dictionary of parameters
                generated_output = self.llm(
                    formatted_prompt,
                    generate_kwargs={
                        'max_new_tokens': 1024,
                        'do_sample': True,
                        'temperature': 0.7,
                        'top_p': 0.95
                    }
                )
            except Exception as e2:
                print(f"Second attempt failed: {e2}")
                # Option 3: Last resort - try with minimal parameters
                generated_output = self.llm(formatted_prompt, max_length=None, max_new_tokens=1024)
        
        # Extract the generated text (format depends on your pipeline configuration)
        if isinstance(generated_output, list):
            result = generated_output[0].get('generated_text', '')
        else:
            result = str(generated_output)
        
        # Clean up the output to extract just the new content
        if formatted_prompt in result:
            result = result.replace(formatted_prompt, '')
        
        # Try to extract JSON from the response using regex
        json_pattern = r'\[[\s\S]*\]'  # Match anything that looks like a JSON array
        json_match = re.search(json_pattern, result)
        
        if json_match:
            potential_json = json_match.group(0)
            try:
                user_stories = json.loads(potential_json)
                print("✅ Successfully parsed JSON from model output")
            except json.JSONDecodeError:
                print(f"⚠️ Found JSON-like structure but couldn't parse it: {potential_json[:100]}...")
                user_stories = self._fallback_processing(result)
        else:
            user_stories = self._fallback_processing(result)
        
        # Save user stories with retry and local storage fallback
        self._save_user_stories(user_stories)
        
        return user_stories
    
    def _save_user_stories(self, user_stories: List[Dict[str, Any]], max_retries: int = 3) -> None:
        """Save user stories to ChromaDB with retry mechanism and local fallback"""
        # Always save to the file system first as backup
        os.makedirs("artifacts/user_stories", exist_ok=True)
        for idx, story in enumerate(user_stories):
            story_id = f"user_story_{idx+1}"
            with open(f"artifacts/user_stories/{story_id}.json", "w") as f:
                json.dump(story, f, indent=2)
            
        # Then try to save to ChromaDB with retries
        for idx, story in enumerate(user_stories):
            story_id = f"user_story_{idx+1}"
            metadata = {
                "type": "user_story",
                "title": str(story.get("title", "Untitled")),
                "priority": str(story.get("priority", "Medium"))
            }
            
            # Truncate content if it's too large
            content = json.dumps(story)
            if len(content) > 5000:  # Arbitrary limit to avoid embedding timeout
                print(f"⚠️ Story content too large ({len(content)} chars), truncating for embedding")
                # Create a shorter version with essential info
                short_story = {
                    "title": story.get("title", "Untitled"),
                    "priority": story.get("priority", "Medium"),
                    "description_excerpt": story.get("description", "")[:500] + "..." if len(story.get("description", "")) > 500 else story.get("description", "")
                }
                content_for_embedding = json.dumps(short_story)
            else:
                content_for_embedding = content
                
            # Try to store in ChromaDB with retries
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt+1}/{max_retries} to store {story_id} in ChromaDB")
                    # Store with timeout handling
                    self.db_manager.store_artifact(
                        artifact_id=story_id,
                        content=content_for_embedding,  # Use potentially truncated content for embedding
                        metadata=metadata
                    )
                    print(f"✅ Successfully stored {story_id} in ChromaDB")
                    break  # Success, exit retry loop
                except Exception as e:
                    print(f"⚠️ Error storing in ChromaDB (attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = 2 ** attempt  # 1, 2, 4, 8... seconds
                        print(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Failed to store {story_id} in ChromaDB after {max_retries} attempts")
                        # Continue with other stories even if this one failed
    
    def _fallback_processing(self, result):
        """Fallback function to handle non-JSON output"""
        print("⚠️ Warning: Output is not valid JSON. Attempting structured extraction...")
        
        # Look for patterns like "Title: Something" or similar structures
        stories = []
        
        # Split by possible user story separators
        story_sections = re.split(r'User Story \d+:|Story \d+:', result)
        
        for section in story_sections:
            if not section.strip():
                continue
                
            story = {}
            
            # Extract title
            title_match = re.search(r'Title:?\s*(.*?)(?:\n|$)', section)
            if title_match:
                story["title"] = title_match.group(1).strip()
            else:
                story["title"] = "Untitled Story"
                
            # Extract description
            desc_match = re.search(r'(?:Description|As a|I want)[:]\s*(.*?)(?=\n\s*(?:Acceptance Criteria|Priority)|$)', 
                                  section, re.DOTALL)
            if desc_match:
                story["description"] = desc_match.group(1).strip()
            else:
                story["description"] = section.strip()
                
            # Extract acceptance criteria
            ac_match = re.search(r'Acceptance Criteria:?\s*(.*?)(?=\n\s*Priority|$)', section, re.DOTALL)
            if ac_match:
                criteria_text = ac_match.group(1).strip()
                # Split criteria by numbers, bullets, or newlines
                criteria = re.findall(r'[-*\d.]\s*(.*?)(?=\n[-*\d.]|\n\n|$)', criteria_text + "\n\n")
                if criteria:
                    story["acceptance_criteria"] = criteria
                else:
                    story["acceptance_criteria"] = [criteria_text]
            else:
                story["acceptance_criteria"] = ["No criteria specified"]
                
            # Extract priority
            priority_match = re.search(r'Priority:?\s*(.*?)(?:\n|$)', section)
            if priority_match:
                story["priority"] = priority_match.group(1).strip()
            else:
                story["priority"] = "Medium"
                
            stories.append(story)
        
        # If we couldn't extract anything meaningful, create a single error story
        if not stories:
            stories = [{"title": "Error parsing user stories", 
                        "description": result,
                        "acceptance_criteria": ["N/A"],
                        "priority": "Medium"}]
            
        print(f"✅ Extracted {len(stories)} stories using fallback processing")
        return stories