import pytest
from peewee import SqliteDatabase
from core.models import Friend, Bill, BillItem, BillParticipant

# ใช้ in-memory database สำหรับ test จะได้ไม่พัง DB จริง
db_conn = SqliteDatabase(':memory:')

@pytest.fixture(autouse=True)
def setup_test_db():
    # ผูกฐานข้อมูลชั่วคราวเข้ากับ Models
    models = [Friend, Bill, BillItem, BillParticipant]
    db_conn.bind(models, bind_refs=False, bind_backrefs=False)
    db_conn.connect()
    db_conn.create_tables(models)
    yield
    db_conn.drop_tables(models)
    db_conn.close()

def test_create_friend():
    # ทดสอบสร้างเพื่อนและเช็คว่าเซฟลง DB จริงไหม
    f = Friend.create(name="Somchai", nickname="Chai")
    saved = Friend.get(Friend.name == "Somchai")
    assert saved.nickname == "Chai"
    assert saved.avatar_color.startswith('#')

def test_bill_and_items():
    # ทดสอบสร้างบิลและรายการอาหาร
    bill = Bill.create(title="Dinner", total=500.0)
    BillItem.create(bill=bill, name="Sushi", price=300.0)
    BillItem.create(bill=bill, name="Beer", price=200.0)
    
    assert bill.items.count() == 2
    assert sum(item.price for item in bill.items) == 500.0

def test_cascade_delete():
    # เช็คว่าถ้าลบบิล รายการในบิลต้องหายไปด้วย (Cascading)
    bill = Bill.create(title="Going to be deleted", total=100)
    BillItem.create(bill=bill, name="Item", price=100)
    
    bill.delete_instance(recursive=True)
    assert BillItem.select().count() == 0
