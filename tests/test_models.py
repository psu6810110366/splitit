import pytest
from peewee import SqliteDatabase
from core.models import Friend, Bill, BillItem, BillParticipant

# ใช้ in-memory database สำหรับ test จะได้ไม่พัง DB จริง
db_conn = SqliteDatabase(":memory:")


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
    Friend.create(name="Somchai", nickname="Chai")
    saved = Friend.get(Friend.name == "Somchai")
    assert saved.nickname == "Chai"
    assert saved.avatar_color.startswith("#")


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


# ── BillParticipant edge case tests ──────────────────────────────────────────


def test_bill_participant_default_not_paid():
    """BillParticipant ค่าเริ่มต้น is_paid ต้องเป็น False"""
    bill = Bill.create(title="Test", total=100.0)
    p = BillParticipant.create(bill=bill, display_name="Alice", amount_owed=100.0)
    assert p.is_paid is False


def test_bill_participant_default_amount_zero():
    """BillParticipant ค่าเริ่มต้น amount_owed ต้องเป็น 0.0"""
    bill = Bill.create(title="Test", total=0.0)
    p = BillParticipant.create(bill=bill, display_name="Bob")
    assert p.amount_owed == 0.0


def test_bill_participant_update_paid():
    """อัปเดต is_paid → True ต้องบันทึกลง DB"""
    bill = Bill.create(title="Lunch", total=200.0)
    p = BillParticipant.create(bill=bill, display_name="Carol", amount_owed=200.0)
    p.is_paid = True
    p.save()
    refetched = BillParticipant.get_by_id(p.id)
    assert refetched.is_paid is True


def test_cascade_delete_removes_participants():
    """ลบบิล → BillParticipant ต้องหายไปด้วย"""
    bill = Bill.create(title="Party", total=500.0)
    BillParticipant.create(bill=bill, display_name="Alice", amount_owed=250.0)
    BillParticipant.create(bill=bill, display_name="Bob", amount_owed=250.0)
    bill.delete_instance(recursive=True)
    assert BillParticipant.select().count() == 0


def test_multiple_bills_independent():
    """หลายบิลต้องไม่ปนกัน"""
    b1 = Bill.create(title="Bill1", total=100.0)
    b2 = Bill.create(title="Bill2", total=200.0)
    BillItem.create(bill=b1, name="A", price=100.0)
    BillItem.create(bill=b2, name="B", price=100.0)
    BillItem.create(bill=b2, name="C", price=100.0)
    assert b1.items.count() == 1
    assert b2.items.count() == 2


def test_friend_avatar_color_is_hex():
    """avatar_color ต้องเป็น hex string ขึ้นต้นด้วย '#'"""
    f = Friend.create(name="Nook")
    assert f.avatar_color.startswith("#")
    assert len(f.avatar_color) == 7  # #RRGGBB


def test_bill_default_not_done():
    """Bill ใหม่ต้องมี is_done=False เป็นค่า default"""
    bill = Bill.create(title="Fresh Bill", total=0.0)
    assert bill.is_done is False


def test_bill_item_quantity_default():
    """BillItem ต้องมี quantity=1 เป็นค่า default"""
    bill = Bill.create(title="Quick", total=50.0)
    item = BillItem.create(bill=bill, name="Coffee", price=50.0)
    assert item.quantity == 1
