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
from sqlalchemy import Text
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



engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)







    
class Prompt(Base):
    __tablename__ = "prompts"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_name_version"),
    )


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    status = Column(SQLEnum(StatusEnum, name="status_enum"), nullable=False)
    body = Column(Text, nullable=False)


    def __repr__(self):
        return f"<Prompt id={self.id!r} name={self.name!r} version={self.version!r} status={self.status!r}  body={self.body!r}>"