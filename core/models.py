import datetime
import random
from peewee import *

db = SqliteDatabase('splitit.db')

def random_hex_color():
    """สุ่มสีสำหรับ Avatar (Random hex color generator)"""
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6', '#3498DB']
    return random.choice(colors)

class BaseModel(Model):
    class Meta:
        database = db

class Friend(BaseModel):
    """ตารางรายชื่อเพื่อน (Friend Model)"""
    name = CharField()
    nickname = CharField(null=True)
    avatar_color = CharField(default=random_hex_color)
    created_at = DateTimeField(default=datetime.datetime.now)

class Bill(BaseModel):
    """ตารางบิลค่าใช้จ่าย (Bill Model)"""
    title = CharField()
    total = FloatField(default=0.0)
    is_done = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

class BillItem(BaseModel):
    """ตารางรายการในบิล (Bill Item Model)"""
    bill = ForeignKeyField(Bill, backref='items', on_delete='CASCADE')
    name = CharField()
    price = FloatField()

class BillParticipant(BaseModel):
    """ตารางผู้เข้าร่วมในบิลและการหารเงิน (Bill Participant Model)"""
    bill = ForeignKeyField(Bill, backref='participants', on_delete='CASCADE')
    friend = ForeignKeyField(Friend, backref='bills', null=True, on_delete='SET NULL')
    display_name = CharField()
    amount_owed = FloatField(default=0.0)
    is_paid = BooleanField(default=False)

def initialize_db():
    """สร้างตารางในฐานข้อมูล (Initialize DB schema)"""
    db.connect()
    db.create_tables([Friend, Bill, BillItem, BillParticipant], safe=True)
    db.close()
