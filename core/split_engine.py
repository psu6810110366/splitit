def split_by_items(items_with_assignments, all_participants):
    """
    หารเงินตามรายการที่แต่ละคนสั่ง (แบบกำหนดเองต่อชิ้น)
    :param items_with_assignments: [{'name': str, 'price': float, 'assigned_to': [str]}]
      — ถ้า assigned_to ว่าง หมายถึงทุกคนหารกัน
    :param all_participants: รายชื่อทุกคนในบิล (e.g. ["Me", "Alice", "Bob"])
    :return: dict {name: amount}
    """
    result = {p: 0.0 for p in all_participants}
    for item in items_with_assignments:
        assigned = item.get('assigned_to') or list(all_participants)
        if not assigned:
            assigned = list(all_participants)
        share = item['price'] / len(assigned)
        for name in assigned:
            if name in result:
                result[name] += share
    return {k: round(v, 2) for k, v in result.items()}


def split_equally(total: float, participants: list) -> dict:
    """
    หารบิลเท่าๆ กันตามจำนวนคน (Split the total equally among participants)
    :param total: ยอดรวมทั้งหมด (e.g. 1500.0)
    :param participants: รายชื่อคนที่หาร (e.g. ["You", "Alice", "Bob"])
    :return: dict {name: amount} -> {"You": 500.0, "Alice": 500.0, "Bob": 500.0}
    """
    if not participants or total <= 0:
        return {}
    
    count = len(participants)
    split_amount = round(total / count, 2)
    
    # คำนวณเศษทศนิยมที่เหลือ (Handle rounding remainder)
    remainder = total - (split_amount * count)
    
    result = {}
    for i, person in enumerate(participants):
        amount = split_amount
        # เอาเศษไปให้คนแรกจ่าย (Add remainder to the first person to make sum exact)
        if i == 0 and remainder != 0:
            amount += remainder
        result[person] = round(amount, 2)
        
    return result

def split_custom(items: list, assignments: dict) -> dict:
    """
    หารบิลตามรายการที่สั่งจริง (Split items based on who ordered what)
    :param items: รายการของ [{'name': 'item1', 'price': 100}, ...]
    :param assignments: ใครกินอะไรบ้าง {'Alice': ['item1'], 'Bob': ['item1']}
    :return: dict {name: amount} -> {'Alice': 50.0, 'Bob': 50.0}
    """
    result = {person: 0.0 for person in assignments.keys()}
    
    # วนลูปตามรายการของแต่ละชิ้น (Calculate cost per item and divide by shared users)
    for item in items:
        item_name = item['name']
        price = item['price']
        
        # หาคนที่ร่วมจ่ายราคานี้ (Find who shares this item)
        shared_by = [p for p, p_items in assignments.items() if item_name in p_items]
        
        if shared_by:
            cost_per_person = price / len(shared_by)
            for person in shared_by:
                result[person] += cost_per_person
                
    # ปัดเศษทศนิยม (Round up to 2 decimals)
    for person in result:
        result[person] = round(result[person], 2)
        
    return result

def format_result_text(bill_title: str, total: float, participants_result: list, items_list: list = None) -> str:
    """
    สร้างข้อความสำหรับคัดลอกลง Clipboard (Format string for sharing to Line/Messenger)
    :param bill_title: ชื่อบิล (e.g. "Shabu Buffet")
    :param total: ยอดเต็ม (e.g. 1500)
    :param participants_result: ผลลัพธ์จากการหาร (list of dicts containing name, amount, is_paid)
    :param items_list: รายการสินค้า (optional)
    :return: Formatted text block
    """
    text = f"💸 สรุปยอดค่า {bill_title}\n"
    
    if items_list:
        text += "📝 รายการ:\n"
        for item in items_list:
            qty = item.get('quantity', 1)
            name = item.get('name', 'Item')
            price = item.get('price', 0.0)
            text += f" - {name} (x{qty}): ฿{price:,.2f}\n"
        text += "\n"

    text += f"💰 ยอดรวม: ฿{total:,.2f}\n"
    text += "-" * 20 + "\n"
    
    all_paid = True
    for p in participants_result:
        name = p.get('name', 'Unknown')
        amount = p.get('amount', 0.0)
        is_paid = p.get('is_paid', False)
        
        status_icon = "✅ สำเร็จ" if is_paid else "⏳ รอชำระ"
        if not is_paid:
            all_paid = False
            
        text += f"👤 {name} ยอดโอน: ฿{amount:,.2f} ({status_icon})\n"
        
    text += "-" * 20 + "\n"
    if all_paid:
        text += "🎉 บิลนี้เคลียร์ครบทุกคนแล้ว ขอบคุณจ้า! 🙏"
    else:
        text += "อย่าลืมโอนเงินนะจ๊ะ! 🙏"
    
    return text
