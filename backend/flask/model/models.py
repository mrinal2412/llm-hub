from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Table,
    Column,
    UniqueConstraint,
    ForeignKey,
    Boolean,
    Integer,
    Text,
    String,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
import enum,uuid
from sqlalchemy.dialects.postgresql import JSONB
import os
from dotenv import load_dotenv


load_dotenv()


class Base(DeclarativeBase):
    pass
class StatusEnum(str, enum.Enum):
    LIVE  = "LIVE"
    Draft = "Draft"

DATABASE_URL = os.environ.get("DATABASE_URL")

print("db env")
print(DATABASE_URL)

# DATABASE_URL = "postgresql+asyncpg://test_postgres_w80l_user:aAcfNJS9sPOjT1tpA4m9qayvLy9GoRM7@dpg-cn1jqnqcn0vc73f91dig-a.oregon-postgres.render.com/test_postgres_w80l"

# DATABASE_URL = "postgresql+asyncpg://postgres:yourPassword@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# class Organization(Base):
#     __tablename__ = "organizations"
#     organization_name = Column(String, primary_key=True)
#     name = Column(Text, nullable=False)
#     address = Column(Text, index=True)
#     github_id = Column(Text, index= True)
#     users = relationship("User", back_populates="organization")


# class User(Base):
#     __tablename__ = "users"
#     user_id = Column(String, primary_key=True)
#     organization_name = Column(
#         String, ForeignKey("organizations.organization_name"), nullable=False
#     )
#     first_name = Column(Text, nullable=False)
#     last_name = Column(Text, nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     organization = relationship("Organization", back_populates="users")
#     projects = relationship("Project", back_populates="user")


# class Project(Base):
#     __tablename__ = "projects"
#     project_id = Column(UUID, primary_key=True, default=uuid.uuid4)
#     user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
#     name = Column(Text, nullable=False)
#     description = Column(Text)
#     status = Column(Text, default="active")
#     user = relationship("User", back_populates="projects")
#     engineering_tasks = relationship(
#         "EngineeringTask",
#         back_populates="project",
#         cascade="all, delete",
#         passive_deletes=True,
#     )


# class EngineeringTask(Base):
#     __tablename__ = "engineering_tasks"
#     task_id = Column(UUID, primary_key=True, default=uuid.uuid4)
#     project_id = Column(UUID, ForeignKey("projects.project_id"), nullable=False)
#     title = Column(Text, nullable=False)
#     description = Column(Text)
#     relevance_to_user = Column(Text)
#     status = Column(Text, default="pending")
#     project = relationship("Project", back_populates="engineering_tasks")
#     notes = Column(Text)
#     owner = Column(Text)
    
class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String(255), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(StatusEnum, name="status_enum"), nullable=False)

    def __repr__(self):
        return f"<Prompt id={self.id!r} name={self.name!r} version={self.version!r} status={self.status!r}>"