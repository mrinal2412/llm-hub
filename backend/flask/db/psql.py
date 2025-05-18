import code
import logging
from math import log
import uuid
from venv import create
from backend.flask.gpt.gpt_client import generateText
from backend.flask.model.models import (
    async_session as AsyncSessionLocal,
)
from sqlalchemy import (
    Table,
    Column,
    delete,
    func,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
    insert,
    update,
)

from backend.flask.model.models import User, Organization, Project, EngineeringTask
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from backend.flask.utils.json_extractor import extract_json_field


REDEX_LOGO_PROFILE_PIC_URL = "/static/images/r-tbg-square-hd-1.png"


async def update_engineering_task_status(task_id: str, new_status: str, notes):
    async with AsyncSessionLocal() as session:  # Ensure AsyncSessionLocal is correctly defined elsewhere
        try:
            # Begin a transaction
            async with session.begin():
                # Fetch the task by task_id
                result = await session.execute(
                    select(EngineeringTask).where(EngineeringTask.task_id == task_id)
                )
                task = result.scalars().first()
                

                if task is None:
                    return "Task not found", False

                # Update the status
                task.status =  new_status
                ## To: Do . Append the notes rather than adding a new one
                task.notes = notes
                await session.flush()
                await session.commit()

                # Commit is automatically handled by the context manager
                return "Status updated successfully", True

        except NoResultFound:
            # This specific exception catch is redundant if checking task is None
            return "Task not found", False
        except Exception as e:
            # General exception handling to catch unexpected errors
            return f"An error occurred: {str(e)}", False

async def get_org_from_github_id(github_id: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                org = await session.execute(
                    select(Organization).where(Organization.github_id == github_id)
                )
                raw_organization = org.scalars().one()
                organizations = {
                    "organization_name": str(raw_organization.organization_name),
                    "github_id": raw_organization.github_id,
                }
            except NoResultFound:
                organizations = {}
            return organizations

async def get_project_ids_from_github_id(github_id: str):
    github_id = str(github_id)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                results = await session.execute(
                select(Project.project_id)
                .join(User, User.user_id == Project.user_id)
                .join(Organization, Organization.organization_name == User.organization_name)
                .where(Organization.github_id == github_id)
                    )
                project_ids = [str(project_id) for project_id in results.scalars().all()]
            except NoResultFound:
                project_ids = []

            return project_ids




async def get_org(user_email: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                org = await session.execute(
                    select(Organization).where(Organization.address == user_email)
                )
                raw_organization = org.scalars().one()
                organizations = {
                    "organization_name": str(raw_organization.organization_name),
                    "github_id": raw_organization.github_id,
                }
            except NoResultFound:
                organizations = {}
            return organizations


async def get_tasks_from_db(project_id: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(EngineeringTask.task_id,
                       EngineeringTask.project_id,
                       EngineeringTask.title,
                       EngineeringTask.description,
                       EngineeringTask.relevance_to_user,
                       EngineeringTask.status, 
                       EngineeringTask.owner,
                       EngineeringTask.notes).where(EngineeringTask.project_id == project_id)
            )
            raw_tasks = result.all()
         
            tasks = [
                {
                    "task_id": str(task.task_id),
                    "project_id": str(task.project_id),
                    "title": task.title,
                    "description": task.description,
                    "relevance_to_user": task.relevance_to_user,
                    "status": task.status,
                    "owner": task.owner,
                    "notes": task.notes
                }
                for task in raw_tasks
            ]
            return tasks


async def retrieve_projects(user_id: str):
    async with AsyncSessionLocal() as session:  # Use the sessionmaker instance you defined
        async with session.begin():
            # Execute a query to select only specific columns from the projects table
            result = await session.execute(
                select(Project.project_id, Project.name, Project.description).where(
                    Project.user_id == user_id
                )
            )
            # Use scalars() to fetch the results and then use all() to get them as a list of tuples
            raw_projects = result.all()

            # print("blaaah")
            # print(raw_projects)
            # for project in raw_projects:
            #     print(project)

            projects = [
                {
                    "project_id": str(project.project_id),
                    "name": project.name,
                    "description": project.description,
                }
                for project in raw_projects
            ]
            return projects


async def add_org(organization_name, github_id, email):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                org = await session.execute(
                    select(Organization).where(Organization.name == organization_name)
                )
                organization = org.one()
                organization.github_id = github_id
                organization.address = email
            except NoResultFound:
                organization = Organization(
                    organization_name=organization_name,
                    name=organization_name,
                    address=email,
                    github_id=github_id,
                )
                session.add(organization)
                await session.flush()
                await session.commit()


async def onboard(
    organization_name,
    address,
    first_name,
    last_name,
    email
):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if the organization exists
            try:
                org = await session.execute(
                    select(Organization).where(Organization.name == organization_name)
                )
                organization = org.scalars().one()
            except NoResultFound:
                organization = Organization(
                    organization_name=organization_name,
                    name=organization_name,
                    address=address,
                )
                session.add(organization)
                await session.flush()  # Ensure 'organization_id' is available after insert

            # Check if the user exists
            try:
                user = await session.execute(select(User).where(User.email == email))
                user = user.scalars().one()
            except NoResultFound:
                user = User(
                    user_id=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    organization_name=organization_name,
                )
                session.add(user)
                await session.flush()
            await session.commit()
    


async def add_data(
    organization_name,
    address,
    first_name,
    last_name,
    email,
    project_name,
    project_description,
    tasks,
):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if the organization exists
            try:
                org = await session.execute(
                    select(Organization).where(Organization.name == organization_name)
                )
                organization = org.scalars().one()
            except NoResultFound:
                organization = Organization(
                    organization_name=organization_name,
                    name=organization_name,
                    address=address,
                )
                session.add(organization)
                await session.flush()  # Ensure 'organization_id' is available after insert

            # Check if the user exists
            try:
                user = await session.execute(select(User).where(User.email == email))
                user = user.scalars().one()
            except NoResultFound:
                user = User(
                    user_id=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    organization_name=organization_name,
                )
                session.add(user)
                await session.flush()  # Ensure 'user_id' is available after insert

            # Create a new project
            project = Project(
                user_id=user.user_id, name=project_name, description=project_description
            )
            session.add(project)
            await session.flush()  # Ensure 'project_id' is available after insert

            # Add engineering tasks
            for task in tasks:
                engineering_task = EngineeringTask(
                    project_id=project.project_id,
                    title=task["title"],
                    description=task["description"],
                    relevance_to_user=task.get("product_contribution", None),
                    status="pending",
                    task_id = task["task_id"],
                    owner  = task["owner"]
                )
                session.add(engineering_task)

            await session.commit()
        return project.project_id
