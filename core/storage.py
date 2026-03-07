"""
storage.py — Database Query Layer (Phase D)
Single Responsibility: ทุก DB query อยู่ที่นี่ที่เดียว
Screen ไม่ควร import peewee โดยตรง — ให้ผ่าน module นี้เสมอ
"""
import datetime
from core.models import db, Bill, BillItem, BillParticipant

# ชื่อที่ใช้แทนตัวเราในบิล (ตั้งเป็น constant เผื่อเปลี่ยนในอนาคต)
MY_DISPLAY_NAME = "Me"


def get_recent_bills(limit: int = 10) -> list:
    """
    ดึงบิลล่าสุดจาก DB พร้อมข้อมูลที่ Dashboard ต้องการ
    Returns: list of dict พร้อม key: bill_id, title, total, date_label, is_done, etc.
    """
    try:
        db.connect(reuse_if_open=True)
        # เรียง Unpaid (is_done=False=0) ก่อน Paid (is_done=True=1) แล้วตามด้วยวันที่ล่าสุด
        bills = (
            Bill.select()
            .order_by(Bill.is_done.asc(), Bill.created_at.desc())
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
            BillParticipant.is_paid == False  # noqa: E712
        )

        for p in participants:
            # ถ้าเป็นชื่อเรา (Me) และยังไม่จ่าย = เราติดหนี้คนอื่น
            if p.display_name == my_name:
                total_owed += p.amount_owed
            else:
                # ถ้าเป็นชื่อคนอื่นและยังไม่จ่าย = เขาติดหนี้เรา
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

def save_bill(bill_name_or_data, total_or_participants=None, items=None, breakdown=None) -> int:
    """
    บันทึกบิลพร้อมรายการและผู้เข้าร่วมลง DB
    รองรับ 2 รูปแบบการเรียก...
    """
    try:
        db.connect(reuse_if_open=True)
        with db.atomic():
            if isinstance(bill_name_or_data, str):
                bill_name = bill_name_or_data
                total = total_or_participants
                items_data = items or []
                breakdown_data = breakdown or {}

                bill = Bill.create(title=bill_name, total=total)
                for item in items_data:
                    BillItem.create(
                        bill=bill,
                        name=item['name'],
                        price=item['price'],
                        quantity=item.get('quantity', 1)
                    )
                for name, amount in breakdown_data.items():
                    # ถ้ารายการเป็นชื่อเรา (MY_DISPLAY_NAME) ให้ตั้งค่าว่าจ่ายแล้ว (is_paid=True) ทันที
                    is_me = (name == MY_DISPLAY_NAME)
                    BillParticipant.create(
                        bill=bill,
                        display_name=name,
                        amount_owed=round(amount, 2),
                        is_paid=is_me
                    )
            else:
                bill_data = bill_name_or_data
                participants_data = total_or_participants or []
                items_data = items or []

                bill = Bill.create(
                    title=bill_data.get('title', 'Unknown Bill'),
                    total=bill_data.get('total', 0.0),
                    notes=bill_data.get('notes', ''),
                    promptpay=bill_data.get('promptpay', ''),
                    is_done=False
                )
                for item in items_data:
                    BillItem.create(
                        bill=bill,
                        name=item.get('name', 'Item'),
                        price=item.get('price', 0.0),
                        quantity=item.get('quantity', 1)
                    )
                for p in participants_data:
                    p_name = p.get('name', 'Unknown')
                    is_me = (p_name == MY_DISPLAY_NAME)
                    BillParticipant.create(
                        bill=bill,
                        display_name=p_name,
                        amount_owed=p.get('amount', 0.0),
                        is_paid=p.get('is_paid', is_me)
                    )

        return bill.id
    except Exception as e:
        print(f"[storage] save_bill error: {e}")
        return -1
    finally:
        if not db.is_closed():
            db.close()


def get_bill_details(bill_id: int) -> dict:
    """
    ดึงรายชื่อบิลและผู้เข้าร่วมจาก DB โดยใช้ bill_id
    """
    try:
        db.connect(reuse_if_open=True)
        bill = Bill.get_by_id(bill_id)
        
        participants = []
        for p in bill.participants:
            participants.append({
                "id": p.id,
                "name": p.display_name,
                "amount": p.amount_owed,
                "is_paid": p.is_paid
            })
            
        items = []
        for i in bill.items:
            items.append({
                "name": i.name,
                "price": i.price,
                "quantity": i.quantity
            })
            
        return {
            "title": bill.title,
            "total": bill.total,
            "is_done": bill.is_done,
            "participants": participants,
            "items": items
        }
    except Exception as e:
        print(f"[storage] get_bill_details error: {e}")
        return {}
    finally:
        if not db.is_closed():
            db.close()

def update_participant_paid(participant_id: int, is_paid: bool):
    """
    อัปเดตสถานะการจ่ายเงิน และตรวจสอบว่าจ่ายครบทุกคนหรือยัง
    """
    try:
        db.connect(reuse_if_open=True)
        p = BillParticipant.get_by_id(participant_id)
        p.is_paid = is_paid
        p.save()
        
        # Check if all participants in this bill are paid
        bill = p.bill
        unpaid_count = BillParticipant.select().where(
            (BillParticipant.bill == bill) & 
            (BillParticipant.is_paid == False)
        ).count()
        
        bill.is_done = (unpaid_count == 0)
        bill.save()
        
    except Exception as e:
        print(f"[storage] update_participant_paid error: {e}")
    finally:
        if not db.is_closed():
            db.close()

# --- Private Helpers ---

def _format_bill_for_dashboard(bill: Bill) -> dict:
    """
    แปลง Bill model เป็น dict ที่ UI ใช้ได้เลย
    """
    unpaid_p = [p for p in bill.participants if not p.is_paid and p.display_name != MY_DISPLAY_NAME]
    me_p = next((p for p in bill.participants if p.display_name == MY_DISPLAY_NAME), None)
    
    if bill.is_done:
        status_label = "CLEARED"
        status_type = "owed"
        emoji = "✅"
    elif unpaid_p:
        # มีเพื่อนยังไม่จ่าย -> เพื่อนติดหนี้เรา
        total_unpaid = sum(p.amount_owed for p in unpaid_p)
        status_label = f"OWES YOU ฿{total_unpaid:,.2f}"
        status_type = "owed"
        emoji = "⏳"
    elif me_p and not me_p.is_paid:
        # เรายังไม่จ่าย -> เราติดหนี้ (ในเคสที่มีคนอื่นเป็นเจ้าของบิล)
        status_label = f"YOU OWE ฿{me_p.amount_owed:,.2f}"
        status_type = "owe"
        emoji = "💸"
    else:
        status_label = "PENDING"
        status_type = "owe"
        emoji = "🧾"

    return {
        "bill_id": bill.id,
        "title": bill.title,
        "total": bill.total,
        "is_done": bill.is_done,
        "date_label": _format_date_label(bill.created_at),
        "amount_label": f"฿{bill.total:,.2f}",
        "status_label": status_label,
        "status_type": status_type,
        "emoji": emoji,
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
