"""
test_storage.py — Unit tests สำหรับ storage layer (core/storage.py)

API ของ save_bill มี 2 รูปแบบ:
  1. save_bill(title: str, total: float, items: list, breakdown: dict)
  2. save_bill(bill_data: dict, participants: list, items: list)
"""

import os
import pytest
import tempfile
from peewee import SqliteDatabase
from core.models import Friend, Bill, BillItem, BillParticipant
import core.storage as st
import core.models as md

_MODELS = [Friend, Bill, BillItem, BillParticipant]


@pytest.fixture(autouse=True)
def isolated_db():
    """ใช้ SQLite temp-file DB แทน splitit.db จริง"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = SqliteDatabase(path)
    db.bind(_MODELS, bind_refs=False, bind_backrefs=False)
    db.connect()
    db.create_tables(_MODELS)

    orig_st_db = st.db
    orig_md_db = md.db
    st.db = db
    md.db = db

    yield db

    st.db = orig_st_db
    md.db = orig_md_db
    db.drop_tables(_MODELS)
    db.close()
    os.unlink(path)


# ── helpers ────────────────────────────────────────────────────────────────────


def _save_str(title, total, breakdown: dict, items: list = None):
    """รูปแบบ string path: save_bill(title, total, items, breakdown)"""
    return st.save_bill(title, total, items or [], breakdown)


def _save_dict(title, total, participants: list, items: list = None):
    """รูปแบบ dict path: save_bill(bill_dict, participants, items)"""
    bill_data = {"title": title, "total": total, "notes": "", "promptpay": ""}
    return st.save_bill(bill_data, participants, items or [])


# ── save_bill (string path) tests ──────────────────────────────────────────────


class TestSaveBillStringPath:
    def test_returns_positive_id(self):
        """save_bill() ต้องคืน id > 0"""
        bid = _save_str("Dinner", 300.0, {"Alice": 150.0, "Bob": 150.0})
        assert bid > 0

    def test_creates_bill_record(self):
        """บิลต้องถูก insert ลง DB"""
        _save_str("Lunch", 200.0, {"A": 200.0})
        assert Bill.select().count() == 1
        assert Bill.get().title == "Lunch"

    def test_creates_participants_from_breakdown(self):
        """breakdown dict ต้องสร้าง BillParticipant ครบ"""
        _save_str("BBQ", 400.0, {"Alice": 200.0, "Bob": 200.0})
        assert BillParticipant.select().count() == 2

    def test_me_auto_marked_paid(self):
        """ชื่อ 'Me' ต้องถูก mark is_paid=True อัตโนมัติ"""
        _save_str("Party", 300.0, {"Me": 150.0, "Alice": 150.0})
        me = BillParticipant.get(BillParticipant.display_name == "Me")
        alice = BillParticipant.get(BillParticipant.display_name == "Alice")
        assert me.is_paid is True
        assert alice.is_paid is False

    def test_creates_bill_items(self):
        """items ที่ส่งมาต้องถูกสร้างใน BillItem"""
        _save_str(
            "Shabu",
            200.0,
            {"Me": 200.0},
            items=[
                {"name": "Pork", "price": 120.0, "quantity": 1},
                {"name": "Veg", "price": 80.0, "quantity": 2},
            ],
        )
        assert BillItem.select().count() == 2


# ── save_bill (dict path) tests ────────────────────────────────────────────────


class TestSaveBillDictPath:
    def test_creates_bill_from_dict(self):
        """dict path ต้องสร้างบิลด้วย title และ total ถูกต้อง"""
        bid = _save_dict(
            "Hotpot",
            600.0,
            [
                {"name": "Me", "amount": 300.0, "is_paid": True},
                {"name": "Bob", "amount": 300.0},
            ],
        )
        assert bid > 0
        assert Bill.get().title == "Hotpot"

    def test_creates_participants_from_list(self):
        """รายชื่อ participants ต้องถูกสร้างใน DB"""
        _save_dict(
            "Ramen",
            200.0,
            [{"name": "Alice", "amount": 100.0}, {"name": "Bob", "amount": 100.0}],
        )
        assert BillParticipant.select().count() == 2

    def test_creates_items(self):
        """items ที่ส่งมาต้องถูกสร้างใน BillItem"""
        _save_dict(
            "Omakase",
            1000.0,
            [{"name": "Me", "amount": 1000.0}],
            items=[
                {"name": "Tuna", "price": 500.0, "quantity": 1},
                {"name": "Crab", "price": 500.0, "quantity": 1},
            ],
        )
        assert BillItem.select().count() == 2


# ── get_bill_details tests ──────────────────────────────────────────────────────


class TestGetBillDetails:
    def test_title_and_total(self):
        """get_bill_details() ต้องคืน title และ total ถูกต้อง"""
        bid = _save_str("Noodle", 150.0, {"Bob": 150.0})
        d = st.get_bill_details(bid)
        assert d["title"] == "Noodle"
        assert d["total"] == 150.0

    def test_participants_names_present(self):
        """ต้องมีรายชื่อผู้เข้าร่วมครบใน participants"""
        bid = _save_str("Sushi", 400.0, {"Alice": 200.0, "Bob": 200.0})
        names = [p["name"] for p in st.get_bill_details(bid)["participants"]]
        assert "Alice" in names
        assert "Bob" in names

    def test_invalid_id_returns_empty(self):
        """id ที่ไม่มีอยู่ต้องคืน {}\""""
        assert st.get_bill_details(99999) == {}


# ── update_participant_paid tests ───────────────────────────────────────────────


class TestUpdateParticipantPaid:
    def test_marks_as_paid(self):
        """update_participant_paid() ต้องเปลี่ยน is_paid → True"""
        _save_str("Steak", 300.0, {"Alice": 300.0})
        p = BillParticipant.get(BillParticipant.display_name == "Alice")
        assert p.is_paid is False
        st.update_participant_paid(p.id, True)
        assert BillParticipant.get_by_id(p.id).is_paid is True

    def test_bill_done_when_all_paid(self):
        """เมื่อทุกคนจ่ายครบ bill.is_done ต้องเป็น True"""
        _save_str("Pizza", 500.0, {"Me": 250.0, "Bob": 250.0})
        bob = BillParticipant.get(BillParticipant.display_name == "Bob")
        st.update_participant_paid(bob.id, True)
        assert Bill.get().is_done is True

    def test_bill_not_done_if_partial(self):
        """ถ้ายังมีคนค้างจ่าย bill.is_done ต้องเป็น False"""
        _save_str("Burger", 400.0, {"Alice": 200.0, "Bob": 200.0})
        assert Bill.get().is_done is False


# ── get_balance_summary tests ───────────────────────────────────────────────────


class TestGetBalanceSummary:
    def test_empty_db_returns_zeros(self):
        """ไม่มีบิลเลย → 0 ทั้งคู่"""
        r = st.get_balance_summary()
        assert r["total_owed"] == 0.0
        assert r["total_owe_me"] == 0.0

    def test_has_expected_keys(self):
        """ต้องมี key total_owed และ total_owe_me"""
        r = st.get_balance_summary()
        assert "total_owed" in r
        assert "total_owe_me" in r

    def test_owe_me_from_unpaid_friend(self):
        """เพื่อนยังไม่จ่าย → total_owe_me ต้องเท่ากับยอดของเพื่อน"""
        _save_str("Ramen", 200.0, {"Me": 100.0, "Alice": 100.0})
        r = st.get_balance_summary()
        assert r["total_owe_me"] == 100.0
        assert r["total_owed"] == 0.0
