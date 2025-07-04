# Quick Start Guide

Get up and running with the Hyperliquid Real-Time Data Collector in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- Hyperliquid account
- API wallet credentials from [Hyperliquid API Management](https://app.hyperliquid.xyz/API)

## Step 1: Clone and Install

```bash
git clone <your-repo-url>
cd hyperliquid-realtime-data
pip install -r requirements.txt
```

## Step 2: Get API Credentials

First, create an API wallet at [https://app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API):

1. **Connect your main wallet** to Hyperliquid
2. **Generate API wallet** with a descriptive name
3. **Authorize the API wallet** (sign transaction with main wallet)
4. **Copy the private key** and store it securely

**Important**: Use your **main wallet address** as `account_address` and the **API wallet's private key** as `secret_key`.

### Option A: Environment Variables (Recommended)
```bash
export HYPERLIQUID_ACCOUNT_ADDRESS="0xYourMainWalletAddress"
export HYPERLIQUID_SECRET_KEY="YourAPIWalletPrivateKey"
export HYPERLIQUID_IS_MAINNET="true"
```

### Option B: Config File
```bash
cp config.example.json config.json
# Edit config.json with your credentials:
# - account_address: Your main wallet address
# - secret_key: Your API wallet's private key
```

## Step 3: Choose Your Assets

Before running, you can customize which cryptocurrencies to track by editing `realtime_data_HL.py` and adding tickers:

```python
# Open realtime_data_HL.py and find line 376 (main function)
asyncio.run(subscribe_to_data(coins=["BTC", "ETH", "HYPE"]))  # Add your preferred coins here

# Or edit the function definition around line 75
async def subscribe_to_data(coins=["BTC", "ETH", "HYPE"]):  # Default coin list
```

**Available Assets**: The script automatically validates against Hyperliquid's available assets.

**Note**: Be mindful of API rate limits when tracking many assets simultaneously.

## Step 4: Run the Data Collector

```bash
python realtime_data_HL.py
```

## Step 5: Monitor Output

The script will:
- Connect to Hyperliquid WebSocket
- Subscribe to your chosen assets within the API limitations
- Create database and CSV files
- Display real-time data in console

## Important: Data Collection Behavior

⚠️ **Data Collection is Session-Based**:
- **Data is only collected while the script is running**
- **When you stop the script (Ctrl+C), data collection stops**
- **CSV files are saved with data from the last session**
- **When you restart the script, CSV files are overwritten (not appended)**

### To Preserve Your Data:
1. **Copy CSV files** to a backup location before stopping the script
2. **Use the SQLite databases** - they persist data between sessions
3. **Create regular backups** of your `data/` folder

**Example backup command:**
```bash
# Before stopping the script, backup your data
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)/
```

## Expected Output

```
Using WebSocket URL: wss://api.hyperliquid.xyz/ws
Validated ETH (Asset ID: 0, Exact Coin: ETH)
Validated HYPE (Asset ID: 1, Exact Coin: HYPE)
...
Subscribed to L2 order book, trades, candles, and activeAssetCtx for ETH
ETH Order Book - Best Bid: 3456.78, Volume: 1.5
ETH Order Book - Best Ask: 3457.12, Volume: 2.1
ETH Mid Price: 3456.95
```

## Generated Files

For each coin, you'll get a dedicated folder in `data/{coin}/` containing:
- `{coin}_main_market_data.db` (SQLite database)
- `{coin}_main_orderbook.csv`
- `{coin}_main_trades.csv`
- `{coin}_main_candles.csv`
- `{coin}_main_asset_context.csv`
- `{coin}_main_orderbook_depth.csv`

Example structure:
```
data/
├── ETH/
│   ├── ETH_main_market_data.db
│   ├── ETH_main_orderbook.csv
│   └── ...
├── HYPE/
│   ├── HYPE_main_market_data.db
│   └── ...
└── ...
```

## Advanced Customization

### Switch to Testnet
Set environment variable:
```bash
export HYPERLIQUID_IS_MAINNET="false"
```

Or edit config.json:
```json
{
    "is_mainnet": false
}
```

### Add More Assets
If you want to add more assets after initial setup, simply edit the coin list in `realtime_data_HL.py` and restart the script. The script will automatically:
- Validate new assets against Hyperliquid's API
- Create new data folders for each asset
- Start collecting data for the new assets

**Note**: Restarting the script will overwrite existing CSV files, but SQLite databases will retain previous data.

## Troubleshooting

### "Asset not found" Error
- Check coin names are correct
- Verify coins exist on Hyperliquid
- Try with testnet first

### Connection Issues
- Check internet connection
- Verify credentials are correct
- Ensure Hyperliquid API is accessible

### Permission Errors
- Ensure write permissions in directory
- Check if files are locked

## Next Steps

1. **Analyze Data**: Use the generated CSV files for analysis
2. **Database Queries**: Query the SQLite databases (data persists between sessions)
3. **Custom Scripts**: Build on top of the collected data
4. **Visualization**: Create charts and dashboards
5. **Data Backup**: Regularly backup your CSV files to preserve historical data

## Need Help?

- Check the full [README.md](README.md)
- Review [SECURITY.md](SECURITY.md) for security best practices
- Open an issue on GitHub

## Security Reminder

⚠️ **Never share your private key!** Keep your credentials secure and never commit them to version control.

### API Wallet Security:
- **Main wallet**: Used for authorization (account_address)
- **API wallet**: Used for trading (secret_key)
- **Validity period**: API keys expire (max 180 days)
- **Regeneration**: Remember to regenerate before expiration 