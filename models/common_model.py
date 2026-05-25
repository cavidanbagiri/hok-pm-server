


from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint, Float, Index
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
# MTO ALL
# =========================================================

class MtoModel(Base):
    __tablename__ = "mtos"

    id = Column(Integer, primary_key=True)

    # Excel columns
    no = Column(String, nullable=False)
    reference_mto = Column(String, nullable=False)
    mto_date = Column(DateTime, nullable=True)
    pid_no = Column(String, nullable=True)
    line_no = Column(String, nullable=True)
    isometric_drawing_no = Column(String, nullable=True)
    iso_rev = Column(String, nullable=True)
    iso_and_rev = Column(String, nullable=True)
    spec = Column(String, nullable=True)
    quantity = Column(Float, nullable=False)
    required_area = Column(Float, nullable=True)
    required_iso = Column(Float, nullable=True)
    comment = Column(String, nullable=True)

    # Foreign Keys
    location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False,
        index=True
    )

    area_id = Column(
        Integer,
        ForeignKey("areas.id"),
        nullable=False,
        index=True
    )

    area_2_id = Column(
        Integer,
        ForeignKey("areas.id"),
        nullable=True,
        index=True
    )

    area_2_desc_id = Column(
        Integer,
        ForeignKey("descriptions.id"),
        nullable=True,
        index=True
    )

    stock_data_id = Column(
        Integer,
        ForeignKey("stock_data.id"),
        nullable=False,
        index=True
    )

    uom_id = Column(
        Integer,
        ForeignKey("uoms.id"),
        nullable=False,
        index=True
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    # Relationships
    location = relationship("LocationModel", foreign_keys=[location_id])
    area = relationship("AreaModel", foreign_keys=[area_id])
    area_2 = relationship("AreaModel", foreign_keys=[area_2_id])
    area_2_desc = relationship("DescriptionModel", foreign_keys=[area_2_desc_id])
    stock_data = relationship("StockDataModel", foreign_keys=[stock_data_id])
    uom = relationship("UomModel", foreign_keys=[uom_id])
    created_by = relationship("UserModel", foreign_keys=[created_by_id])

    # Computed property (not stored in database)
    @property
    def iso_stock_kod(self):
        """Computed field: ISOMETRIC_DRAWING_NO + STOCK_CODE"""
        if self.isometric_drawing_no and self.stock_data:
            return f"{self.isometric_drawing_no}{self.stock_data.stock_code}"
        return None

    # Unique constraint
    __table_args__ = (
        # Unique constraint on computed field (requires special handling)
        # Since iso_stock_kod is computed, we'll handle uniqueness in application logic
        # Or add a stored column if needed for database-level constraint
        Index('idx_mto_reference', 'reference_mto', 'no', 'line_no'),
        Index('idx_mto_stock_data', 'stock_data_id'),
        Index('idx_mto_date', 'mto_date'),
    )

    def __str__(self) -> str:
        return f"MTO {self.reference_mto} - {self.no} - {self.line_no}"
















