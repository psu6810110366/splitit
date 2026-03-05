import pytest
import json
from core.ai_service import scan_receipt

# สร้าง Stub สำหรับจำลองคำตอบจาก Gemini
class MockResponse:
    def __init__(self, text):
        self.text = text

def test_scan_receipt_with_stub(monkeypatch):
    # เราจะ Stub (หลอก) ฟังก์ชัน generate_content ของ Gemini 
    # เพื่อให้รันเทสได้โดยไม่ต้องใช้เน็ตและไม่ต้องมี API Key จริง
    
    def mock_generate_content(self, contents):
        # จำลอง JSON ที่ AI ควรตอบกลับมา
        mock_data = {
            "title": "Stub Coffee",
            "items": [{"name": "Latte", "price": 60.0}],
            "subtotal": 60.0,
            "tax_or_service_charge": 0.0,
            "total": 60.0
        }
        return MockResponse(json.dumps(mock_data))

    # ต้อง Stub Image.open ด้วย เพราะเราไม่มีไฟล์รูปจริง
    from PIL import Image
    class MockImage:
        def __getattr__(self, name): return lambda *args, **kwargs: None
        @property
        def width(self): return 100
        @property
        def height(self): return 100
        def save(self, *args, **kwargs): pass
    
    monkeypatch.setattr(Image, "open", lambda path: MockImage())

    # ใช้ monkeypatch ไปแก้พฤติกรรมของตัวแปร/ฟังก์ชันใน library
    from google.generativeai import GenerativeModel
    monkeypatch.setattr(GenerativeModel, "generate_content", mock_generate_content)
    # ต้องหลอกให้โปรแกรมคิดว่ามี API Key ด้วย
    monkeypatch.setattr("core.ai_service.GEMINI_API_KEY", "fake_key_for_testing")

    # รันฟังก์ชันจริงที่ต้องการเทส
    result = scan_receipt("dummy_path.jpg")
    
    assert result["title"] == "Stub Coffee"
    assert len(result["items"]) == 1
    assert result["total"] == 60.0

def test_scan_receipt_error_handling(monkeypatch):
    # ทดสอบกรณี AI พัง หรือตอบกลับมาเน่า
    def mock_fail(self, contents):
        raise Exception("API Timeout")

    from google.generativeai import GenerativeModel
    monkeypatch.setattr(GenerativeModel, "generate_content", mock_fail)
    monkeypatch.setattr("core.ai_service.GEMINI_API_KEY", "fake_key")

    result = scan_receipt("any.jpg")
    assert "error" in result
    assert "Failed to process receipt" in result["error"]
