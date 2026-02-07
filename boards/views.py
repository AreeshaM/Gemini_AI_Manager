from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Task, Comment
from .ai_engine import generate_smart_tasks
from google import genai
import os

# Dashboard View
def dashboard(request):
    if request.method == "POST":
        p_name = request.POST.get('project_name')
        p_desc = request.POST.get('project_desc')
        new_project = Project.objects.create(name=p_name, description=p_desc)
        
        ai_response = generate_smart_tasks(p_name, p_desc)
        
        if "Error" in ai_response or not ai_response:
            Task.objects.create(project=new_project, title="AI Pending", description="API limit reached. Please wait for reset.", status='TODO')
        else:
            lines = ai_response.split('\n')
            for line in lines:
                if ":" in line:
                    title, desc = line.split(":", 1)
                    Task.objects.create(project=new_project, title=title.strip(), description=desc.strip(), status='TODO')
        return redirect('dashboard')

    projects_list = []
    for project in Project.objects.all().order_by('-id'):
        total = project.tasks.count()
        done = project.tasks.filter(status='DONE').count()
        progress = (done / total * 100) if total > 0 else 0
        projects_list.append({'obj': project, 'progress': round(progress), 'tasks': project.tasks.all()})

    return render(request, 'boards/dashboard.html', {'projects_list': projects_list})

# Task Detail View (With Crash Protection)
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == "POST":
        author = request.POST.get('author_name')
        content = request.POST.get('comment_text')
        if content:
            Comment.objects.create(task=task, author_name=author, text=content)
            return redirect('task_detail', task_id=task.id)

    # Gemini API Call - Stable Version
    api_key = os.getenv("GEMINI_API_KEY")
    solution = "AI Solution currently unavailable. Please check your API key or wait for the limit to reset."

    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"Provide a technical solution for: {task.title}. Context: {task.project.description}"
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            solution = response.text
        except Exception as e:
            solution = f"💡 [Offline Mode]: Our AI Architect is resting. Manual guide: Focus on building the core logic for {task.title}."

    comments = task.comments.all().order_by('-created_at')
    return render(request, 'boards/task_detail.html', {'task': task, 'solution': solution, 'comments': comments})

# Update Task Status
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'DONE' if task.status == 'TODO' else 'TODO'
    task.save()
    return redirect('dashboard')