import os
import json
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import List, Literal

client = OpenAI() # Relies on OPENAI_API_KEY environment variable

class TaskSchema(BaseModel):
    title: str = Field(description="Title of the care task")
    duration_minutes: int = Field(description="Duration in minutes (1-240)")
    time_of_day: Literal["morning", "afternoon", "evening", "anytime"] = Field(description="Time of day")
    frequency: Literal["daily", "weekly", "monthly"] = Field(description="How often it repeats")
    completed: bool = Field(default=False)

class OptimizationResult(BaseModel):
    explanation: str = Field(description="A friendly explanation of what you changed and why, specific to the pet species.")
    optimized_tasks: List[TaskSchema] = Field(description="The balanced and complete list of tasks")

def optimize_schedule(pet_name: str, species: str, current_tasks: list) -> dict:
    """
    Sends the current tasks to OpenAI and returns an optimized task list.
    """
    system_prompt = (
        "You are an expert pet care scheduling agent. Your job is to review a pet's daily care schedule, "
        "fix any overloaded time slots (e.g., too many tasks in the 'morning'), and ensure essential "
        "tasks are present based on the species.\n"
        "Rules:\n"
        "1. Do not exceed ~90 minutes of total tasks per time_of_day slot (morning, afternoon, evening). "
        "If a slot is overloaded, move some tasks to 'anytime' or another slot.\n"
        "2. Add any missing essential tasks for a {species} (e.g., if a dog lacks a walk, add a 'Walk' task).\n"
        "3. Maintain the completed status of existing tasks.\n"
        "4. Return a JSON structure containing an 'explanation' string and the 'optimized_tasks' list."
    )

    user_message = f"Pet Name: {pet_name}\nSpecies: {species}\nCurrent Tasks:\n{json.dumps(current_tasks, indent=2)}"

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt.format(species=species)},
                {"role": "user", "content": user_message}
            ],
            response_format=OptimizationResult,
        )
        return completion.choices[0].message.parsed.model_dump()
    except Exception as e:
        return {
            "explanation": f"AI Optimization failed: {str(e)}",
            "optimized_tasks": current_tasks
        }
