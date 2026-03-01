from fastapi import FastAPI, Request
from delta_rest_client import DeltaRestClient
import os

app = FastAPI()

# ===== API KEYS =====
API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

# ===== DELTA CONNECTION =====
client = DeltaRestClient(
    base_url="https://api.delta.exchange",
    api_key=API_KEY,
    api_secret=API_SECRET
)

# ===== RISK SETTINGS =====
CAPITAL = float(os.getenv("CAPITAL", 3000))
RISK_PCT = float(os.getenv("RISK_PCT", 0.003))
ATR_MULT = float(os.getenv("ATR_MULT", 1.2))

# ===== DELTA PRODUCT ID =====
# BTCUSDT Perpetual product_id on Delta = 27
PRODUCT_ID = 27

@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()

        side = data["side"].lower()
        price = float(data["price"])
        atr = float(data["atr"])

        # ===== RISK CALCULATION =====
        risk_amount = CAPITAL * RISK_PCT
        stop_distance = atr * ATR_MULT
        qty = round(risk_amount / stop_distance, 3)

        if qty <= 0:
            return {"error": "Invalid quantity"}

        # ===== PLACE MARKET ORDER =====
        order = client.place_order(
            product_id=PRODUCT_ID,
            size=qty,
            side=side,
            order_type="market"
        )

        return {
            "status": "order placed",
            "side": side,
            "quantity": qty,
            "order": order
        }

    except Exception as e:
        return {"error": str(e)}
