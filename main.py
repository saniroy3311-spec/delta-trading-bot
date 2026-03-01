from fastapi import FastAPI, Request
from delta_rest_client import DeltaRestClient
import os

app = FastAPI()

# Required API keys
API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

client = DeltaRestClient(
    api_key=API_KEY,
    api_secret=API_SECRET
)

# Safe defaults (won’t crash)
CAPITAL = float(os.getenv("CAPITAL", 3000))
RISK_PCT = float(os.getenv("RISK_PCT", 0.003))
ATR_MULT = float(os.getenv("ATR_MULT", 1.2))

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    side = data["side"]
    price = float(data["price"])
    atr = float(data["atr"])

    risk_amount = CAPITAL * RISK_PCT
    stop_distance = atr * ATR_MULT
    qty = round(risk_amount / stop_distance, 3)

    client.place_order(
        product_id="BTCUSDT",
        size=qty,
        side=side.lower(),
        order_type="market"
    )

    return {"status": "order placed"}
