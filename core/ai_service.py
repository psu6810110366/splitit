import os
import json
import tempfile
import google.generativeai as genai
from PIL import Image

# โหลด API Key จาก Environment (Load API Key from env)
# Note: In production, load this from .env file or secure storage
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def preprocess_image(image_path: str) -> str:
    """
    ลดขนาดและบีบอัดรูปภาพก่อนส่งให้ AI เพื่อลด Latency (Resize & Compress)
    """
    try:
        img = Image.open(image_path)
        
        # แปลงเป็น RGB เผื่อเป็น PNG ที่มี Alpha channel
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # กำหนดขนาดสูงสุดที่ขอบยาวที่สุดไม่เกิน 1024px
        max_size = 1024
        if max(img.width, img.height) > max_size:
            ratio = max_size / max(img.width, img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        # บันทึกรูปชั่วคราวแบบลดคุณภาพ (JPEG 80%)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp_file.name, "JPEG", quality=80)
        return temp_file.name
    except Exception as e:
        print(f"Image preprocessing failed: {e}")
        return image_path # ถ้าพังก็ส่งรูปต้นฉบับไปเลย

def scan_receipt(image_path: str) -> dict:
    """
    อ่านบิลด้วย Gemini 1.5 Flash (Scan receipt using Gemini)
    Returns ONLY valid JSON: {title, total, subtotal, tax_or_service_charge, items: [{name, price}]}
    """
    if not GEMINI_API_KEY:
        return {"error": "API Key is missing. Please set GEMINI_API_KEY."}
        
    compressed_image_path = None
    try:
        # 1. ย่อรูปก่อนส่ง (Image Pre-processing)
        compressed_image_path = preprocess_image(image_path)
        img = Image.open(compressed_image_path)
        
        # 2. เลือกโมเดลที่เร็วและเหมาะกับ Vision (Select Flash model)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. คำสั่งเฉพาะเจาะจงที่เข้มงวด (Strict Prompting)
        prompt = """
        You are a highly accurate receipt parsing AI. Look at the provided receipt image.
        Extract the store name, itemized list, subtotal, tax/service charge (if explicitly shown, separate it from items), and the grand total.
        
        CRITICAL RULES:
        1. Return ONLY valid JSON format. No markdown blocks, no conversational text.
        2. Currency is Thai Baht. Output all prices as floats.
        3. Tax/Service Charge MUST be separated from the main food/drink items if possible.
        4. If unreadable or not a receipt, return exactly: {"error": "cannot_read"}
        
        JSON SCHEMA TO FOLLOW EXACTLY:
        {
          "title": "Store Name Here",
          "items": [{"name": "Item 1", "price": 100.0}, {"name": "Item 2", "price": 50.0}],
          "subtotal": 150.0,
          "tax_or_service_charge": 15.0,
          "total": 165.0
        }
        """
        
        # 4. ส่งคำขอไปที่ Gemini (Send request)
        response = model.generate_content([prompt, img])
        
        # 5. ดึงข้อความและทำความสะอาด (Extract and clean response for JSON parsing)
        text_result = response.text.strip()
        
        # เอา markdown format ออกถ้า AI เผลอใส่มา (Remove markdown code blocks if present)
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
    finally:
        # ทำความสะอาดไฟล์ชั่วคราว (Cleanup temp file)
        if compressed_image_path and compressed_image_path != image_path:
            try:
                os.remove(compressed_image_path)
            except OSError:
                pass

def parse_slip(image_path: str) -> dict:
    """
    ฟังก์ชันสำหรับอ่านสลิปโอนเงิน (Optional: Parse bank transfer slip)
    (Can use similar logic to scan_receipt if needed)
    """
    return {"error": "Not implemented yet."}
