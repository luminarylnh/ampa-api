from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 虛擬資料庫 (存在記憶體中)
barcode_db = {}

@app.get("/")
def read_root():
    return {"status": "Smart Tag System Online"}

@app.get("/generate/{tag_id}", response_class=HTMLResponse)
def generate_qr(tag_id: str):
    # 紀錄至收錢清單 (預設狀態 0: 尚未啟動)
    if tag_id not in barcode_db:
        barcode_db[tag_id] = 0
        
    # 客戶掃描後會前往的網址 (您的 Render 網址)
    qr_data = f"https://a-tag-system.onrender.com/scan/{tag_id}"
    
    # 呼叫全球最穩定的外部雲端 API 幫我們畫 QR Code
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_data}"
    
    return f"""
    <html>
        <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
            <h2 style="color: #1e3a8a;">A-Tag 標籤生成成功</h2>
            <p style="font-size: 20px;">料號: <b>{tag_id}</b></p>
            <img src="{qr_image_url}" alt="QR Code" style="margin: 20px; border: 5px solid #ccc; border-radius: 10px;" />
            <p style="font-size: 16px; color: #555;">請掃描上方條碼以啟動標籤</p>
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

@app.get("/summary", response_class=HTMLResponse)
def get_summary():
    activated_list = [tag for tag, status in barcode_db.items() if status == 1]
    
    if not activated_list:
        items_html = "<li style='color: gray; text-align: center;'>目前尚無啟動的料號...快去掃碼收錢！</li>"
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
