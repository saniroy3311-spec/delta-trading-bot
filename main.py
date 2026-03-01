from fastapi import FastAPI, Request
from delta_rest_client import DeltaRestClient
import os

app = FastAPI()

# Get API keys from Railway variables
API_KEY = os.getenv("DELTA_API_KEY")
API_SECRET = os.getenv("DELTA_API_SECRET")

# Connect to Delta Exchange (LIVE)
client = DeltaRestClient(
    base_url="https://api.delta.exchange",
    api_key=API_KEY,
    api_secret=API_SECRET
)

# Default values (safe if variables not set)
CAPITAL = float(os.getenv("CAPITAL", 3000))
RISK_PCT = float(os.getenv("RISK_PCT", 0.003))
ATR_MULT = float(os.getenv("ATR_MULT", 1.2))

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    side = data["side"]          # BUY or SELL
    price = float(data["price"])
    atr = float(data["atr"])

    # Risk calculation
    risk_amount = CAPITAL * RISK_PCT
    stop_distance = atr * ATR_MULT
    qty = round(risk_amount / stop_distance, 3)

    # Place market order
    client.place_order(
        product_id="BTCUSDT",
        size=qty,
        side=side.lower(),
        order_type="market"
    )

    return {"status": "order placed", "quantity": qty}
