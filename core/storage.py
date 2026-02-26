"""
storage.py — Database Query Layer (Phase D)
Single Responsibility: ทุก DB query อยู่ที่นี่ที่เดียว
Screen ไม่ควร import peewee โดยตรง — ให้ผ่าน module นี้เสมอ
"""
import datetime
from core.models import db, Bill, BillItem, BillParticipant, Friend

# ชื่อที่ใช้แทนตัวเราในบิล (ตั้งเป็น constant เผื่อเปลี่ยนในอนาคต)
MY_DISPLAY_NAME = "Me"


def get_recent_bills(limit: int = 10) -> list:
    """
    ดึงบิลล่าสุดจาก DB พร้อมข้อมูลที่ Dashboard ต้องการ
    Returns: list of dict พร้อม key: title, total, date_label, is_done, participant_count
    """
    try:
        db.connect(reuse_if_open=True)
        bills = (
            Bill.select()
            .order_by(Bill.created_at.desc())
            .limit(limit)
        )
        result = []
        for bill in bills:
            result.append(_format_bill_for_dashboard(bill))
        return result
    except Exception as e:
        print(f"[storage] get_recent_bills error: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()


def get_balance_summary(my_name: str = MY_DISPLAY_NAME) -> dict:
    """
    คำนวณยอดคงเหลือ: คุณเป็นหนี้ใคร vs ใครเป็นหนี้คุณ
    Returns: {"total_owed": float, "total_owe_me": float}
    """
    try:
        db.connect(reuse_if_open=True)
        total_owed = 0.0    # ยอดที่คุณยังต้องจ่าย
        total_owe_me = 0.0  # ยอดที่คนอื่นต้องจ่ายคุณ

        participants = BillParticipant.select().where(
            BillParticipant.is_paid == False  # noqa: E712 — peewee syntax
        )

        for p in participants:
            if p.display_name == my_name:
                # คุณยังไม่ได้จ่าย
                total_owed += p.amount_owed
            else:
                # คนอื่นยังไม่ได้จ่าย (ถ้าคุณเป็นคนจ่ายบิลนั้น)
                total_owe_me += p.amount_owed

        return {
            "total_owed": round(total_owed, 2),
            "total_owe_me": round(total_owe_me, 2),
        }
    except Exception as e:
        print(f"[storage] get_balance_summary error: {e}")
        return {"total_owed": 0.0, "total_owe_me": 0.0}
    finally:
        if not db.is_closed():
            db.close()


# --- Private Helpers ---

def _format_bill_for_dashboard(bill: Bill) -> dict:
    """
    แปลง Bill model เป็น dict ที่ UI ใช้ได้เลย
    Clean Code: ซ่อน logic การ format ไว้ใน helper แทนที่จะยัดใน loop
    """
    return {
        "title": bill.title,
        "total": bill.total,
        "is_done": bill.is_done,
        "date_label": _format_date_label(bill.created_at),
        "amount_label": f"฿{bill.total:,.2f}",
        "status_color": "#00C853" if bill.is_done else "#FF6B6B",
    }


def _format_date_label(dt: datetime.datetime) -> str:
    """แปลงวันที่เป็น label เช่น Today, Yesterday หรือ วัน/เดือน"""
    today = datetime.date.today()
    bill_date = dt.date() if hasattr(dt, "date") else today

    if bill_date == today:
        return "Today"
    elif bill_date == today - datetime.timedelta(days=1):
        return "Yesterday"
    else:
        return bill_date.strftime("%-d %b")  # e.g. "24 Feb"
