from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from datetime import datetime
import time
import random
from ..database import engine
from ..models.all_models import Task, TaskStatus, Group
from .whatsapp_service import whatsapp_service

scheduler = BackgroundScheduler()

def check_pending_tasks():
    """
    Periodic job to check for tasks that need to be executed.
    """
    now_str = datetime.now().strftime("%H:%M")
    
    with Session(engine) as session:
        # 1. Find Tasks that are PENDING and match current time
        # This is a simplified logic. In a real scenario, we might have a separate 'Campaign' 
        # that generates Tasks. Here, we assume Tasks are pre-generated or we check Plans.
        
        # For this MVP, let's assume we look for PENDING tasks where scheduled_time <= now
        # OR tasks that are just PENDING and we process them if the global schedule allows.
        
        # Taking "Tasks" as individual send actions in the queue.
        statement = select(Task).where(Task.status == TaskStatus.PENDING)
        tasks = session.exec(statement).all()
        
        for task in tasks:
            # Check if it's time (Simple string match for MVP "HH:MM")
            if task.scheduled_time == now_str:
                process_task(session, task)

def process_task(session: Session, task: Task):
    """
    Executes a single task.
    """
    # Mark as Running
    task.status = TaskStatus.RUNNING
    session.add(task)
    session.commit()
    
    # Get User and Group info
    user = task.user
    # Task might be linked to a specific group but our model didn't link Task -> Group directly yet
    # Let's assume the Task content implies the target or we need to fetch it.
    # Refactoring Model needed? Or just use "Group" logic.
    # Re-reading requirement: "Tasks are executed sequentially... For each group: Send message"
    # So a "Scheduled Time" spawns a "Job" that iterates over "Groups".
    
    # Logic Correction: The Scheduler should trigger a "Campaign" which creates "Tasks" for each group.
    # For now, let's assume the 'Task' IS the action for one group.
    
    target_group = "Unknown" # Need to link Task to Group in next step if missing
    
    # Execute
    success, msg = whatsapp_service.send_message(target_group, task.message_content, task.media_path)
    
    # Update Status
    task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
    task.result_log = msg
    task.last_run = datetime.now()
    session.add(task)
    session.commit()
    
    # Human delay
    delay = random.randint(10, 30)
    time.sleep(delay)

def start_scheduler():
    scheduler.add_job(check_pending_tasks, 'interval', minutes=1)
    scheduler.start()
