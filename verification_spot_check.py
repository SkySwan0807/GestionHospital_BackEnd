from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from pharmacy.database import Base
from pharmacy.medications.model import Medication
from pharmacy.medications.category_model import TherapeuticCategory
from decimal import Decimal

# Setup in-memory database
engine = create_engine('sqlite:///:memory:',
                       connect_args={'check_same_thread': False})

# Ensure SQLite enforces foreign keys
@event.listens_for(engine, 'connect')
def set_pragma(conn, _):
    conn.cursor().execute('PRAGMA foreign_keys=ON')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# Test Case 1: Successful insertion
m1 = Medication(name='Aspirin', generic_name='ASA',
                dosage='100mg', price=Decimal('1.50'))
db.add(m1); db.commit()
print('INSERT 1: OK')

# Test Case 2: UNIQUE constraint check (Should fail commit)
try:
    m2 = Medication(name='Aspirin', generic_name='ASA',
                    dosage='200mg', price=Decimal('2.00'))
    db.add(m2); db.commit()
    print('FAIL: UNIQUE constraint not working')
except Exception as e:
    db.rollback()
    print(f'UNIQUE constraint: OK — {type(e).__name__} raised as expected')

# Test Case 3: Defaults check
db.refresh(m1)
assert m1.stock_quantity == 0
assert m1.is_active is True
assert m1.created_at is not None
print('Defaults: OK')
print('All spot checks passed.')
