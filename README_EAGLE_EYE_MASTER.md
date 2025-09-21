# Eagle Eye Master - Quick Start Guide

## 🚀 One Command, Any Area - No Code Changes Needed!

Eagle Eye Master ให้คุณเลือกพื้นที่ได้อย่างยืดหยุ่น โดยไม่ต้องแก้ไข code

### 📊 พื้นที่ที่ใช้ได้
- **6 จังหวัด** | **14 อำเภอ** | **37 ตำบล** | **628 หมู่บ้าน** | **1,002 Happy Blocks**

---

## 🎯 Quick Commands

### 1. ดูพื้นที่ทั้งหมด
```bash
python scripts/eagle_eye_master.py --list-areas
```

### 2. เลือกโดยจังหวัด
```bash
python scripts/eagle_eye_master.py --province="สงขลา" --limit=10
```

### 3. เลือกโดยอำเภอ
```bash
python scripts/eagle_eye_master.py --district="หาดใหญ่" --limit=5
```

### 4. เลือกโดยตำบล
```bash
python scripts/eagle_eye_master.py --subdistrict="ท่าข้าม" --limit=3
```

### 5. เลือกโดยหมู่บ้าน (ใหม่!)
```bash
python scripts/eagle_eye_master.py --village="หมู่บ้านออกซิเจน วีฟวา" --limit=1
```

### 6. เลือกหลายหมู่บ้าน
```bash
python scripts/eagle_eye_master.py --village="บ้านน้ำกระจาย สงขลา-หาดใหญ่ สายเก่า,หมู่บ้านออกซิเจน วีฟวา"
```

### 7. เลือกโดย Happy Block ID
```bash
python scripts/eagle_eye_master.py --happyblock="07110-100570,07130-100555"
```

### 8. เลือกโดยพิกัดภูมิศาสตร์
```bash
python scripts/eagle_eye_master.py --bbox="7.0,100.5,7.2,100.6" --limit=5
```

### 9. รวมหลายเงื่อนไข
```bash
python scripts/eagle_eye_master.py --province="สงขลา" --district="หาดใหญ่" --village="หมู่บ้านออกซิเจน วีฟวา" --format=excel
```

### 10. โหมดแบบ Interactive
```bash
python scripts/eagle_eye_master.py --interactive
```

---

## 📁 Output Formats

### CSV (default)
```bash
python scripts/eagle_eye_master.py --district="หาดใหญ่" --format=csv
```

### Excel
```bash
python scripts/eagle_eye_master.py --district="หาดใหญ่" --format=excel
```

---

## 🎛️ Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--province` | จังหวัด (comma-separated) | `--province="สงขลา,ภูเก็ต"` |
| `--district` | อำเภอ (comma-separated) | `--district="หาดใหญ่,เมือง"` |
| `--subdistrict` | ตำบล (comma-separated) | `--subdistrict="ท่าข้าม,บางใหญ่"` |
| `--village` | หมู่บ้าน (comma-separated) | `--village="หมู่บ้านออกซิเจน วีฟวา"` |
| `--happyblock` | Happy Block IDs | `--happyblock="07110-100570,07130-100555"` |
| `--bbox` | พิกัดสี่เหลี่ยม | `--bbox="7.0,100.5,7.2,100.6"` |
| `--limit` | จำนวน Happy Blocks | `--limit=5` |
| `--format` | รูปแบบไฟล์ | `--format=excel` |
| `--interactive` | โหมด Interactive | `--interactive` |
| `--list-areas` | แสดงพื้นที่ทั้งหมด | `--list-areas` |

---

## 📊 Report Structure

### OVERVIEW Rows (สำหรับผู้จัดการ)
- Happy Block summary
- Priority Score
- Total ports available
- Timing recommendations
- Google Maps links

### DETAIL Rows (สำหรับทีมขาย)
- Individual L2 equipment details
- Specific coordinates
- Port availability per L2
- Installation status
- Utilization percentage

---

## ✅ Quick Test

```bash
# ทดสอบด่วน - Hat Yai area, top 3 blocks, Excel format
python scripts/eagle_eye_master.py --district="หาดใหญ่" --limit=3 --format=excel
```

**Output**: `eagle_eye_report_หาดใหญ่_YYYYMMDD_HHMM.xlsx`

---

## 🔧 Troubleshooting

### Unicode Issues (Thai characters)
- Output files สามารถเปิดด้วย Excel ได้ปกติ
- Console อาจแสดงอักขระไทยผิดเพี้ยน แต่ไฟล์ผลลัพธ์ถูกต้อง

### No Results Found
```
No Happy Blocks found with specified criteria!
```
- ลองใช้ `--list-areas` ดูพื้นที่ที่มี
- ตรวจสอบชื่อพื้นที่ให้ถูกต้อง
- ลดเงื่อนไขให้น้อยลง

---

## 📞 Support

สำหรับการใช้งาน Eagle Eye Master:
1. ใช้ `--list-areas` ดูพื้นที่ที่มี
2. เริ่มจากเงื่อนไขง่าย ๆ เช่น `--province` หรือ `--district`
3. ใช้ `--interactive` สำหรับ user-friendly interface

**Ready to boost your sales efficiency!** 🎯