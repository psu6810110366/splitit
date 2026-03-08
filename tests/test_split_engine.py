from core.split_engine import (
    split_equally,
    split_custom,
    split_by_items,
    format_result_text,
)


def test_split_equally_basic():
    # เคสหารลงตัวปกติ
    res = split_equally(300, ["A", "B", "C"])
    assert res["A"] == 100
    assert res["B"] == 100
    assert res["C"] == 100


def test_split_equally_with_remainder():
    # เคสหารไม่ลงตัว (100 / 3)
    # คนแรกต้องแบกเศษเพื่อให้ยอดรวมตรงเป๊ะ
    res = split_equally(100, ["A", "B", "C"])
    assert res["A"] == 33.34
    assert res["B"] == 33.33
    assert res["C"] == 33.33
    assert sum(res.values()) == 100.0


def test_split_equally_edge_cases():
    assert split_equally(0, ["A"]) == {}
    assert split_equally(100, []) == {}


def test_split_custom_logic():
    items = [{"name": "Beer", "price": 120}, {"name": "Water", "price": 20}]
    # A กินเบียร์คนเดียว, B กินน้ำ, แต่แชร์เบียร์ด้วยกัน (สมมติแชร์)
    assignments = {"Alice": ["Beer"], "Bob": ["Beer", "Water"]}

    res = split_custom(items, assignments)
    # Beer 120 / 2 = 60 each
    # Water 20 / 1 = 20 for Bob
    assert res["Alice"] == 60.0
    assert res["Bob"] == 80.0


def test_split_custom_rounding():
    items = [{"name": "Shared", "price": 100}]
    # แชร์ 3 คน
    assignments = {"P1": ["Shared"], "P2": ["Shared"], "P3": ["Shared"]}
    res = split_custom(items, assignments)
    # 100 / 3 = 33.333... -> round to 33.33
    assert res["P1"] == 33.33


# ─────────────────────────────────────────────────────────────
# split_by_items tests
# ─────────────────────────────────────────────────────────────


def test_split_by_items_assigned():
    """แต่ละ item กำหนดว่าใครจ่าย"""
    items = [
        {"name": "ข้าวผัด", "price": 60, "assigned_to": ["Alice"]},
        {"name": "ต้มยำ", "price": 80, "assigned_to": ["Alice", "Bob"]},
    ]
    res = split_by_items(items, ["Alice", "Bob"])
    # Alice: 60 + 40 = 100, Bob: 40
    assert res["Alice"] == 100.0
    assert res["Bob"] == 40.0


def test_split_by_items_empty_assigned_means_everyone():
    """assigned_to ว่าง → ทุกคนหารกัน"""
    items = [{"name": "ชาเขียว", "price": 90, "assigned_to": []}]
    res = split_by_items(items, ["A", "B", "C"])
    assert res["A"] == 30.0
    assert res["B"] == 30.0
    assert res["C"] == 30.0


def test_split_by_items_only_one_person():
    """คน assign เดียว → จ่ายคนเดียว"""
    items = [{"name": "พิซซ่า", "price": 200, "assigned_to": ["Bob"]}]
    res = split_by_items(items, ["Alice", "Bob"])
    assert res["Alice"] == 0.0
    assert res["Bob"] == 200.0


def test_split_by_items_multiple_items_mixed():
    """หลาย item ผสมกัน (assigned + ไม่ assigned)"""
    items = [
        {"name": "เบียร์", "price": 120, "assigned_to": ["Alice", "Bob"]},
        {"name": "น้ำเปล่า", "price": 20, "assigned_to": []},
    ]
    res = split_by_items(items, ["Alice", "Bob"])
    # เบียร์: 60 each | น้ำ: 10 each
    assert res["Alice"] == 70.0
    assert res["Bob"] == 70.0


def test_split_by_items_rounding():
    """ราคาหารไม่ลงตัวต้องปัดเศษถูก"""
    items = [{"name": "ไอศครีม", "price": 100, "assigned_to": ["X", "Y", "Z"]}]
    res = split_by_items(items, ["X", "Y", "Z"])
    # 100/3 = 33.33
    assert res["X"] == 33.33
    assert res["Y"] == 33.33
    assert res["Z"] == 33.33


# ─────────────────────────────────────────────────────────────
# format_result_text tests
# ─────────────────────────────────────────────────────────────


def test_format_result_text_basic():
    """ข้อความพื้นฐาน — มีชื่อบิล, ยอดรวม, และผู้เข้าร่วม"""
    participants = [
        {"name": "Alice", "amount": 150.0, "is_paid": False},
        {"name": "Bob", "amount": 150.0, "is_paid": False},
    ]
    text = format_result_text("Dinner", 300.0, participants)
    assert "Dinner" in text
    assert "฿300.00" in text
    assert "Alice" in text
    assert "Bob" in text


def test_format_result_text_all_paid():
    """ทุกคนจ่ายแล้ว → มีข้อความ 'เคลียร์ครบ'"""
    participants = [
        {"name": "Alice", "amount": 100.0, "is_paid": True},
    ]
    text = format_result_text("Lunch", 100.0, participants)
    assert "เคลียร์ครบ" in text


def test_format_result_text_has_pending():
    """มีคนยังไม่จ่าย → มีข้อความรอชำระ"""
    participants = [
        {"name": "Bob", "amount": 200.0, "is_paid": False},
    ]
    text = format_result_text("BBQ", 200.0, participants)
    assert "อย่าลืมโอน" in text
    assert "⏳ รอชำระ" in text


def test_format_result_text_with_items():
    """ส่ง items เข้าไปด้วย → แสดงหัวข้อรายการ"""
    participants = [{"name": "A", "amount": 50.0, "is_paid": True}]
    items = [{"name": "ข้าวมันไก่", "price": 50.0, "quantity": 1}]
    text = format_result_text("Brunch", 50.0, participants, items)
    assert "📝 รายการ" in text
    assert "ข้าวมันไก่" in text
    assert "฿50.00" in text


def test_format_result_text_status_icon():
    """ผู้จ่ายแล้วต้องมี ✅, ยังไม่จ่ายต้องมี ⏳"""
    participants = [
        {"name": "Alice", "amount": 100.0, "is_paid": True},
        {"name": "Bob", "amount": 100.0, "is_paid": False},
    ]
    text = format_result_text("Party", 200.0, participants)
    assert "✅ สำเร็จ" in text
    assert "⏳ รอชำระ" in text
