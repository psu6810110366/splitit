import os
from dotenv import load_dotenv

# โหลด .env ก่อน ค่อย import ai_service
load_dotenv()

from core.ai_service import scan_receipt

def test_receipts():
    receipts = [
        "assets/test_receipt_35.png",
        "assets/test_receipt_40.png"
    ]
    
    for r in receipts:
        print(f"\\n--- ทดสอบใบเสร็จ: {r} ---")
        if not os.path.exists(r):
            print(f"ไม่พบไฟล์: {r}")
            continue
            
        print("กำลังส่งให้ Gemini ประมวลผล...")
        result = scan_receipt(r)
        
        print("ผลลัพธ์ (JSON):")
        import json
        try:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print(result)

if __name__ == "__main__":
    test_receipts()
