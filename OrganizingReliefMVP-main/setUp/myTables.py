from sqlalchemy import Column, Integer,  UUID, String, ForeignKey, DateTime, Float
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Orgs(Base):
    __tablename__ = 'organizations'
    orgName = Column(String, primary_key=True)
    orgPin = Column(Integer, nullable=False)

class User(Base):
    __tablename__ = 'user_table'
    email = Column(String, primary_key=True)
    children = relationship("EmergencyCall", back_populates="parent")
    children2 = relationship("Chats", back_populates="parent")
    children3 = relationship("MunicipalityChats", back_populates="parent")
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    orgName = Column(String, nullable=False)

class EmergencyCall(Base):
    __tablename__ = 'emergencyCalls_table'
    callId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    urgency = Column(Integer, nullable=False)
    emergencyDescription = Column(String, nullable=False)
    municipality = Column(String, nullable=False)
    extendedLocationInfo = Column(String, nullable=True)
    date_time_called = Column(DateTime, nullable=False)
    user_email = Column(String, ForeignKey('user_table.email'))
    parent = relationship("User", back_populates="children")
    status = Column(String, nullable=False)
    lastUpdated = Column(DateTime, nullable=False)
    responses = relationship("EmergencyCallsResponses", back_populates='parent_call')

class EmergencyCallsResponses(Base):
    __tablename__ = 'emergencyCallRespoonses_table'
    resId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    callId = Column(UUID(as_uuid=True), ForeignKey("emergencyCalls_table.callId"), nullable=False)
    date_time_responded = Column(DateTime, nullable=False)
    urgency = Column(Integer, nullable=False)
    resolution = Column(String, nullable=False)
    emergencyDescription = Column(String, nullable=False)
    location = Column(String, nullable=False)
    messageToCaller = Column(String, nullable=False)
    damages = Column(String, nullable=True)
    resources = Column(String, nullable=True)
    colabOrg = Column(String, nullable=True)
    parent_call = relationship("EmergencyCall", back_populates="responses")

class Hubs(Base):
    __tablename__ = 'aidHubs_table'
    mainProvider = Column(String, ForeignKey('user_table.email'), primary_key=True)
    municipality = Column(String, nullable=False)
    zipcode = Column(String, nullable=False)
    city = Column(String, nullable=False)
    streetAddr = Column(String, nullable=False)
    aidDescription = Column(String, nullable=False)
    currCapacity = Column(Integer, nullable=True)

class MunicipalityUrgency(Base):
    __tablename__ = 'munUrgency_table'
    municipality = Column(String, primary_key=True)
    urgency_rating = Column(Float, nullable=False)

class Chats(Base):
    __tablename__ = 'chats_table'
    chat = Column(String, nullable=False)
    resId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String, ForeignKey('user_table.email'))
    parent = relationship("User", back_populates="children2")
    date_time = Column(DateTime, nullable=False)

class MunicipalityChats(Base):
    __tablename__ = 'munchats_table'
    chat = Column(String, nullable=False)
    resId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String, ForeignKey('user_table.email'))
    parent = relationship("User", back_populates="children3")
    date_time = Column(DateTime, nullable=False)
    municipality = Column(String, nullable=False)



db_url = 'postgresql://postgres:Montegod111!!!@localhost:5432/OrganizingReliefeSignUp'
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)
