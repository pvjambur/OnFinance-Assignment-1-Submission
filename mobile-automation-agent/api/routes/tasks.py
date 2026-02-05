from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models.task import TaskCreate, TaskHistory
from agents.intent_agent import intent_agent
# from core.orchestrator import orchestrator # would need async wrapper

router = APIRouter()

@router.post("/", response_model=dict)
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    """
    Submit a new task command.
    """
    # 1. Parse Intent immediately
    intent = intent_agent.run(task.command)
    
    if intent.get("error"):
        raise HTTPException(status_code=400, detail="Could not parse intent")

    # 2. Trigger Orchestrator (Async)
    # background_tasks.add_task(orchestrator.execute_task_loop, intent)
    
    return {
        "status": "accepted",
        "task_id": "pending-uuid", # In real app, create DB record first
        "intent_parsed": intent
    }

@router.get("/", response_model=List[str])
async def list_tasks():
    return ["Task 1", "Task 2"] # Placeholder
