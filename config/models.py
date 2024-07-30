from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import  declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(String, primary_key=True)
    from_mail = Column(String)
    to_mail = Column(String)
    subject = Column(String)
    date = Column(DateTime)
    message = Column(String)