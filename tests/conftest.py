"""
conftest.py — Shared pytest fixtures สำหรับ tests ทั้งหมด
แยก setup ออกจาก test_models.py ให้สามารถ reuse ได้ทุก module
"""

import pytest
from peewee import SqliteDatabase
from core.models import Friend, Bill, BillItem, BillParticipant


# ใช้ in-memory SQLite เพื่อไม่ให้กระทบ DB จริง
_TEST_DB = SqliteDatabase(":memory:")
_MODELS = [Friend, Bill, BillItem, BillParticipant]


@pytest.fixture(scope="function")
def test_db():
    """
    Fixture สร้าง in-memory DB สด ๆ ต่อ 1 test function
    — bind → create tables → yield → drop tables → close
    """
    _TEST_DB.bind(_MODELS, bind_refs=False, bind_backrefs=False)
    _TEST_DB.connect()
    _TEST_DB.create_tables(_MODELS)
    yield _TEST_DB
    _TEST_DB.drop_tables(_MODELS)
    _TEST_DB.close()


@pytest.fixture(scope="function")
def sample_bill(test_db):
    """Fixture สร้างบิลตัวอย่างพร้อม 2 รายการและ 2 ผู้เข้าร่วม"""
    bill = Bill.create(title="Test Dinner", total=500.0)
    BillItem.create(bill=bill, name="Sushi", price=300.0, quantity=1)
    BillItem.create(bill=bill, name="Beer", price=200.0, quantity=2)
    BillParticipant.create(
        bill=bill, display_name="Me", amount_owed=250.0, is_paid=True
    )
    BillParticipant.create(
        bill=bill, display_name="Alice", amount_owed=250.0, is_paid=False
    )
    return bill


@pytest.fixture(scope="function")
def sample_friend(test_db):
    """Fixture สร้างเพื่อนตัวอย่าง"""
    return Friend.create(name="Somchai", nickname="Chai")
