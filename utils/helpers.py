# utils/helpers.py
"""
Helper functions for the project team simulation
"""
import re
import json
import os

def extract_code_blocks(text):
    """Extract code blocks from markdown text"""
    code_blocks = []
    pattern = r"```(?:python)?\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        code_blocks.append(match.strip())
    
    return code_blocks

def ensure_directory_exists(directory_path):
    """Ensure a directory exists, create it if it doesn't"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def load_template(template_path):
    """Load a template file"""
    with open(template_path, "r") as f:
        return f.read()

def save_artifact(artifact_id, content, artifact_type, directory=None):
    """Save an artifact to a file"""
    if directory is None:
        directory = f"artifacts/{artifact_type}s"
    
    ensure_directory_exists(directory)
    
    file_extension = ".py" if artifact_type == "code" else ".json" if artifact_type == "user_story" else ".txt"
    file_path = f"{directory}/{artifact_id}{file_extension}"
    
    with open(file_path, "w") as f:
        if artifact_type == "user_story" and isinstance(content, dict):
            json.dump(content, f, indent=2)
        else:
            f.write(content)
    
    return file_path

def parse_json_safely(json_string):
    """Safely parse JSON string with fallback for malformed JSON"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        # Try to fix common JSON errors
        # 1. Missing quotes around keys
        fixed_string = re.sub(r'(\s*?)(\w+)(\s*?):', r'\1"\2"\3:', json_string)
        # 2. Single quotes instead of double quotes
        fixed_string = fixed_string.replace("'", "\"")
        
        try:
            return json.loads(fixed_string)
        except json.JSONDecodeError:
            # Return a basic structure if all else fails
            return {"error": "Could not parse JSON", "content": json_string}