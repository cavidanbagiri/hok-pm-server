


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


class StockDataModel(Base):
    __tablename__ = "stock_data"
    id = Column(Integer, primary_key=True)

    stock_code = Column(String, nullable=False)
    alternative_id = Column(String, nullable=True)
    old_code = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    type_id = Column(Integer, ForeignKey("type.id"), nullable=False)
    uom_id = Column(Integer, ForeignKey("uom.id"), nullable=False)


class SubTypeModel(Base):
    __tablename__ = "subtype"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return self.name


class Size1Model(Base):
    __tablename__ = "size_1"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return self.name


class Size2Model(Base):
    __tablename__ = "size_2"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return self.name


class MaterialModel(Base):
    __tablename__ = "material"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return self.name


class DescriptionModel(Base):
    __tablename__ = "description"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return self.name


class TypeModel(Base):
    __tablename__ = "type"
    id = Column(Integer, primary_key=True)
    subtype_id = Column(Integer, ForeignKey("subtype.id"), nullable=False)
    size1_id = Column(Integer, ForeignKey("size_1.id"), nullable=False)
    size2_id = Column(Integer, ForeignKey("size_2.id"), nullable=True)
    material_id = Column(Integer, ForeignKey("material.id"), nullable=False)
    description_id = Column(Integer, ForeignKey("description.id"), nullable=False)
    thickness_1 = Column(String, nullable=True)
    thickness_2 = Column(String, nullable=True)

    # Relationships
    subtype = relationship("SubTypeModel")
    size1 = relationship("Size1Model")
    size2 = relationship("Size2Model")
    material = relationship("MaterialModel")
    description = relationship("DescriptionModel")