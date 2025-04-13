
# -*- coding: utf-8 -*-
"""
Task Management System

This module implements functionality for creating, viewing, updating and deleting tasks in the task management system.

Created: 2023-01-17
Author: John Doe
"""

# Standard library imports
import os
import json
import logging

# Third-party imports
# []

# Local application imports
# []

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TASKS_FILENAME = 'tasks.json'

# Classes and functions
class Task:
    """
    A class for representing a task in the task management system.
    
    Attributes:
        id (int): The unique identifier of the task.
        title (str): The title of the task.
        description (str): The description of the task.
        due_date (datetime): The due date of the task.
        priority (str): The priority of the task.
        status (str): The status of the task.
    """
    
    def __init__(self, id, title, description, due_date, priority, status):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status

class TaskManager:
    """
    A class for managing tasks in the task management system.
    
    Attributes:
        tasks (list[Task]): The list of tasks in the task management system.
    """
    
    def __init__(self):
        self.tasks = []

    def create_task(self, title, description, due_date, priority, status):
        """
        Create a new task with the given title, description, due date, priority and status.
        
        Args:
            title (str): The title of the task.
            description (str): The description of the task.
            due_date (datetime): The due date of the task.
            priority (str): The priority of the task.
            status (str): The status of the task.
        """
        # Implement this function to create a new task with the given title, description, due date, priority and status.
        # Return the created task.
        
    def view_task(self, id=None, title=None):
        """
        View an existing task by its ID or title.
        
        Args:
            id (int, optional): The ID of the task to view. Defaults to None.
            title (str, optional): The title of the task to view. Defaults to None.
        
        Returns:
            Task: The viewed task.
        """
        # Implement this function to view an existing task by its ID or title.
        # Return the viewed task.
        
    def update_task(self, id, title=None, description=None, due_date=None, priority=None, status=None):
        """
        Update an existing task with the given ID, title, description, due date, priority and status.
        
        Args:
            id (int): The ID of the task to update.
            title (str, optional): The new title of the task. Defaults to None.
            description (str, optional): The new description of the task. Defaults to None.
            due_date (datetime, optional): The new due date of the task. Defaults to None.
            priority (str, optional): The new priority of the task. Defaults to None.
            status (str, optional): The new status of the task. Defaults to None.
        """
        # Implement this function to update an existing task with the given ID, title, description, due date, priority and status.
        
    def delete_task(self, id):
        """
        Delete an existing task by its ID.
        
        Args:
            id (int): The ID of the task to delete.
        """
        # Implement this function to delete an existing task by its ID.
