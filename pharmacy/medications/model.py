"""
pharmacy/medications/model.py
─────────────────────────────────────────────────────────────────
Pure data-mapping layer.  No business logic, no validation rules.
All constraint semantics live here; behavioural rules live in
service.py.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from pharmacy.database import Base


class Medication(Base):
    __tablename__ = "medications"

    # ── Composite unique constraint ───────────────────────────────
    # (name, generic_name) together must be unique so that the same
    # brand name can exist for different active ingredients, but no
    # two rows may represent an identical drug identity.
    __table_args__ = (
        UniqueConstraint("name", "generic_name", name="uq_medication_name_generic"),
    )

    # ── Primary key ───────────────────────────────────────────────
    # Integer autoincrement preferred over UUID for SQLite:
    #   • native ROWID alias → zero-cost index
    #   • compact FK references in future child tables
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # ── Core identity fields ──────────────────────────────────────
    # Mapped from: inventory.item_name → name (semantic rename)
    name = Column(
        String(200),
        nullable=False,
        index=True,  # Frequent search target; prevents full-table scans
        comment="Brand / trade name of the medication",
    )

    # New field — not in inventory; required to distinguish
    # medications that share a brand name across formulations.
    generic_name = Column(
        String(200),
        nullable=False,
        comment="INN / generic (active ingredient) name",
    )

    # ── Dosage & packaging ────────────────────────────────────────
    dosage = Column(
        String(100),
        nullable=False,
        comment="Strength description, e.g. '500 mg', '10 mg/5 ml'",
    )

    # Mapped from: inventory.unit → unit (direct carry-over)
    # Kept nullable: not all medications use a distinct dispensing unit.
    unit = Column(
        String(20),
        nullable=True,
        comment="Dispensing unit, e.g. 'tablet', 'capsule', 'ml'",
    )

    description = Column(
        String(500),
        nullable=True,
        comment="Optional free-text clinical notes or storage instructions",
    )

    # ── Pricing ───────────────────────────────────────────────────
    # Numeric(10, 2) maps to SQLite NUMERIC affinity (stored as text-
    # encoded decimal) to avoid IEEE 754 rounding errors in Float.
    price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Unit selling price. Use Numeric, not Float, for currency.",
    )

    # ── Inventory stock ───────────────────────────────────────────
    # Mapped from: inventory.quantity → stock_quantity (semantic rename)
    stock_quantity = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Current on-hand quantity. Adjusted via stock_adjustments events.",
    )

    # Alert threshold — triggers low-stock warnings in a future
    # notification module.  Kept here (not purchase_orders) because
    # it describes an intrinsic property of the medication, not a
    # procurement decision.
    min_stock_threshold = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Reorder alert level. 0 = no alerting configured.",
    )

    # ── Catalogue / classification ────────────────────────────────
    # FK to therapeutic_categories catalog table.
    # Nullable so drugs can be added before the catalog is populated.
    therapeutic_category_id = Column(
        Integer,
        ForeignKey("therapeutic_categories.id"),
        nullable=True,
        index=True,  # JOIN target from dispensations / prescriptions
        comment="FK → therapeutic_categories.id",
    )

    # ── Lifecycle fields ──────────────────────────────────────────
    expiration_date = Column(
        Date,
        nullable=True,
        comment="Batch expiration date. Null for non-expiring consumables.",
    )

    # Boolean stored as INTEGER 0/1 in SQLite (type affinity).
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Soft-delete flag. Inactive medications are hidden from orders.",
    )

    # ── Audit timestamps ──────────────────────────────────────────
    # server_default=func.now() → DB sets value on INSERT via SQL.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Row creation timestamp (DB-generated).",
    )

    # SQLite has no native ON UPDATE trigger for columns.
    # A lambda returning datetime.now(timezone.utc) is used instead of
    # the deprecated datetime.utcnow (removed-warning in Python 3.12+).
    # SQLAlchemy calls this callable on every ORM UPDATE statement.
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),  # timezone-aware, Python 3.12+ safe
        comment="Last modification timestamp (Python-ORM managed).",
    )

    # ── Debug representation ──────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"<Medication("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"generic_name={self.generic_name!r}, "
            f"dosage={self.dosage!r}, "
            f"stock={self.stock_quantity!r}, "
            f"active={self.is_active!r}"
            f")>"
        )

