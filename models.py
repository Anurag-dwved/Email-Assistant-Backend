from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    
    id = Column(String, primary_key=True)
    thread_id = Column(String)
    sender = Column(String)
    recipients = Column(String)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(DateTime)
    is_read = Column(Boolean, default=False)
    labels = Column(String)
    has_attachment = Column(Boolean, default=False)

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(String, primary_key=True)
    email_id = Column(String, ForeignKey('emails.id'))
    filename = Column(String)
    mime_type = Column(String)
    size = Column(Integer)

# Initialize database
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)