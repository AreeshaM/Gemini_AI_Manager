from google import genai
import os

def generate_smart_tasks(project_name, project_desc):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: API Key missing."
    
    client = genai.Client(api_key=api_key)
    prompt = f"As a project architect, create 5 actionable tasks for a project named '{project_name}'. Description: {project_desc}. Format each task as 'Title: Description' on a new line."
    
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"