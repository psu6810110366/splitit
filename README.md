# SplitIt 💸

แอปพลิเคชันสำหรับช่วยคำนวณและแบ่งค่าใช้จ่าย (Split Bill) พัฒนาด้วยภาษ Python และ Kivy Framework

## 🚀 ฟีเจอร์หลัก

- (กำลังพัฒนา) แบ่งค่าอาหาร/ค่าใช้จ่ายกับเพื่อน

## 🛠️ วิธีการติดตั้ง (Installation)

1. **Clone โปรเจกต์นี้ลงเครื่อง:**

   ```bash
   git clone git@github.com:psu6810110366/splitit.git
   cd splitit
   ```

2. **สร้าง Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # สำหรับ macOS/Linux
   # venv\Scripts\activate  # สำหรับ Windows
   ```

3. **ติดตั้ง Library ที่จำเป็น:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 วิธีการรันโปรแกรม (Running)

ขณะที่อยู่ใน `venv` ให้รันคำสั่ง:

```bash
python main.py
```

## 🏗️ โครงสร้างโปรเจกต์

- `main.py`: ไฟล์หลักสำหรับรันแอปพลิเคชัน
- `main.kv`: ไฟล์สำหรับออกแบบ UI (Kivy Language)
- `requirements.txt`: รายการ Library ที่โปรเจกต์ต้องการ
- `.gitignore`: การตั้งค่าเพื่อไม่ให้เอาไฟล์บางอย่าง (เช่น `venv`) ขึ้น Git
