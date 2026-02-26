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

def format_result_text(bill_title: str, total: float, participants_result: dict) -> str:
    """
    สร้างข้อความสำหรับคัดลอกลง Clipboard (Format string for sharing to Line/Messenger)
    :param bill_title: ชื่อบิล (e.g. "Shabu Buffet")
    :param total: ยอดเต็ม (e.g. 1500)
    :param participants_result: ผลลัพธ์จากการหาร (e.g. {"Alice": 500, "Bob": 500})
    :return: Formatted text block
    """
    text = f"💸 สรุปยอดค่า {bill_title}\n"
    text += f"💰 ยอดรวม: ฿{total:,.2f}\n"
    text += "-" * 20 + "\n"
    
    for name, amount in participants_result.items():
        text += f"👤 {name} จ่าย: ฿{amount:,.2f}\n"
        
    text += "-" * 20 + "\n"
    text += "อย่าลืมโอนเงินนะจ๊ะ! 🙏"
    
    return text
