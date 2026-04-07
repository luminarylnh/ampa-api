from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import qrcode
from io import BytesIO

app = FastAPI()

# 模擬資料庫：0 為待處理，1 為已啟動
barcode_db = {"TAG001": 0}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Smart Tag 系統已連線</h1><p>目前狀態：運作正常</p>"

@app.get("/scan/{tag_id}", response_class=HTMLResponse)
def scan_tag(tag_id: str):
    if tag_id in barcode_db:
        barcode_db[tag_id] = 1 # 模擬掃描動作
        return f"""
        <html>
            <body style="text-align:center; font-family:sans-serif; padding-top:50px;">
                <h1 style="color:green;">✔️ Tag {tag_id} 已啟動</h1>
                <p style="font-size:24px;">狀態：已裝櫃 (Activated)</p>
                <p>數據已同步至 Keystone 供應鏈系統</p>
                <div style="margin-top:20px; font-size:12px; color:gray;">RWA PulseFi 技術支援</div>
            </body>
        </html>
        """
    return "<h1>錯誤：無效的標籤</h1>", 404

@app.get("/generate/{tag_id}")
def generate_qr(tag_id: str):
    # 這裡已經換成您正式的 Render 網址
    qr_data = f"https://ampa-tag-system.onrender.com/scan/{tag_id}"
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
