


from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base


# =========================================================
# AREA
# =========================================================

class AreaModel(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # doc_no = Column(String, nullable=False, unique=True) #Before
    doc_no = Column(String, nullable=False, ) # Must be
    doc_rev = Column(String, nullable=False)
    say_iso_no = Column(String, nullable=False)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint("name", "project_id"),
    )

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"{self.description} "
            f"{self.say_iso_no} "
            f"{self.doc_rev} "
            f"{self.doc_no}"
        )


# =========================================================
# LOCATION
# =========================================================

class LocationModel(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint("name", "project_id"),
    )

    def __str__(self) -> str:
        return f"{self.name} {self.project_id}"


# =========================================================
# UOM
# =========================================================

class UomModel(Base):
    __tablename__ = "uoms"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


# =========================================================
# STOCK DATA
# =========================================================

class StockDataModel(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True)

    stock_code = Column(String, nullable=False, unique=True)

    alternative_id = Column(String, nullable=True)
    old_code = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    type_id = Column(
        Integer,
        ForeignKey("types.id"),
        nullable=False,
        index=True
    )

    uom_id = Column(
        Integer,
        ForeignKey("uoms.id"),
        nullable=False,
        index=True
    )

    item_type = relationship(
        "TypeModel",
        backref="stock_datas"
    )

    uom = relationship(
        "UomModel",
        backref="stock_datas"
    )

    def __str__(self) -> str:
        return (
            f"{self.stock_code} "
            f"{self.old_code} "
            f"{self.comment}"
        )


# =========================================================
# SUBTYPE
# =========================================================

class SubTypeModel(Base):
    __tablename__ = "subtypes"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# SIZE 1
# =========================================================

class Size1Model(Base):
    __tablename__ = "size_1"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# SIZE 2
# =========================================================

class Size2Model(Base):
    __tablename__ = "size_2"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# MATERIAL
# =========================================================

class MaterialModel(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# DESCRIPTION
# =========================================================

class DescriptionModel(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# ITEM TYPES
# =========================================================

class TypesModel(Base):
    __tablename__ = "item_types"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"{self.name}"


# =========================================================
# TYPES
# =========================================================

class TypeModel(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True)

    type_id = Column(
        Integer,
        ForeignKey("item_types.id"),
        nullable=False,
        index=True
    )

    subtype_id = Column(
        Integer,
        ForeignKey("subtypes.id"),
        nullable=False,
        index=True
    )

    size1_id = Column(
        Integer,
        ForeignKey("size_1.id"),
        nullable=False,
        index=True
    )

    size2_id = Column(
        Integer,
        ForeignKey("size_2.id"),
        nullable=True,
        index=True
    )

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=False,
        index=True
    )

    description_id = Column(
        Integer,
        ForeignKey("descriptions.id"),
        nullable=False,
        index=True
    )

    thickness_1 = Column(String, nullable=True)
    thickness_2 = Column(String, nullable=True)

    # Relationships
    type = relationship("TypesModel")
    subtype = relationship("SubTypeModel")
    size1 = relationship("Size1Model")
    size2 = relationship("Size2Model")
    material = relationship("MaterialModel")
    description = relationship("DescriptionModel")


# =========================================================
# STATUS
# =========================================================




























#
#
#
# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
#
# from db.base import Base
#
#
# class AreaModel(Base):
#     __tablename__ = "areas"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#     description = Column(String, nullable=False)
#
#     doc_no = Column(String, nullable=False, unique=True)
#     doc_rev = Column(String, nullable=False) # new added
#     say_iso_no = Column(String, nullable=False) # new added
#
#     project_id = Column(
#         Integer,
#         ForeignKey("projects.id"),
#         nullable=False,
#         index=True
#     )
#
#     def __str__(self) -> str:
#         return f"{self.name} {self.description} {self.say_iso_no} {self.doc_rev} {self.doc_no}"
#
#
# class LocationModel(Base):
#     __tablename__ = "locations"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#
#     project_id = Column(
#         Integer,
#         ForeignKey("projects.id"),
#         nullable=False,
#         index=True
#     )
#
#     def __str__(self) -> str:
#         return f"{self.name} {self.project_id}"
#
# class UomModel(Base):
#     __tablename__ = "uoms"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self) -> str:
#         return f"{self.name}"
#
#
# class StockDataModel(Base):
#     __tablename__ = "stock_data"
#     id = Column(Integer, primary_key=True)
#
#     stock_code = Column(String, nullable=False, unique=True)
#     alternative_id = Column(String, nullable=True)
#     old_code = Column(String, nullable=True)
#     comment = Column(String, nullable=True)
#     type_id = Column(Integer, ForeignKey("types.id"), nullable=False)
#     uom_id = Column(Integer, ForeignKey("uoms.id"), nullable=False)
#
#     type = relationship("TypeModel", backref="stock_datas")
#     uom = relationship("UomModel", backref="stock_datas")
#
#     def __str__(self) -> str:
#         return f"{self.type} {self.uom} {self.stock_code} {self.old_code} {self.comment} {self.type_id}"
#
#
#
# class SubTypeModel(Base):
#     __tablename__ = "subtypes"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# class Size1Model(Base):
#     __tablename__ = "size_1"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# class Size2Model(Base):
#     __tablename__ = "size_2"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# class MaterialModel(Base):
#     __tablename__ = "materials"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# class DescriptionModel(Base):
#     __tablename__ = "descriptions"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#
#     def __str__(self):
#         return f"{self.name}"
#
# class TypesModel(Base):
#     __tablename__ = "item_types"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#
#     def __str__(self):
#         return f"{self.name}"
#
#
# class TypeModel(Base):
#     __tablename__ = "types"
#     id = Column(Integer, primary_key=True)
#     type_id = Column(Integer, ForeignKey("item_types.id"), nullable=False) # new added
#     subtype_id = Column(Integer, ForeignKey("subtypes.id"), nullable=False)
#     size1_id = Column(Integer, ForeignKey("size_1.id"), nullable=False)
#     size2_id = Column(Integer, ForeignKey("size_2.id"), nullable=True)
#     material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
#     description_id = Column(Integer, ForeignKey("descriptions.id"), nullable=False)
#     thickness_1 = Column(String, nullable=True)
#     thickness_2 = Column(String, nullable=True)
#
#     # Relationships
#     type = relationship("TypesModel") #new added
#     subtype = relationship("SubTypeModel")
#     size1 = relationship("Size1Model")
#     size2 = relationship("Size2Model")
#     material = relationship("MaterialModel")
#     description = relationship("DescriptionModel")
#
#
#
#
