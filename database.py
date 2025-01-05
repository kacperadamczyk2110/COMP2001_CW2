from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey
from urllib.parse import quote_plus

# Database configuration
#-------------------------
db_server = 'DIST-6-505.uopnet.plymouth.ac.uk'
db_name = 'COMP2001_KAdamczyk'
db_username = 'KAdamczyk'
db_password = 'SvlZ432+'
connection_string = f'mssql+pyodbc://{db_username}:{quote_plus(db_password)}@{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'

# Create database engine
#-------------------------
engine = create_engine(connection_string)
metadata = MetaData()

# Define Users table globally
#----------------------------
users_table = Table(
    'APP_USER', metadata,
    Column('UserID', Integer, primary_key=True),
    Column('Email_address', String(255), nullable=False),
    Column('Role', String(50), nullable=False),
    schema='CW2'
)

# Define Trails table
#-------------------------
trails_table = Table(
    'TRAIL', metadata,
    Column('TrailID', Integer, primary_key=True),
    Column('TrailName', String(255), nullable=False),
    Column('TrailSummary', String(255)),
    Column('TrailDescription', String(255)),
    Column('Difficulty', String(50)),
    Column('Location', String(255)),
    Column('Length', Float),
    Column('ElevationGain', Float),
    Column('RouteType', String(50)),
    Column('OwnerID', Integer, ForeignKey('CW2.APP_USER.UserID')),
    Column('Pt1_Lat', Float),
    Column('Pt1_Long', Float),
    Column('Pt1_Desc', String(255)),
    Column('Pt2_Lat', Float),
    Column('Pt2_Long', Float),
    Column('Pt2_Desc', String(255)),
    schema='CW2'
)

# Define Features table
#-------------------------
features_table = Table(
    'FEATURE', metadata,
    Column('TrailFeatureID', Integer, primary_key=True),
    Column('TrailFeature', String(255), nullable=False),
    schema='CW2'
)

# Define Trail Features table
#-------------------------
trail_feature_table = Table(
    'TRAIL_FEATURE', metadata,
    Column('TrailID', Integer, ForeignKey('CW2.TRAIL.TrailID'), primary_key=True),
    Column('TrailFeatureID', Integer, ForeignKey('CW2.FEATURE.TrailFeatureID'), primary_key=True),
    schema='CW2'
)
