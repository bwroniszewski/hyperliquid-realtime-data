import asyncio
import json
import websockets
import sqlite3
import csv
import os
from datetime import datetime
import pytz
from hyperliquid.info import Info
from hyperliquid.utils import constants
from example_utils import load_config

# Define WebSocket URLs explicitly
MAINNET_WS_URL = "wss://api.hyperliquid.xyz/ws"
TESTNET_WS_URL = "wss://api.hyperliquid-testnet.xyz/ws"

def init_db(coin):
    """Initialize SQLite database for a coin with orderbook, trades, candles, asset_context, and orderbook_depth tables."""
    # Create folder for this coin
    coin_folder = f"data/{coin}"
    os.makedirs(coin_folder, exist_ok=True)
    
    # Create database in the coin folder
    db_path = os.path.join(coin_folder, f"{coin}_main_market_data.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orderbook
                 (timestamp REAL, best_bid REAL, bid_volume REAL, best_ask REAL, ask_volume REAL, mid_price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (timestamp REAL, price REAL, volume REAL, side TEXT, notional REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS candles
                 (timestamp REAL, mark_price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS asset_context
                 (timestamp REAL, oracle_price REAL, funding_rate REAL, open_interest REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orderbook_depth
                 (timestamp REAL, level INTEGER, bid_price REAL, bid_volume REAL, ask_price REAL, ask_volume REAL)''')
    conn.commit()
    conn.close()

def init_csv_files(coin):
    """Initialize CSV files for order book, trade, candle, asset context, and order book depth data."""
    # Create folder for this coin
    coin_folder = f"data/{coin}"
    os.makedirs(coin_folder, exist_ok=True)
    
    # Create CSV files in the coin folder
    with open(os.path.join(coin_folder, f"{coin}_main_orderbook.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Best Bid", "Bid Volume", "Best Ask", "Ask Volume", "Mid Price"])
    with open(os.path.join(coin_folder, f"{coin}_main_trades.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Price", "Volume", "Side", "Notional"])
    with open(os.path.join(coin_folder, f"{coin}_main_candles.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Mark Price"])
    with open(os.path.join(coin_folder, f"{coin}_main_asset_context.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Oracle Price", "Funding Rate", "Open Interest"])
    with open(os.path.join(coin_folder, f"{coin}_main_orderbook_depth.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Level", "Bid Price", "Bid Volume", "Ask Price", "Ask Volume"])

async def get_asset_id(coin, is_mainnet):
    """Retrieve the asset ID and exact coin name for a given coin."""
    api_url = constants.MAINNET_API_URL if is_mainnet else constants.TESTNET_API_URL
    info = Info(api_url, skip_ws=True)
    try:
        meta = info.meta()
        assets = meta.get("universe", [])
        if not assets:
            raise ValueError(f"No assets found in meta response for {coin}. Response: {meta}")
        for index, asset in enumerate(assets):
            if asset["name"].lower() == coin.lower():
                if asset.get("isDelisted", False):
                    raise ValueError(f"Asset '{coin}' is delisted.")
                return index, asset["name"]
        raise ValueError(f"Asset '{coin}' not found. Available assets: {[a['name'] for a in assets]}")
    except Exception as e:
        raise ValueError(f"Failed to fetch asset ID for '{coin}': {str(e)}")

async def send_ping(websocket, interval=30):
    """Send periodic ping messages to keep the WebSocket connection alive."""
    while True:
        try:
            await websocket.ping()
            print("Sent ping to server")
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Ping error: {str(e)}")
            break

async def subscribe_to_data(coins=["BTC", "ETH", "HYPE"]):
    """Subscribe to order book, trade, candle, and asset context data for specified coins."""
    config = load_config()
    is_mainnet = config["is_mainnet"]
    ws_url = MAINNET_WS_URL if is_mainnet else TESTNET_WS_URL
    print(f"Using WebSocket URL: {ws_url}")

    # Validate coins and initialize storage
    valid_coins = []
    coin_asset_map = {}
    for coin in coins:
        try:
            asset_id, exact_coin = await get_asset_id(coin, is_mainnet)
            init_db(exact_coin)
            init_csv_files(exact_coin)
            valid_coins.append(exact_coin)
            coin_asset_map[exact_coin] = asset_id
            print(f"Validated {coin} (Asset ID: {asset_id}, Exact Coin: {exact_coin})")
        except ValueError as e:
            print(f"Skipping {coin}: {e}")
            continue

    if not valid_coins:
        print("No valid coins to subscribe to. Exiting.")
        return

    orderbook_rows = {coin: [] for coin in valid_coins}
    orderbook_depth_rows = {coin: [] for coin in valid_coins}
    trade_rows = {coin: [] for coin in valid_coins}
    candle_rows = {coin: [] for coin in valid_coins}
    asset_ctx_rows = {coin: [] for coin in valid_coins}
    error_count = 0
    max_errors = 5

    while True:
        ping_task = None
        try:
            async with websockets.connect(ws_url, ping_interval=None) as websocket:
                ping_task = asyncio.create_task(send_ping(websocket, interval=30))

                for coin in valid_coins:
                    # Subscribe to L2 order book
                    subscription_l2 = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "l2Book",
                            "coin": coin
                        }
                    }
                    await websocket.send(json.dumps(subscription_l2))
                    # Subscribe to trades
                    subscription_trades = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "trades",
                            "coin": coin
                        }
                    }
                    await websocket.send(json.dumps(subscription_trades))
                    # Subscribe to candles (1m interval for mark price)
                    subscription_candle = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "candle",
                            "coin": coin,
                            "interval": "1m"
                        }
                    }
                    await websocket.send(json.dumps(subscription_candle))
                    # Subscribe to asset context (oracle price, funding rate, open interest)
                    subscription_asset_ctx = {
                        "method": "subscribe",
                        "subscription": {
                            "type": "activeAssetCtx",
                            "coin": coin
                        }
                    }
                    await websocket.send(json.dumps(subscription_asset_ctx))
                    print(f"Subscribed to L2 order book, trades, candles, and activeAssetCtx for {coin} (Asset ID: {coin_asset_map[coin]})")
                    await asyncio.sleep(1)

                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=60)
                        data = json.loads(message)
                        print(f"Received message: {data}")
                        cest = pytz.timezone("Europe/Paris")
                        cest_timestamp = datetime.now(cest).timestamp()

                        if data.get("channel") == "l2Book":
                            book_data = data.get("data", {})
                            coin = book_data.get("coin", "Unknown")
                            if coin not in valid_coins:
                                print(f"Ignoring l2Book data for untracked coin: {coin}")
                                continue
                            levels = book_data.get("levels", [])
                            bids = levels[0] if len(levels) > 0 else []
                            asks = levels[1] if len(levels) > 1 else []
                            print(f"Parsed l2Book data for {coin}: bids={bids[:5]}... asks={asks[:5]}...")
                            if bids and asks:
                                best_bid = float(bids[0]['px'])
                                best_ask = float(asks[0]['px'])
                                bid_volume = float(bids[0]['sz'])
                                ask_volume = float(asks[0]['sz'])
                                mid_price = (best_bid + best_ask) / 2
                                print(f"{coin} Order Book - Best Bid: {best_bid}, Volume: {bid_volume}")
                                print(f"{coin} Order Book - Best Ask: {best_ask}, Volume: {ask_volume}")
                                print(f"{coin} Mid Price: {mid_price}")
                                orderbook_rows[coin].append((cest_timestamp, best_bid, bid_volume, best_ask, ask_volume, mid_price))
                                for i in range(min(5, len(bids), len(asks))):
                                    bid_price = float(bids[i]['px'])
                                    bid_volume = float(bids[i]['sz'])
                                    ask_price = float(asks[i]['px'])
                                    ask_volume = float(asks[i]['sz'])
                                    orderbook_depth_rows[coin].append((cest_timestamp, i+1, bid_price, bid_volume, ask_price, ask_volume))
                                # Batch write to database
                                db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                                conn = sqlite3.connect(db_path)
                                c = conn.cursor()
                                if len(orderbook_rows[coin]) >= 100:
                                    c.executemany("INSERT INTO orderbook VALUES (?, ?, ?, ?, ?, ?)", orderbook_rows[coin])
                                    c.executemany("INSERT INTO orderbook_depth VALUES (?, ?, ?, ?, ?, ?)", orderbook_depth_rows[coin])
                                    conn.commit()
                                    orderbook_rows[coin].clear()
                                    orderbook_depth_rows[coin].clear()
                                conn.close()
                                # Write to CSV
                                with open(os.path.join(f"data/{coin}", f"{coin}_main_orderbook.csv"), "a", newline="") as f:
                                    writer = csv.writer(f)
                                    writer.writerow([cest_timestamp, best_bid, bid_volume, best_ask, ask_volume, mid_price])
                                with open(os.path.join(f"data/{coin}", f"{coin}_main_orderbook_depth.csv"), "a", newline="") as f:
                                    writer = csv.writer(f)
                                    for i in range(min(5, len(bids), len(asks))):
                                        writer.writerow([cest_timestamp, i+1, float(bids[i]['px']), float(bids[i]['sz']), float(asks[i]['px']), float(asks[i]['sz'])])

                        elif data.get("channel") == "trades":
                            trades = data.get("data", [])
                            coin = trades[0].get("coin", "Unknown") if trades else "Unknown"
                            if coin not in valid_coins:
                                print(f"Ignoring trades data for untracked coin: {coin}")
                                continue
                            for trade in trades:
                                price = float(trade["px"])
                                volume = float(trade["sz"])
                                side = "Buy" if trade["side"] == "B" else "Sell"
                                notional = price * volume
                                print(f"{coin} Trade - Price: {price}, Volume: {volume}, Side: {side}, Notional: {notional}")
                                trade_rows[coin].append((cest_timestamp, price, volume, side, notional))
                                db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                                conn = sqlite3.connect(db_path)
                                c = conn.cursor()
                                if len(trade_rows[coin]) >= 100:
                                    c.executemany("INSERT INTO trades VALUES (?, ?, ?, ?, ?)", trade_rows[coin])
                                    conn.commit()
                                    trade_rows[coin].clear()
                                conn.close()
                                with open(os.path.join(f"data/{coin}", f"{coin}_main_trades.csv"), "a", newline="") as f:
                                    writer = csv.writer(f)
                                    writer.writerow([cest_timestamp, price, volume, side, notional])

                        elif data.get("channel") == "candle":
                            candle_data = data.get("data", {})
                            coin = candle_data.get("s", "Unknown")
                            if coin not in valid_coins:
                                print(f"Ignoring candle data for untracked coin: {coin}")
                                continue
                            mark_price = float(candle_data.get("c", 0))
                            print(f"{coin} Candle - Mark Price: {mark_price}")
                            candle_rows[coin].append((cest_timestamp, mark_price))
                            db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                            conn = sqlite3.connect(db_path)
                            c = conn.cursor()
                            if len(candle_rows[coin]) >= 100:
                                c.executemany("INSERT INTO candles VALUES (?, ?)", candle_rows[coin])
                                conn.commit()
                                candle_rows[coin].clear()
                            conn.close()
                            with open(os.path.join(f"data/{coin}", f"{coin}_main_candles.csv"), "a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([cest_timestamp, mark_price])

                        elif data.get("channel") == "activeAssetCtx":
                            ctx_data = data.get("data", {})
                            coin = ctx_data.get("coin", "Unknown")
                            if coin not in valid_coins:
                                print(f"Ignoring activeAssetCtx data for untracked coin: {coin}")
                                continue
                            ctx = ctx_data.get("ctx", {})
                            try:
                                oracle_price = float(ctx.get("oraclePx", 0))
                                funding_rate = float(ctx.get("funding", 0))
                                open_interest = float(ctx.get("openInterest", 0))
                            except (ValueError, TypeError) as e:
                                print(f"Error parsing activeAssetCtx data for {coin}: {str(e)}. Data: {ctx}")
                                continue
                            print(f"{coin} Asset Context - Oracle Price: {oracle_price}, Funding Rate: {funding_rate}, Open Interest: {open_interest}")
                            asset_ctx_rows[coin].append((cest_timestamp, oracle_price, funding_rate, open_interest))
                            db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                            conn = sqlite3.connect(db_path)
                            c = conn.cursor()
                            if len(asset_ctx_rows[coin]) >= 100:
                                c.executemany("INSERT INTO asset_context VALUES (?, ?, ?, ?)", asset_ctx_rows[coin])
                                conn.commit()
                                asset_ctx_rows[coin].clear()
                            conn.close()
                            with open(os.path.join(f"data/{coin}", f"{coin}_main_asset_context.csv"), "a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([cest_timestamp, oracle_price, funding_rate, open_interest])

                        elif data.get("channel") == "subscriptionResponse":
                            print(f"Subscription confirmed: {data.get('data', {})}")

                        elif data.get("channel") == "error":
                            print(f"Error from server: {data.get('data', 'Unknown error')}")
                            error_count += 1
                            if error_count >= max_errors:
                                print("Too many errors. Terminating...")
                                return

                    except asyncio.TimeoutError:
                        print("No message received within 60 seconds. Sending ping...")
                        await websocket.ping()

                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
                        error_count += 1
                        if error_count >= max_errors:
                            print("Too many errors. Terminating...")
                            return

        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {str(e)}. Reconnecting in 5 seconds...")
            if ping_task:
                ping_task.cancel()
            for coin in valid_coins:
                db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                if orderbook_rows[coin]:
                    c.executemany("INSERT INTO orderbook VALUES (?, ?, ?, ?, ?, ?)", orderbook_rows[coin])
                if orderbook_depth_rows[coin]:
                    c.executemany("INSERT INTO orderbook_depth VALUES (?, ?, ?, ?, ?, ?)", orderbook_depth_rows[coin])
                if trade_rows[coin]:
                    c.executemany("INSERT INTO trades VALUES (?, ?, ?, ?, ?)", trade_rows[coin])
                if candle_rows[coin]:
                    c.executemany("INSERT INTO candles VALUES (?, ?)", candle_rows[coin])
                if asset_ctx_rows[coin]:
                    c.executemany("INSERT INTO asset_context VALUES (?, ?, ?, ?)", asset_ctx_rows[coin])
                conn.commit()
                conn.close()
                orderbook_rows[coin].clear()
                orderbook_depth_rows[coin].clear()
                trade_rows[coin].clear()
                candle_rows[coin].clear()
                asset_ctx_rows[coin].clear()
            await asyncio.sleep(5)

        except Exception as e:
            print(f"Unexpected error: {str(e)}. Reconnecting in 5 seconds...")
            if ping_task:
                ping_task.cancel()
            for coin in valid_coins:
                db_path = os.path.join(f"data/{coin}", f"{coin}_main_market_data.db")
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                if orderbook_rows[coin]:
                    c.executemany("INSERT INTO orderbook VALUES (?, ?, ?, ?, ?, ?)", orderbook_rows[coin])
                if orderbook_depth_rows[coin]:
                    c.executemany("INSERT INTO orderbook_depth VALUES (?, ?, ?, ?, ?, ?)", orderbook_depth_rows[coin])
                if trade_rows[coin]:
                    c.executemany("INSERT INTO trades VALUES (?, ?, ?, ?, ?)", trade_rows[coin])
                if candle_rows[coin]:
                    c.executemany("INSERT INTO candles VALUES (?, ?)", candle_rows[coin])
                if asset_ctx_rows[coin]:
                    c.executemany("INSERT INTO asset_context VALUES (?, ?, ?, ?)", asset_ctx_rows[coin])
                conn.commit()
                conn.close()
                orderbook_rows[coin].clear()
                orderbook_depth_rows[coin].clear()
                trade_rows[coin].clear()
                candle_rows[coin].clear()
                asset_ctx_rows[coin].clear()
            await asyncio.sleep(5)

def main():
    """Main function to run the data collection."""
    print("Starting Hyperliquid Real-Time Data Collection...")
    print("Press Ctrl+C to stop the collection.")
    try:
        asyncio.run(subscribe_to_data(coins=["BTC", "ETH", "HYPE"]))
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()