from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import qrcode
import io
import base64

app = FastAPI()

# 虛擬資料庫 (存在記憶體中)
barcode_db = {}

@app.get("/")
def read_root():
    return {"status": "Smart Tag System Online"}

@app.get("/generate/{tag_id}", response_class=HTMLResponse)
def generate_qr(tag_id: str):
    # 設定為未啟動狀態 (0)
    if tag_id not in barcode_db:
        barcode_db[tag_id] = 0
        
    # 生成指向 scan 網址的 QR Code
    qr_data = f"https://a-tag-system.onrender.com/scan/{tag_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    return f"""
    <html>
        <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
            <h2>A-Tag 標籤生成成功</h2>
            <p>料號: <b>{tag_id}</b></p>
            <img src="data:image/png;base64,{qr_b64}" alt="QR Code" />
            <p>請掃描上方條碼以啟動標籤</p>
        </body>
    </html>
    """

@app.get("/scan/{tag_id}", response_class=HTMLResponse)
def scan_qr(tag_id: str):
    # 標記為已啟動 (1)
    barcode_db[tag_id] = 1
    return f"""
    <html>
        <body style="text-align: center; font-family: sans-serif; padding-top: 50px; background-color: #f0fdf4;">
            <h1 style="color: #16a34a;">✔️ Tag {tag_id} 已啟動</h1>
            <p style="font-size: 20px;">狀態：已裝櫃 (Activated)</p>
            <p>數據已同步至雲端</p>
        </body>
    </html>
    """

# --- 這是您專屬的收錢清單 (匯總頁面) ---
@app.get("/summary", response_class=HTMLResponse)
def get_summary():
    activated_list = [tag for tag, status in barcode_db.items() if status == 1]
    
    if not activated_list:
        items_html = "<li style='color: gray;'>目前尚無啟動的料號...快去掃碼收錢！</li>"
    else:
        items_html = "".join([f"<li style='margin: 10px 0; font-size: 18px; border-bottom: 1px dashed #ccc; padding-bottom: 5px;'>📦 料號: <b>{tag}</b> <span style='float: right; color: #16a34a;'>✔️ 已裝櫃</span></li>" for tag in activated_list])
    
    return f"""
    <html>
        <body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: 0 auto; background-color: #f8fafc;">
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-top: 0;">📊 A-Tag 專案料號匯總</h1>
                <p style="font-size: 18px;">總計啟動件數: <b style="color: #dc2626; font-size: 28px;">{len(activated_list)}</b> 件</p>
                <ul style="list-style-type: none; padding: 0; margin-top: 20px;">
                    {items_html}
                </ul>
                <p style="color: gray; font-size: 12px; margin-top: 40px; text-align: center;">*目前為展示模式，資料暫存於雲端記憶體</p>
            </div>
        </body>
    </html>
    """
