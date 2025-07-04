# Folder Structure and Organization

## Project Structure

```
hyperliquid-realtime-data/
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── SECURITY.md                 # Security guidelines
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation
├── config.example.json         # Example configuration
├── .gitignore                  # Git ignore rules
├── example_utils.py            # Configuration utilities
├── realtime_data_2.py          # Main data collection script
├── create_data_structure.py    # Demo folder creation
├── view_data.py                # Data viewer utility
└── data/                       # Data storage (created at runtime)
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

## File Descriptions

### Core Files
- **`realtime_data_2.py`**: Main script that collects real-time data from Hyperliquid
- **`example_utils.py`**: Configuration loading utilities with environment variable support
- **`config.example.json`**: Template for user configuration (safe to commit)

### Documentation
- **`README.md`**: Comprehensive project documentation
- **`QUICKSTART.md`**: 5-minute quick start guide
- **`SECURITY.md`**: Security best practices and guidelines
- **`LICENSE`**: MIT License for open source distribution

### Configuration
- **`requirements.txt`**: Python package dependencies
- **`setup.py`**: Package installation configuration
- **`.gitignore`**: Git ignore rules for security

### Utility Scripts
- **`create_data_structure.py`**: Creates demo folder structure
- **`view_data.py`**: Interactive data viewer for collected data

## Data Organization

### Folder Structure
Each cryptocurrency gets its own folder under `data/`:
```
data/
├── {COIN_NAME}/
│   ├── {COIN_NAME}_main_market_data.db    # SQLite database
│   ├── {COIN_NAME}_main_orderbook.csv     # Order book data
│   ├── {COIN_NAME}_main_trades.csv        # Trade data
│   ├── {COIN_NAME}_main_candles.csv       # Candle/mark price data
│   ├── {COIN_NAME}_main_asset_context.csv # Asset context data
│   └── {COIN_NAME}_main_orderbook_depth.csv # Order book depth
```

### Data Files
- **Database**: SQLite database with all data types
- **CSV Files**: Individual CSV files for each data type
- **Automatic Creation**: Folders and files are created automatically when the script runs

## Security Features

### Protected Files
- `config.json` (user credentials) - gitignored
- `data/` folder - gitignored
- All `*.db` files - gitignored
- All `*_main_*.csv` files - gitignored

### Safe to Commit
- All documentation files
- Example configuration
- Source code
- Utility scripts

## Usage Workflow

1. **Setup**: Copy `config.example.json` to `config.json` and add credentials
2. **Run**: Execute `python realtime_data_2.py`
3. **Monitor**: Data is automatically organized in `data/{coin}/` folders
4. **View**: Use `python view_data.py` to inspect collected data
5. **Analyze**: Access CSV files or SQLite databases for analysis

## Benefits of This Structure

### Organization
- **Clean Separation**: Each coin has its own folder
- **Easy Navigation**: Clear file naming conventions
- **Scalable**: Easy to add new coins

### Security
- **Credential Protection**: Sensitive files are gitignored
- **Environment Variables**: Support for secure credential storage
- **Clear Guidelines**: Security documentation included

### Usability
- **Self-Documenting**: Clear folder structure
- **Utility Scripts**: Built-in tools for data viewing
- **Comprehensive Docs**: Multiple documentation levels

## GitHub Publication Ready

This structure is optimized for GitHub publication:
- ✅ All essential files included
- ✅ Security measures implemented
- ✅ Clear documentation
- ✅ Professional organization
- ✅ Easy to understand and use 