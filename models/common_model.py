


from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base


class AreaModel(Base):
    __tablename__ = "area"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    def __str__(self) -> str:
        return self.name + " (" + self.description + ")"


class LocationModel(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    def __str__(self) -> str:
        return self.name + " (" + self.project_id + ")"

class UomModel(Base):
    __tablename__ = "uom"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __str__(self) -> str:
        return self.name


class TypeModel(Base):
    __tablename__ = "type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sub_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    material = Column(String, nullable=False)
    size_1 = Column(String, nullable=False)
    size_2 = Column(String, nullable=True)
    thickness_1 = Column(String, nullable=True)
    thickness_2 = Column(String, nullable=True)

class StockDataModel(Base):
    __tablename__ = "stock_data"
    id = Column(Integer, primary_key=True)

    stock_code = Column(String, nullable=False)
    alternative_id = Column(String, nullable=True)
    old_code = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    type_id = Column(Integer, ForeignKey("type.id"), nullable=False)
    uom_id = Column(Integer, ForeignKey("uom.id"), nullable=False)
