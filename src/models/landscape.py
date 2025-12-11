from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text, Table, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from ..database import Base
import enum
from datetime import datetime

# Enums for various classifications

class CountryCode(str, enum.Enum):
    DE = "DE"
    NL = "NL"

class LandUseCategory(str, enum.Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"
    FOREST = "forest"
    WATER = "water"
    TRANSPORT = "transport"
    RECREATION = "recreation"
    PROTECTED = "protected"
    OTHER = "other"

class ProtectionCategory(str, enum.Enum):
    NATURA2000 = "natura_2000"
    NATURE_RESERVE = "nature_reserve"
    LANDSCAPE_PROTECTION = "landscape_protection"
    WATER_PROTECTION = "water_protection"
    FOREST_PROTECTION = "forest_protection"
    CULTURAL_HERITAGE = "cultural_heritage"

# Association tables for many-to-many relationships

parcel_land_use = Table(
    'parcel_land_use', Base.metadata,
    Column('parcel_id', Integer, ForeignKey('parcels.id')),
    Column('land_use_id', Integer, ForeignKey('land_use_categories.id')),
    Column('valid_from', DateTime, default=datetime.utcnow),
    Column('valid_to', DateTime, nullable=True)
)

enterprise_branches = Table(
    'enterprise_branches', Base.metadata,
    Column('enterprise_id', Integer, ForeignKey('enterprises.id')),
    Column('nace_code', String, ForeignKey('nace_categories.code')),
    Column('is_primary', Boolean, default=False)
)

# Base model with common fields
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100))
    updated_by = Column(String(100))

# Main entity models

class AdministrativeArea(Base, TimestampMixin):
    """Administrative areas like countries, states, municipalities"""
    __tablename__ = 'administrative_areas'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    level = Column(Integer)  # 0=country, 1=state, 2=district, 3=municipality, etc.
    country = Column(Enum(CountryCode))
    parent_id = Column(Integer, ForeignKey('administrative_areas.id'))
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    # Relationships
    parent = relationship('AdministrativeArea', remote_side=[id], backref='children')
    
    __table_args__ = (
        Index('idx_administrative_areas_geometry', geometry, postgresql_using='gist'),
    )

class Parcel(Base, TimestampMixin):
    """Land parcels/cadastral units"""
    __tablename__ = 'parcels'
    
    id = Column(Integer, primary_key=True)
    parcel_number = Column(String(50), nullable=False)
    area_m2 = Column(Float)
    municipality_id = Column(Integer, ForeignKey('administrative_areas.id'))
    country = Column(Enum(CountryCode))
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    # Relationships
    municipality = relationship('AdministrativeArea')
    land_uses = relationship('LandUseCategory', secondary=parcel_land_use, back_populates='parcels')
    
    __table_args__ = (
        Index('idx_parcels_geometry', geometry, postgresql_using='gist'),
        Index('idx_parcels_parcel_number', 'parcel_number'),
    )

class LandUseCategory(Base, TimestampMixin):
    """Categories of land use"""
    __tablename__ = 'land_use_categories'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(Enum(LandUseCategory))
    
    # Relationships
    parcels = relationship('Parcel', secondary=parcel_land_use, back_populates='land_uses')

class ProtectedArea(Base, TimestampMixin):
    """Protected areas like nature reserves, Natura 2000 sites, etc."""
    __tablename__ = 'protected_areas'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    designation = Column(Enum(ProtectionCategory))
    legal_status = Column(String(100))
    protection_level = Column(String(50))
    area_m2 = Column(Float)
    established_date = Column(DateTime)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    __table_args__ = (
        Index('idx_protected_areas_geometry', geometry, postgresql_using='gist'),
    )

class Enterprise(Base, TimestampMixin):
    """Businesses and organizations"""
    __tablename__ = 'enterprises'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(200))
    postal_code = Column(String(20))
    city = Column(String(100))
    country = Column(Enum(CountryCode))
    website = Column(String(200))
    email = Column(String(100))
    phone = Column(String(50))
    employees_min = Column(Integer)
    employees_max = Column(Integer)
    founded_year = Column(Integer)
    geometry = Column(Geometry('POINT', srid=4326))
    data_source = Column(String(100))
    source_id = Column(String(100))
    
    # Relationships
    branches = relationship('NACECategory', secondary=enterprise_branches, back_populates='enterprises')
    
    __table_args__ = (
        Index('idx_enterprises_geometry', geometry, postgresql_using='gist'),
    )

class NACECategory(Base, TimestampMixin):
    """NACE classification for economic activities"""
    __tablename__ = 'nace_categories'
    
    code = Column(String(10), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Relationships
    enterprises = relationship('Enterprise', secondary=enterprise_branches, back_populates='branches')

class Infrastructure(Base, TimestampMixin):
    """Transportation and utility infrastructure"""
    __tablename__ = 'infrastructure'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    type = Column(String(50))  # road, railway, waterway, power_line, etc.
    subtype = Column(String(50))  # highway, primary, secondary, etc.
    status = Column(String(50))
    geometry = Column(Geometry('GEOMETRY', srid=4326))  # Can be LINESTRING or POINT
    
    __table_args__ = (
        Index('idx_infrastructure_geometry', geometry, postgresql_using='gist'),
    )

class PlanningDocument(Base, TimestampMixin):
    """Spatial planning documents and regulations"""
    __tablename__ = 'planning_documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    document_type = Column(String(100))  # B-Plan, Flächennutzungsplan, etc.
    document_number = Column(String(50))
    status = Column(String(50))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime, nullable=True)
    document_url = Column(String(500))
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    
    __table_args__ = (
        Index('idx_planning_documents_geometry', geometry, postgresql_using='gist'),
    )

class EnvironmentalData(Base, TimestampMixin):
    """Environmental measurements and indicators"""
    __tablename__ = 'environmental_data'
    
    id = Column(Integer, primary_key=True)
    parameter = Column(String(100), nullable=False)  # temperature, precipitation, air_quality, etc.
    value = Column(Float)
    unit = Column(String(20))
    date = Column(DateTime)
    source = Column(String(200))
    geometry = Column(Geometry('POINT', srid=4326))
    
    __table_args__ = (
        Index('idx_environmental_data_geometry', geometry, postgresql_using='gist'),
        Index('idx_environmental_data_parameter', 'parameter'),
    )

# Additional models for specific data types can be added as needed
# For example: Building, WaterBody, AgriculturalParcel, etc.
