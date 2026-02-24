# 🧾 SplitIt - Bill Splitting Application

> แอปพลิเคชันสำหรับหารบิลร่วมกัน พร้อม AI สแกนใบเสร็จอัตโนมัติ

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Kivy](https://img.shields.io/badge/Kivy-2.3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 ภาพรวมโปรแกรม (Overview)

SplitIt คือแอปพลิเคชัน Kivy สำหรับหารบิลระหว่างเพื่อน โดยมีฟีเจอร์หลักดังนี้

- 📸 **สแกนใบเสร็จด้วย AI** — ใช้ Gemini 1.5 Flash อ่านใบเสร็จและแยกรายการอัตโนมัติ
- ➗ **หารบิลได้ 2 แบบ** — หารเท่ากัน (Split Equally) หรือกำหนดเองต่อคน (Custom Amount)
- 👥 **จัดการเพื่อน** — บันทึกรายชื่อเพื่อนไว้ใช้ซ้ำในครั้งถัดไป
- 📊 **ติดตามการจ่ายเงิน** — ดูได้ว่าใครจ่ายแล้ว ใครยังค้างอยู่
- 📋 **คัดลอกสรุปบิล** — copy ข้อความสรุปส่งหาเพื่อนผ่าน LINE/WhatsApp ได้เลย

---

## 👥 ทีมพัฒนา (Team)

| ชื่อ | รหัสนักศึกษา | หน้าที่ |
|------|-------------|---------|
| [ชื่อคนที่ 1] | [รหัส] | Core, Scan Screen, AI Integration, Dashboard |
| [ชื่อคนที่ 2] | [รหัส] | New Split, Friend Management, Summary, Result Screen |

---

## 🗂️ โครงสร้างโปรเจกต์ (Project Structure)

```
splitit/
├── main.py                    # Entry point — เริ่มต้น app และ ScreenManager
├── requirements.txt           # รายการ dependencies
├── .env                       # API Keys (ไม่อยู่ใน Git)
├── .gitignore
├── README.md
│
├── core/                      # Business Logic Layer
│   ├── models.py              # Peewee ORM — โครงสร้างฐานข้อมูล
│   ├── storage.py             # CRUD operations สำหรับ SQLite
│   ├── split_engine.py        # ตรรกะการคำนวณหารบิล
│   └── ai_service.py          # เชื่อมต่อ Gemini API
│
├── screens/                   # หน้าจอแต่ละหน้า
│   ├── dashboard_screen.py    # หน้าหลัก
│   ├── scan_screen.py         # หน้าสแกนใบเสร็จ
│   ├── new_split_screen.py    # หน้าสร้างบิลใหม่
│   ├── summary_screen.py      # หน้าสรุปบิล
│   └── result_screen.py       # หน้าผลลัพธ์ / ใครจ่ายเท่าไร
│
├── components/                # Reusable Widgets
│   ├── bill_card.py           # การ์ดแสดงบิลในหน้า Dashboard
│   ├── item_row.py            # แถวแสดงรายการสินค้าในบิล
│   └── person_row.py          # แถวแสดงชื่อ + ยอดที่ต้องจ่าย
│
├── kv/                        # KV Layout Files (UI)
│   ├── dashboard.kv
│   ├── scan.kv
│   ├── new_split.kv
│   ├── summary.kv
│   └── result.kv
│
└── assets/
    ├── fonts/                 # Custom fonts
    └── images/                # Icons, images
```

---

## 🔄 การทำงานของโปรแกรม (Workflow)

```
┌─────────────┐
│  Dashboard  │  ← หน้าหลัก: แสดง Balance Summary + Recent Splits
└──────┬──────┘
       │
  [Create New Bill]
       │
┌──────▼──────────┐
│  Scan Screen    │  ← ถ่ายรูป / เลือกจาก Gallery / กรอกเอง (Manual)
└──────┬──────────┘
       │ AI ประมวลผล → ดึง ชื่อร้าน, ราคา, รายการ
┌──────▼──────────┐
│ New Split Screen│  ← แก้ไขรายการ, เพิ่มเพื่อน, เลือกวิธีหาร
└──────┬──────────┘
       │ กด Calculate!
┌──────▼──────────┐
│ Summary Screen  │  ← แสดง Breakdown ว่าใครต้องจ่ายเท่าไร
└──────┬──────────┘
       │ กด Finish
┌──────▼──────────┐
│ Result Screen   │  ← ดูสถานะการจ่าย, Copy ข้อความ, กลับหน้าหลัก
└─────────────────┘
```

---

## 🤖 การทำงานของ AI (AI Integration)

โปรแกรมใช้ **Google Gemini 1.5 Flash** สำหรับอ่านใบเสร็จ โดยส่งรูปภาพพร้อม prompt ไปที่ API และรับผลลัพธ์กลับมาในรูปแบบ JSON

```
รูปใบเสร็จ
    ↓
Gemini 1.5 Flash API
    ↓
JSON: { title, total, items: [{name, price}] }
    ↓
แสดงผลใน New Split Screen (แก้ไขได้)
```

**หมายเหตุ:** ถ้า AI อ่านไม่ออก สามารถกรอกข้อมูลเองได้ผ่าน Manual mode

---

## 🗃️ ฐานข้อมูล (Database)

ใช้ **SQLite** ผ่าน **Peewee ORM** เก็บข้อมูลไว้ที่เครื่องโดยไม่ต้องมี server

| ตาราง | เก็บอะไร |
|-------|---------|
| `Friend` | ชื่อ, nickname, สีประจำตัว |
| `Bill` | ชื่อบิล, ยอดรวม, วันที่, สถานะ |
| `BillItem` | รายการสินค้าในแต่ละบิล |
| `BillParticipant` | ว่าใครอยู่ในบิลนี้ จ่ายเท่าไร จ่ายแล้วหรือยัง |

---

## ⚙️ วิธีติดตั้งและรัน (Installation & Running)

### 1. ติดตั้ง Dependencies

```bash
# Clone repository
git clone https://github.com/psu6810110366/splitit.git
cd splitit

# สร้าง virtual environment (แนะนำ)
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# ติดตั้ง packages
pip install -r requirements.txt
```

### 2. ตั้งค่า API Key

```bash
# สร้างไฟล์ .env ในโฟลเดอร์หลัก
# (รับ API Key ฟรีได้ที่ https://aistudio.google.com/apikey)

echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 3. รันโปรแกรม

```bash
python main.py
```

---

## 📦 Dependencies (requirements.txt)

```
kivy==2.3.1
kivymd==1.2.0
google-generativeai>=0.4.0
peewee>=3.17.0
Pillow>=10.0.0
python-dotenv>=1.0.0
pyperclip>=1.8.2
```

---

## 🧩 Widgets และ Callbacks

### Widgets (มีทั้งหมด 40+ widgets)

| หน้าจอ | Widgets หลัก |
|--------|-------------|
| Dashboard | ScreenManager, ScrollView, BillCard, Label, Button, BottomNav |
| Scan | Camera, Button (ถ่าย/Gallery/Manual), ProgressBar, Label |
| New Split | TextInput, RecycleView, ItemRow, ToggleButton, PersonRow, Modal |
| Summary | ScrollView, PersonBreakdownRow, Label, Button |
| Result | Label, PersonRow (+ paid status), Button |

### Callbacks (มีทั้งหมด 12 callbacks)

| ชื่อ Callback | หน้าที่ |
|--------------|---------|
| `on_scan_press()` | เปิดกล้องถ่ายรูปใบเสร็จ |
| `on_gallery_press()` | เลือกรูปจาก Gallery |
| `on_ai_result(result)` | รับผลจาก Gemini และแสดงรายการ |
| `on_add_item()` | เพิ่มรายการสินค้าด้วยตัวเอง |
| `on_delete_item(item_id)` | ลบรายการสินค้า |
| `on_add_friend()` | เปิด modal เลือก/เพิ่มเพื่อน |
| `on_split_mode_toggle(mode)` | สลับระหว่าง Equal / Custom |
| `on_calculate()` | คำนวณยอดและไป Summary |
| `on_copy_clipboard()` | copy สรุปบิลเป็นข้อความ |
| `on_mark_paid(participant_id)` | กดว่าคนนี้จ่ายแล้ว |
| `on_remind_press(name, amount)` | copy ข้อความทวงเงิน |
| `on_save_and_finish()` | บันทึกบิลและกลับหน้าหลัก |

---

## 📝 Git Commit Convention

```
feat:   เพิ่มฟีเจอร์ใหม่
fix:    แก้ bug
ui:     เปลี่ยน layout / design
refactor: ปรับ code โดยไม่เปลี่ยน behavior
docs:   อัปเดต README หรือ comment
test:   เพิ่ม test
chore:  งานเบื้องหลัง เช่น setup, config
```

---

## 📄 License

MIT License
