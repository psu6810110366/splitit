from core.split_engine import split_equally, split_custom

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
    items = [
        {'name': 'Beer', 'price': 120},
        {'name': 'Water', 'price': 20}
    ]
    # A กินเบียร์คนเดียว, B กินน้ำ, แต่แชร์เบียร์ด้วยกัน (สมมติแชร์)
    assignments = {
        "Alice": ["Beer"],
        "Bob": ["Beer", "Water"]
    }
    
    res = split_custom(items, assignments)
    # Beer 120 / 2 = 60 each
    # Water 20 / 1 = 20 for Bob
    assert res["Alice"] == 60.0
    assert res["Bob"] == 80.0

def test_split_custom_rounding():
    items = [{'name': 'Shared', 'price': 100}]
    # แชร์ 3 คน 
    assignments = {
        "P1": ["Shared"],
        "P2": ["Shared"],
        "P3": ["Shared"]
    }
    res = split_custom(items, assignments)
    # 100 / 3 = 33.333... -> round to 33.33
    assert res["P1"] == 33.33
