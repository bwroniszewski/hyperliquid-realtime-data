# Hyperliquid Real-Time Market Data Collector

A Python application that collects real-time market data from Hyperliquid exchange via WebSocket connections. This tool subscribes to order book, trades, candles, and asset context data for multiple cryptocurrencies and stores the data in both SQLite databases and CSV files.

## Features

- **Real-time Data Collection**: Subscribe to multiple data streams simultaneously
- **Multiple Data Types**: 
  - Order book data (L2 depth)
  - Trade data (executed trades)
  - Candle data (mark prices)
  - Asset context (oracle prices, funding rates, open interest)
- **Dual Storage**: Data stored in both SQLite databases and CSV files
- **Multi-Asset Support**: Track multiple cryptocurrencies simultaneously
- **Automatic Reconnection**: Handles connection drops with automatic reconnection
- **Batch Processing**: Efficient batch writes to database for better performance
- **Error Handling**: Robust error handling with configurable retry limits

## Prerequisites

- Python 3.7+
- Hyperliquid account with API access
- Required Python packages (see `requirements.txt`)

## Getting Your API Credentials

Before running the script, you need to create an API wallet and get your credentials from the [Hyperliquid API Management Page](https://app.hyperliquid.xyz/API).

### Steps to Create an API Wallet:

1. **Navigate to API Management**:
   - Go to [https://app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API)
   - Connect your main wallet (e.g., MetaMask) to Hyperliquid

2. **Generate API Wallet**:
   - Enter a descriptive name for your API wallet (e.g., "MyTradingBot")
   - Click "Generate" to create a new API wallet
   - This generates a wallet address and private key

3. **Authorize the API Wallet**:
   - Click "Authorize API Wallet"
   - Sign the transaction with your main wallet
   - Set validity period (up to 180 days maximum)

4. **Securely Store Credentials**:
   - Copy the displayed private key
   - Store it securely (encrypted file or password manager)
   - **Never share or commit this key to code**

### Important Notes:
- Use your **main wallet address** as `account_address` (not the API wallet address)
- Use the **API wallet's private key** as `secret_key`
- The main wallet authorizes the API wallet for trading

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd hyperliquid-realtime-data
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**:
   - Copy `config.example.json` to `config.json`
   - Edit `config.json` with your Hyperliquid credentials:
     ```json
     {
         "account_address": "your_main_wallet_address",
         "secret_key": "your_api_wallet_private_key",
         "is_mainnet": true
     }
     ```

## Configuration

### config.json
```json
{
    "account_address": "0x...",
    "secret_key": "your_private_key_here",
    "is_mainnet": true
}
```

**Security Note**: Never commit your `config.json` file to version control. It's already included in `.gitignore`.

### Environment Variables (Alternative)
You can also use environment variables instead of config.json:
```bash
export HYPERLIQUID_ACCOUNT_ADDRESS="your_wallet_address"
export HYPERLIQUID_SECRET_KEY="your_private_key"
export HYPERLIQUID_IS_MAINNET="true"
```

## Usage

### Basic Usage
```bash
python realtime_data_HL.py
```

The script:
- Connects to the Hyperliquid WebSocket (wss://api.hyperliquid.xyz/ws or testnet equivalent).
- Validates coins and subscribes to their data streams.
- Stores data in data/{coin}/ folders as SQLite databases and CSV files.

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


### Custom Coin List
You can easily customize which coins to track by editing the coin list in `realtime_data_HL.py`:

```python
# In realtime_data_HL.py, line 376 (main function)
asyncio.run(subscribe_to_data(coins=["BTC", "ETH", "HYPE"]))

# Or in the function definition (line 75)
async def subscribe_to_data(coins=["BTC", "ETH", "HYPE"]):
```

**Examples of custom coin lists:**
```python
# Track only major coins
coins=["BTC", "ETH"]

# Track specific meme coins
coins=["HYPE", "FARTCOIN", "kPEPE", "WIF"]

# Track all available coins (within API limits)
coins=["BTC", "ETH", "HYPE", "SOL", "FARTCOIN", "SUI", "SEI", "kPEPE", "WIF", "AAVE", "APT", "CRV", "MATIC", "LINK"]
```

### Available Coins
The script automatically validates coins against the Hyperliquid API. 

**API Limitations**: Be mindful of Hyperliquid's API rate limits and connection limits when adding many coins simultaneously.

## Data Output

### Data Organization
All data is organized in a `data/` folder with subfolders for each coin:

```
data/
├── ETH/
│   ├── ETH_main_market_data.db
│   ├── ETH_main_orderbook.csv
│   ├── ETH_main_trades.csv
│   ├── ETH_main_candles.csv
│   ├── ETH_main_asset_context.csv
│   └── ETH_main_orderbook_depth.csv
├── HYPE/
│   ├── HYPE_main_market_data.db
│   ├── HYPE_main_orderbook.csv
│   └── ...
└── ...
```

### SQLite Databases
For each coin, a database file is created: `data/{coin}/{coin}_main_market_data.db`

**Tables**:
- `orderbook`: Best bid/ask prices and volumes
- `trades`: Executed trades with price, volume, side
- `candles`: Mark prices over time
- `asset_context`: Oracle prices, funding rates, open interest
- `orderbook_depth`: Full order book depth (top 5 levels)

**Important**: SQLite databases persist data between script sessions, unlike CSV files which are overwritten on restart.

### CSV Files
For each coin, CSV files are created in `data/{coin}/`:
- `{coin}_main_orderbook.csv`
- `{coin}_main_trades.csv`
- `{coin}_main_candles.csv`
- `{coin}_main_asset_context.csv`
- `{coin}_main_orderbook_depth.csv`

**Note**: CSV files are overwritten each time the script starts. To preserve historical data, backup these files before stopping the script.

## Data Schema

### Order Book Data
- `timestamp`: Unix timestamp
- `best_bid`: Best bid price
- `bid_volume`: Volume at best bid
- `best_ask`: Best ask price
- `ask_volume`: Volume at best ask
- `mid_price`: Mid price ((best_bid + best_ask) / 2)

### Trade Data
- `timestamp`: Unix timestamp
- `price`: Trade price
- `volume`: Trade volume
- `side`: "Buy" or "Sell"
- `notional`: Price × Volume

### Asset Context Data
- `timestamp`: Unix timestamp
- `oracle_price`: Oracle price
- `funding_rate`: Current funding rate
- `open_interest`: Open interest

### The current script collects data for perpetual assets using WebSocket channels (l2Book, trades, candle, activeAssetCtx). To collect spot market data:

Modify Subscriptions in realtime_data_2.py:

Replace l2Book with spotL2Book for spot order book data.
Replace trades with spotTrades for spot trade data.

Note: candle and activeAssetCtx are not available for spot assets.

Update Coin Names:

Use spot pair names (e.g., PURR/USDC) from the spotMeta.universe field in the meta endpoint.

Example Modification (in subscribe_to_data function):

Update Asset ID Validation:
Modify get_asset_id to check spotMeta.universe and return 10000 + index.

Note: Spot data storage can reuse the existing orderbook, trades, and orderbook_depth tables, but you may want to create separate tables (e.g., spot_orderbook) for clarity.

## Security Considerations

⚠️ **IMPORTANT**: This application requires your private key to access Hyperliquid APIs.

### Security Best Practices:
1. **Never commit credentials**: The `config.json` file is gitignored
2. **Use environment variables**: Consider using environment variables instead of config files
3. **Restrict file permissions**: Ensure config files have restricted permissions
4. **Use dedicated wallets**: Consider using a dedicated wallet for API access
5. **Monitor usage**: Regularly check your API usage and wallet activity

### Alternative: Environment Variables
You can modify `example_utils.py` to use environment variables:
```python
import os

def load_config():
    return {
        "account_address": os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS"),
        "secret_key": os.getenv("HYPERLIQUID_SECRET_KEY"),
        "is_mainnet": os.getenv("HYPERLIQUID_IS_MAINNET", "true").lower() == "true"
    }
```

## Error Handling

The application includes robust error handling:
- **Connection drops**: Automatic reconnection with 5-second delays
- **Invalid coins**: Skips invalid coins and continues with valid ones
- **Data parsing errors**: Logs errors and continues processing
- **Rate limiting**: Built-in delays between operations

## Monitoring

The application provides real-time logging:
- Connection status
- Data reception confirmations
- Error messages
- Data processing statistics

## Troubleshooting

### Common Issues

1. **"Asset not found" errors**:
   - Check coin names are correct
   - Verify coins are available on Hyperliquid
   - Check if using mainnet vs testnet

2. **Connection issues**:
   - Verify internet connection
   - Check Hyperliquid API status
   - Ensure credentials are correct

3. **Permission errors**:
   - Ensure write permissions in the directory
   - Check if files are locked by other processes

### Logs
The application provides detailed console output for debugging.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational and research purposes. Use at your own risk. The authors are not responsible for any financial losses or damages resulting from the use of this software.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information

## Acknowledgments

- Hyperliquid team for providing the API
- Python community for the excellent libraries used