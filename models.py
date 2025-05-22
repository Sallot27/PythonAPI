from sqlalchemy import Table, Column, Integer, String, ForeignKey
from database import metadata

applications = Table(
    "applications", metadata,
    Column("id", Integer, primary_key=True),
    Column("reference_number", String),
)

images = Table(
    "images", metadata,
    Column("id", Integer, primary_key=True),
    Column("application_id", Integer, ForeignKey("applications.id")),
    Column("car_side", String),
    Column("file_path", String),
)
