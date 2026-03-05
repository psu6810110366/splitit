# 🧾 SplitIt - Premium Bill Splitting Application

> แอปพลิเคชันสำหรับหารบิลร่วมกัน พร้อม AI สแกนใบเสร็จอัตโนมัติ และระบบหารเงินที่ยืดหยุ่น

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Kivy](https://img.shields.io/badge/Kivy-2.3.1-green)
![KivyMD](https://img.shields.io/badge/KivyMD-1.2.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 ฟีเจอร์หลัก (Key Features)

SplitIt ออกแบบมาเพื่อช่วยให้การหารบิลหลังมื้ออาหารหรือกิจกรรมต่างๆ เป็นเรื่องง่ายและรวดเร็ว:

- 📸 **AI Receipt Scanning** — ใช้ Google Gemini 1.5 Flash อ่านใบเสร็จและแยกรายการสินค้าพร้อมราคาให้อัตโนมัติ (รวดเร็วและแม่นยำ)
- ➗ **Flexible Splitting Modes** —
  - **Split Equally**: หารเท่ากันทุกคนโดยคำนวณจากยอดรวม
  - **Custom Amount**: กำหนดราคาเองต่อคน (Manual Entry) พร้อมแถบ **"Remaining Balance"** แจ้งเตือนยอดที่ยังค้างอยู่
- 🎨 **Premium UI/UX Design** — ทำงานด้วย KivyMD พร้อมไอคอนระบบ (MDIcon) ที่คมชัด ทันสมัย และรองรับทุกอุปกรณ์
- 👥 **Friend Management System** — บันทึกรายชื่อเพื่อนและสีประจำตัว (Avatar Color) เพื่อความรวดเร็วในการเลือกครั้งถัดไป
- 📋 **One-Tap Summary** — คัดลอกข้อความสรุปการหารไปส่งใน LINE/Messenger ได้ทันที

---

## 🎨 ส่วนติดต่อผู้ใช้ (User Interface)

ในเวอร์ชันล่าสุด (v1.4) เราได้ปรับปรุงหน้า Dashboard ให้ดูพรีเมียมยิ่งขึ้น:

- **Universal Icons**: เปลี่ยนจาก Emoji มาเป็น MDIcons เพื่อแก้ปัญหาการแสดงผลผิดพลาด (รูปสี่เหลี่ยม)
- **Symmetry Layout**: จัดวางตำแหน่งปุ่ม Scan และ Add Friend ให้สมดุลและสวยงาม
- **Smart Icons**: ระบบเลือกไอคอนบิลให้อัตโนมัติตามชื่อรายการ (เช่น อาหาร, กาแฟ, รถแท็กซี่)

---

## 👥 ทีมพัฒนา (Development Team)

| ชื่อ | รหัสนักศึกษา | หน้าที่หลัก |
|------|-------------|---------|
| นายมูฮัมหมัดฟาอีฟ ยามา | 6810110498 | Core Logic, Scan Screen, AI Integration, Dashboard Polish |
| นายสรวิศ จิตณรงค์  | 6810110366 | New Split Screen, Custom Split Engine, Friend Management, Results |

---

## 🗂️ โครงสร้างโปรเจกต์ (Project Structure)

```
splitit/
├── main.py                    # จุดเริ่มต้นแอป (ScreenManager)
├── .env                       # เก็บ API Key (Gemini)
├── core/                      # ส่วนประมวลผล (Backend)
│   ├── models.py              # ฐานข้อมูล (SQLite + Peewee)
│   ├── storage.py             # ฟังก์ชันจัดการข้อมูล (CRUD)
│   ├── split_engine.py        # ตรรกะการคำนวณเงิน
│   └── ai_service.py          # ส่วนเชื่อมต่อ Gemini AI
├── screens/                   # หน้าจอหลัก (Logic)
├── components/                # ส่วนประกอบ UI (Reusable Widgets)
├── kv/                        # ไฟล์ดีไซน์ (Layouts)
└── assets/                    # ฟอนต์และรูปภาพ
```

---

## ⚙️ วิธีติดตั้งและใช้งาน (Installation)

1. **เตรียมสภาพแวดล้อม:**

```bash
git clone https://github.com/psu6810110366/splitit.git
cd splitit
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
```

1. **ติดตั้ง Package:**

```bash
pip install -r requirements.txt
```

1. **ตั้งค่า API Key:**

สร้างไฟล์ `.env` และใส่ Key ของคุณ (รับฟรีได้ที่ [AI Studio](https://aistudio.google.com/apikey))

```env
GEMINI_API_KEY=your_key_here
```

1. **รันโปรแกรม:**

```bash
python main.py
```

---

## 🧩 เทคโนโลยีที่ใช้ (Tech Stack)

- **Language**: Python 3.11+
- **Framework**: Kivy & KivyMD (Material Design)
- **Database**: SQLite (ORM via Peewee)
- **AI**: Gemini 1.5 Flash
- **Tools**: python-dotenv, pyperclip, pillow

---

## 📄 ใบอนุญาต (License)

โครงการนี้อยู่ภายใต้ใบอนุญาต MIT License สามารถนำไปพัฒนาต่อยอดได้ตามเงื่อนไข
