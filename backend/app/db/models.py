from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    projects: List["Project"] = Relationship(back_populates="owner")


class APIKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    key: str = Field(unique=True, index=True, max_length=255)
    user_id: UUID = Field(foreign_key="users.id")
    user: Optional[User] = Relationship()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = Field(default=None)


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    # Bug #3 fix — unique project name per user
    __table_args__ = (UniqueConstraint("owner_id", "name", name="unique_project_per_user"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(max_length=255)
    repo_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: UUID = Field(foreign_key="users.id")
    owner: Optional[User] = Relationship(back_populates="projects")
    documentation: List["Documentation"] = Relationship(back_populates="project")


class Documentation(SQLModel, table=True):
    __tablename__ = "documentation"
    # Bug #4 fix — unique doc per project
    __table_args__ = (UniqueConstraint("code_hash", "project_id", name="unique_doc_per_project"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    file_path: str = Field(max_length=1000)
    function_name: str = Field(max_length=255, index=True)
    code_hash: str = Field(max_length=64, index=True)
    doc_content: str
    language: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    project_id: UUID = Field(foreign_key="projects.id")
    project: Optional[Project] = Relationship(back_populates="documentation")
