import os
import json
import google.generativeai as genai
from PIL import Image

# โหลด API Key จาก Environment (Load API Key from env)
# Note: In production, load this from .env file or secure storage
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def scan_receipt(image_path: str) -> dict:
    """
    อ่านบิลด้วย Gemini 1.5 Flash (Scan receipt using Gemini)
    Returns ONLY valid JSON: {title, total, items: [{name, price}]}
    """
    if not GEMINI_API_KEY:
        return {"error": "API Key is missing. Please set GEMINI_API_KEY."}
        
    try:
        # โหลดรูปภาพ (Load image)
        img = Image.open(image_path)
        
        # เลือกโมเดลที่เร็วและเหมาะกับ Vision (Select Flash model)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # คำสั่งเฉพาะเจาะจงที่ลูกค้าขอ (Exact prompt from requirements)
        prompt = (
            "Look at this receipt. Extract store name, total amount, and itemized list. "
            "Return ONLY valid JSON: {\"title\": \"store name\", \"total\": 0.0, \"items\": [{\"name\": \"item1\", \"price\": 0.0}]} "
            "Currency is Thai Baht. If unreadable return {\"error\": \"cannot_read\"}"
        )
        
        # ส่งคำขอไปที่ Gemini (Send request)
        response = model.generate_content([prompt, img])
        
        # ดึงข้อความและทำความสะอาด (Extract and clean response for JSON parsing)
        text_result = response.text.strip()
        
        # เอา markdown format ออกถ้ามี (Remove markdown code blocks if present)
        if text_result.startswith("```json"):
            text_result = text_result[7:]
        if text_result.startswith("```"):
            text_result = text_result[3:]
        if text_result.endswith("```"):
            text_result = text_result[:-3]
            
        text_result = text_result.strip()
        
        # แปลงเป็น Dictionary (Parse JSON)
        return json.loads(text_result)
        
    except Exception as e:
        # จับ Error ทุกประเภท (Catch all errors gracefully)
        return {"error": f"Failed to process receipt: {str(e)}"}

def parse_slip(image_path: str) -> dict:
    """
    ฟังก์ชันสำหรับอ่านสลิปโอนเงิน (Optional: Parse bank transfer slip)
    (Can use similar logic to scan_receipt if needed)
    """
    return {"error": "Not implemented yet."}
