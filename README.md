# Binance Futures Trading Terminal

## Overview
The Binance Futures Trading Terminal is a professional-grade, locally-hosted algorithmic trading interface built for the Binance Futures Testnet. It features a robust Python backend service layer interacting with the Binance API, and offers two distinct user interfaces: a fast, interactive Command Line Interface (CLI) for terminal users and a sleek, comprehensive Streamlit web dashboard for visual traders.

This project emphasizes clean architecture, strong typing, and comprehensive error handling to ensure reliable trade execution and portfolio monitoring.

## Features
- **Credential Verification**: Securely test and validate your API keys and Futures permissions before risking capital or encountering API rejections.
- **Market Orders**: Instantly execute trades at the best available market price.
- **Limit Orders**: Set specific price points for entry or exit.
- **Stop Limit Orders**: Protect your capital or catch breakouts with conditional limit orders triggered by stop prices.
- **Open Orders Management**: View all active orders and seamlessly cancel them individually.
- **Order History**: Access your historical ledger of trades, fully filterable and exportable.
- **Live BTC Price Widget**: Real-time ticker and candlestick charting utilizing Plotly.
- **Streamlit Dashboard**: A responsive, TradingView-inspired local web UI offering comprehensive market analytics and a user-friendly execution terminal.
- **Logging**: Production-ready rotating file logging (`logs/trading.log`) capturing detailed lifecycle events of every order.
- **Validation**: Strict input validation layer guarding against malformed requests prior to API transmission.
- **Error Handling**: Graceful degradation and human-readable feedback on network failures, API errors, and testnet limitations.

## Architecture
The application employs a layered architecture separating concerns for maintainability and scalability:

**User Interfaces (CLI / Streamlit)** 
&rarr; **Service Layer (`OrderService`)**: Handles business logic, validation coordination, and standardizes data models.
&rarr; **Binance Client Wrapper (`BinanceFuturesClient`)**: Manages authentication, connection state, and raw API communication.
&rarr; **Binance Futures Testnet**: The remote exchange environment.

## Project Structure
```text
trading_bot/
├── .env.example          # Template for environment variables
├── .gitignore            # Ignored files (logs, pycache, .env)
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License
├── app.py                # Streamlit Web Application
├── cli.py                # Command Line Interface Application
├── screenshots/          # Documentation screenshots
├── logs/                 # Directory containing rotating logs (auto-generated)
│   └── trading.log
└── bot/                  # Core Service Layer
    ├── __init__.py
    ├── client.py         # Binance API wrapper
    ├── config.py         # Centralized configuration
    ├── constants.py      # Enums and fixed values
    ├── logging_config.py # Structured logging setup
    ├── models.py         # Strongly-typed data models (OrderResponse)
    ├── orders.py         # OrderService business logic
    └── validators.py     # Strict input validation logic
```

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/binance-futures-trading-bot.git
cd binance-futures-trading-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Environment Setup
The bot requires Binance Futures Testnet API credentials.
Create a `.env` file in the root directory based on the `.env.example`:

```bash
# .env
API_KEY=your_testnet_api_key_here
API_SECRET=your_testnet_api_secret_here
TESTNET=True
```

## Running CLI
The CLI provides an interactive menu or automated command-line execution.

**Verify Credentials:**
```bash
python cli.py --verify-credentials
```

**Market Order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit Order:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 4000
```

**Stop Limit Order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 60000 --stop-price 60500
```

**Interactive Mode:**
```bash
python cli.py
```

## Running Web UI
Launch the interactive Streamlit dashboard:

```bash
streamlit run app.py
```

## Screenshots
### Market Dashboard
![Market Dashboard](screenshots/dashboard.png)

### Order Execution Terminal
![Market Order](screenshots/market_order.png)

### Order History & Analytics
![Order History](screenshots/order_history.png)

## Logging
All system events, validation checks, and API responses are securely logged using a rotating file handler located at `logs/trading.log`. This file ensures long-term traceability and simplifies debugging for complex trading sequences without cluttering the console output.

## Security
- **.env Handling**: API keys are injected via environment variables using `python-dotenv`. The `.env` file is explicitly ignored in `.gitignore` to prevent accidental credential leakage.
- **Local Execution**: The application runs entirely on your local machine, ensuring API keys never leave your system except during encrypted API calls to Binance.
- **Permissions Validation**: Pre-flight checks ensure the provided keys have the correct permissions to avoid mid-trade rejections.

## Future Improvements
- **Automated Trading Strategies**: Implementation of a strategy engine for moving average crossovers or RSI-based algorithms.
- **WebSocket Integration**: Transition from REST API polling to real-time WebSockets for sub-millisecond price updates and instant order fill notifications.
- **Unit & Integration Testing**: Achieve high test coverage using `pytest` and mocked API responses.
- **Dockerization**: Provide a `Dockerfile` and `docker-compose.yml` for isolated deployment.
- **Multi-Exchange Support**: Abstract the client interface to support additional exchanges seamlessly.
