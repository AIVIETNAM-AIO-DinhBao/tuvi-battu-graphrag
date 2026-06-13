# Hướng dẫn sử dụng Lasotuvi API

## 📋 Tổng quan

API Lasotuvi cung cấp các endpoints để sinh lá số Tử Vi từ thông tin ngày sinh. API được xây dựng bằng FastAPI và cung cấp output dạng JSON có cấu trúc.

**Base URL**: `http://localhost:8000`

---

## 🚀 Khởi động server

```bash
cd tuvi-battu-graphrag/backend

# Cài đặt dependencies (nếu chưa cài)
./setup_lasotuvi.sh
pip install -r requirements.txt

# Chạy server
uvicorn app.main:app --reload
```

Server sẽ chạy tại: `http://localhost:8000`

**Interactive API docs**: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### 1. Health Check

Kiểm tra trạng thái của Lasotuvi service.

**Endpoint**: `GET /lasotuvi/health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "lasotuvi_available": true
}
```

**cURL Example**:
```bash
curl http://localhost:8000/lasotuvi/health
```

---

### 2. Generate Birth Chart (POST)

Sinh lá số Tử Vi từ thông tin ngày sinh.

**Endpoint**: `POST /lasotuvi/generate`

**Request Body**:
```json
{
  "ngay": 15,
  "thang": 10,
  "nam": 1990,
  "gio": 6,
  "gioi_tinh": 1,
  "duong_lich": true,
  "time_zone": 7
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ngay` | int | ✅ | Ngày sinh (1-31) |
| `thang` | int | ✅ | Tháng sinh (1-12) |
| `nam` | int | ✅ | Năm sinh (1900-2100) |
| `gio` | int | ✅ | Giờ sinh (1-12)<br>1=Tý, 2=Sửu, ..., 12=Hợi |
| `gioi_tinh` | int | ✅ | Giới tính<br>1=Nam, -1=Nữ |
| `duong_lich` | bool | ❌ | Lịch Dương (default: true) |
| `time_zone` | int | ❌ | UTC offset (default: 7) |

**Response**:
```json
{
  "thongTinCanChi": {
    "ngay": 15,
    "thang": 10,
    "nam": 1990,
    "gio": 6,
    "gioiTinh": "Nam"
  },
  "daiCung": {
    "cungMenh": {
      "index": 5,
      "tenCung": "Thìn"
    },
    "cungThan": {
      "index": 11,
      "tenCung": "Tuất"
    }
  },
  "thapNhiCung": [
    {
      "cungSo": 1,
      "cungTen": "Tý",
      "cungChu": "Mệnh",
      "hanhCung": "Thủy",
      "amDuong": "Dương",
      "daiHan": 22,
      "tieuHan": "Dần",
      "coThhan": false,
      "cungSao": [
        {
          "saoTen": "Tử vi",
          "saoDacTinh": "Mãnh",
          "saoID": 1
        }
      ]
    }
    // ... 11 cung còn lại
  ],
  "timestamp": "2026-06-13T14:00:00"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/lasotuvi/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ngay": 15,
    "thang": 10,
    "nam": 1990,
    "gio": 6,
    "gioi_tinh": 1,
    "duong_lich": true,
    "time_zone": 7
  }'
```

**Python Example**:
```python
import requests

url = "http://localhost:8000/lasotuvi/generate"
data = {
    "ngay": 15,
    "thang": 10,
    "nam": 1990,
    "gio": 6,
    "gioi_tinh": 1,
    "duong_lich": True,
    "time_zone": 7
}

response = requests.post(url, json=data)
la_so = response.json()

print(f"Cung Mệnh: {la_so['daiCung']['cungMenh']['tenCung']}")
print(f"Cung Thân: {la_so['daiCung']['cungThan']['tenCung']}")
```

---

### 3. Generate Birth Chart (GET)

Alternative endpoint sử dụng query parameters (cho testing).

**Endpoint**: `GET /lasotuvi/generate`

**Query Parameters**:
```
?ngay=15&thang=10&nam=1990&gio=6&gioi_tinh=1&duong_lich=true&time_zone=7
```

**cURL Example**:
```bash
curl "http://localhost:8000/lasotuvi/generate?ngay=15&thang=10&nam=1990&gio=6&gioi_tinh=1"
```

**Browser URL**:
```
http://localhost:8000/lasotuvi/generate?ngay=15&thang=10&nam=1990&gio=6&gioi_tinh=1
```

---

## 📊 Response Structure

### ThapNhiCung (12 Cung)

Mỗi cung trong mảng `thapNhiCung` có cấu trúc:

```json
{
  "cungSo": 1,           // Số thứ tự cung (1-12)
  "cungTen": "Tý",       // Tên địa chi của cung
  "cungChu": "Mệnh",     // Vai trò của cung (Mệnh, Phụ mẫu, Phúc đức, ...)
  "hanhCung": "Thủy",    // Hành của cung (Kim, Mộc, Thủy, Hỏa, Thổ)
  "amDuong": "Dương",    // Âm hoặc Dương
  "daiHan": 22,          // Đại hạn (tuổi)
  "tieuHan": "Dần",      // Tiểu hạn (cung)
  "coThhan": false,      // Có cung Thân ký cư hay không
  "cungSao": [...]       // Danh sách sao trong cung
}
```

### CungSao (Sao trong cung)

Mỗi sao có cấu trúc:

```json
{
  "saoTen": "Tử vi",           // Tên sao
  "saoDacTinh": "Mãnh",        // Đặc tính: Mãnh, Vượng, Đắc, Bình, Hãm
  "saoID": 1                   // ID của sao
}
```

---

## ⚠️ Error Handling

### Validation Errors (400)

```json
{
  "detail": "Ngày sinh phải trong khoảng 1-31, nhận được: 32"
}
```

**Common validation errors**:
- Ngày không hợp lệ (1-31)
- Tháng không hợp lệ (1-12)
- Năm không hợp lệ (1900-2100)
- Giờ không hợp lệ (1-12)
- Giới tính không hợp lệ (1 hoặc -1)

### Server Errors (500)

```json
{
  "detail": "Lỗi khi sinh lá số: <error message>"
}
```

---

## 💡 Use Cases

### 1. Sinh lá số cho người dùng mới

```python
import requests

def create_birth_chart(user_birth_info):
    """Create birth chart for new user"""
    url = "http://localhost:8000/lasotuvi/generate"
    
    response = requests.post(url, json={
        "ngay": user_birth_info['day'],
        "thang": user_birth_info['month'],
        "nam": user_birth_info['year'],
        "gio": user_birth_info['hour'],
        "gioi_tinh": 1 if user_birth_info['gender'] == 'male' else -1,
        "duong_lich": True,
        "time_zone": 7
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to generate chart: {response.text}")

# Example usage
user = {
    'day': 15,
    'month': 10,
    'year': 1990,
    'hour': 6,
    'gender': 'male'
}

chart = create_birth_chart(user)
print(f"Birth chart created for {user['day']}/{user['month']}/{user['year']}")
```

### 2. Lấy thông tin cung cụ thể

```python
def get_cung_menh_info(la_so):
    """Extract Cung Mệnh information"""
    cung_menh_index = la_so['daiCung']['cungMenh']['index']
    
    for cung in la_so['thapNhiCung']:
        if cung['cungSo'] == cung_menh_index:
            return {
                'ten_cung': cung['cungTen'],
                'hanh': cung['hanhCung'],
                'am_duong': cung['amDuong'],
                'sao': [s['saoTen'] for s in cung['cungSao']]
            }
    return None

cung_menh = get_cung_menh_info(chart)
print(f"Cung Mệnh: {cung_menh}")
```

### 3. Phân tích sao trong các cung

```python
def analyze_stars(la_so):
    """Analyze stars distribution across palaces"""
    star_count = {}
    
    for cung in la_so['thapNhiCung']:
        cung_name = cung['cungTen']
        star_count[cung_name] = len(cung['cungSao'])
    
    return star_count

stars = analyze_stars(chart)
print(f"Star distribution: {stars}")
```

---

## 🔧 Integration với Frontend

### React Example

```typescript
// api/lasotuvi.ts
export interface BirthChartRequest {
  ngay: number;
  thang: number;
  nam: number;
  gio: number;
  gioi_tinh: number;
  duong_lich?: boolean;
  time_zone?: number;
}

export async function generateBirthChart(
  data: BirthChartRequest
): Promise<any> {
  const response = await fetch('http://localhost:8000/lasotuvi/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

// Component usage
const birthChart = await generateBirthChart({
  ngay: 15,
  thang: 10,
  nam: 1990,
  gio: 6,
  gioi_tinh: 1
});
```

---

## 📝 Testing

### Run unit tests

```bash
cd tuvi-battu-graphrag/backend
pytest tests/test_lasotuvi_service.py -v
```

### Manual testing với cURL

```bash
# Test health endpoint
curl http://localhost:8000/lasotuvi/health

# Test generation
curl -X POST http://localhost:8000/lasotuvi/generate \
  -H "Content-Type: application/json" \
  -d '{"ngay":15,"thang":10,"nam":1990,"gio":6,"gioi_tinh":1}'
```

---

## 📚 Giờ sinh (Địa chi mapping)

| Giờ | Địa chi | Thời gian |
|-----|---------|-----------|
| 1 | Tý | 23h-01h |
| 2 | Sửu | 01h-03h |
| 3 | Dần | 03h-05h |
| 4 | Mão | 05h-07h |
| 5 | Thìn | 07h-09h |
| 6 | Tỵ | 09h-11h |
| 7 | Ngọ | 11h-13h |
| 8 | Mùi | 13h-15h |
| 9 | Thân | 15h-17h |
| 10 | Dậu | 17h-19h |
| 11 | Tuất | 19h-21h |
| 12 | Hợi | 21h-23h |

---

## 🔗 Tài liệu liên quan

- [LASOTUVI_SETUP.md](./LASOTUVI_SETUP.md) - Hướng dẫn cài đặt
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API documentation
- [Redoc](http://localhost:8000/redoc) - Alternative API docs

---

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. ✅ Lasotuvi đã được cài đặt đúng chưa? (xem LASOTUVI_SETUP.md)
2. ✅ Server đang chạy không? (`uvicorn app.main:app`)
3. ✅ Port 8000 có bị block không?
4. ✅ Request body format có đúng không?