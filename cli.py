import argparse
import sys
import logging

from bot.client import BinanceFuturesClient
from bot.orders import OrderService, OrderServiceError
from bot.logging_config import setup_logging
from bot.constants import OrderSide, OrderType

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, FloatPrompt
    from rich import box
except ImportError:
    print("Please install the 'rich' library: pip install rich")
    sys.exit(1)

console = Console()

def run_automated_mode(args, logger):
    """Executes the CLI in automated mode using argparse."""
    try:
        # Handle the new connection test feature
        if args.test_connection:
            print("\n🔄 Testing connection to Binance Futures Testnet...")
            client = BinanceFuturesClient()
            if client.test_connection():
                print("\n✅ CONNECTION SUCCESS: Securely connected to Binance Futures Testnet using your credentials.\n")
                sys.exit(0)
            else:
                print("\n❌ CONNECTION FAILED: Could not connect to Binance Futures Testnet. Please check your .env credentials or internet connection.\n")
                sys.exit(1)

        # Handle deep credential verification
        if args.verify_credentials:
            print("\n🔐 Verifying API Keys and Futures Permissions...")
            client = BinanceFuturesClient()
            status = client.verify_credentials()
            
            print("\n" + "=" * 55)
            print(" 🛡️  CREDENTIAL VERIFICATION STATUS")
            print("=" * 55)
            print(f"  Account Reachable   : {'✅ YES' if status['account_reachable'] else '❌ NO'}")
            print(f"  API Key Valid       : {'✅ YES' if status['api_key_valid'] else '❌ NO'}")
            print(f"  Secret Key Valid    : {'✅ YES' if status['secret_key_valid'] else '❌ NO'}")
            print(f"  Futures Permissions : {'✅ YES' if status['futures_permissions'] else '❌ NO'}")
            print("=" * 55 + "\n")
            
            if status['api_key_valid'] and status['secret_key_valid'] and status['futures_permissions']:
                print("✅ ALL CHECKS PASSED: Your keys are perfectly configured for Futures trading.\n")
                sys.exit(0)
            else:
                print("❌ VERIFICATION FAILED: Please check your API keys and ensure 'Enable Futures' is checked in your API management settings.\n")
                sys.exit(1)

        # If not testing connection, enforce the standard trading arguments manually
        missing_args = []
        if not args.symbol: missing_args.append("--symbol")
        if not args.side: missing_args.append("--side")
        if not args.type: missing_args.append("--type")
        if not args.quantity: missing_args.append("--quantity")

        if missing_args:
            print(f"The following arguments are required for placing an order: {', '.join(missing_args)}\nAlternatively, use --test-connection to verify your keys.")
            sys.exit(1)

        # Enforce price argument strictly for LIMIT and STOP_LIMIT orders
        if args.type in ("LIMIT", "STOP_LIMIT") and args.price is None:
            print(f"--price is required for {args.type} orders.")
            sys.exit(1)
            
        if args.type == "STOP_LIMIT" and args.stop_price is None:
            print("--stop-price is required for STOP_LIMIT orders.")
            sys.exit(1)

        # 1. Display order request summary
        print("\n" + "=" * 55)
        print(" 📋 ORDER REQUEST SUMMARY")
        print("=" * 55)
        print(f"  Symbol:    {args.symbol}")
        print(f"  Side:      {args.side}")
        print(f"  Type:      {args.type}")
        print(f"  Quantity:  {args.quantity}")
        if args.type in ("LIMIT", "STOP_LIMIT"):
            print(f"  Price:     {args.price}")
        if args.type == "STOP_LIMIT":
            print(f"  Stop Price:{args.stop_price}")
        print("=" * 55 + "\n")

        # 6. Use services from orders.py & 7. Do not place API logic inside CLI
        client = BinanceFuturesClient()
        order_service = OrderService(client)

        print("🚀 Executing order via Binance API...\n")

        if args.type == "MARKET":
            response = order_service.place_market_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity
            )
        elif args.type == "LIMIT":
            response = order_service.place_limit_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price
            )
        elif args.type == "STOP_LIMIT":
            response = order_service.place_stop_limit_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price,
                stop_price=args.stop_price
            )

        # 2. Display order response details
        print("\n" + "=" * 55)
        print(" 📄 ORDER RESPONSE DETAILS")
        print("=" * 55)
        for key, value in vars(response).items():
            formatted_key = key.replace('_', ' ').title()
            # If value is an Enum, get its string value
            print_val = value.value if hasattr(value, 'value') else value
            print(f"  {formatted_key:<15}: {print_val}")
        print("=" * 55 + "\n")

        # 3. Display success message
        print("✅ SUCCESS: Order completed successfully.\n")

    except OrderServiceError as e:
        print("\n" + "!" * 55)
        print(f"❌ ORDER ERROR: \n   {e}")
        print("!" * 55 + "\n")
        logger.error(f"Order Service Error during CLI execution: {e}")
        sys.exit(1)
        
    except ValueError as e:
        print("\n" + "!" * 55)
        print(f"❌ CONFIGURATION ERROR: \n   {e}")
        print("!" * 55 + "\n")
        logger.error(f"Configuration Error during CLI execution: {e}")
        sys.exit(1)
        
    except Exception as e:
        print("\n" + "!" * 55)
        print(f"❌ UNEXPECTED ERROR: \n   {e}")
        print("!" * 55 + "\n")
        logger.exception("Unexpected error occurred during CLI execution.")
        sys.exit(1)


def run_interactive_mode(logger):
    """Executes the CLI in an interactive rich menu mode."""
    console.print(Panel("[bold cyan]🚀 Binance Futures Trading Bot (Testnet)[/]", expand=False, box=box.ROUNDED))
    
    try:
        with console.status("Initializing Client...", spinner="dots"):
            client = BinanceFuturesClient()
            order_service = OrderService(client)
    except Exception as e:
        console.print(Panel(f"[bold red]❌ Initialization Failed[/]\n{e}", border_style="red"))
        sys.exit(1)

    while True:
        console.print("\n[bold]Main Menu[/bold]")
        console.print("1. [cyan]Verify Credentials[/]")
        console.print("2. [cyan]Market Order[/]")
        console.print("3. [cyan]Limit Order[/]")
        console.print("4. [cyan]Stop Limit Order[/]")
        console.print("5. [cyan]View Open Orders[/]")
        console.print("6. [cyan]View Order History[/]")
        console.print("7. [red]Exit[/]")

        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7"])

        try:
            if choice == "1":
                with console.status("Verifying credentials securely...", spinner="dots"):
                    status = client.verify_credentials()
                
                table = Table(title="Credential Verification Status", box=box.ROUNDED)
                table.add_column("Check", style="cyan")
                table.add_column("Status", justify="center")
                table.add_row("Account Reachable", "[green]✅ YES[/]" if status['account_reachable'] else "[red]❌ NO[/]")
                table.add_row("API Key Valid", "[green]✅ YES[/]" if status['api_key_valid'] else "[red]❌ NO[/]")
                table.add_row("Secret Key Valid", "[green]✅ YES[/]" if status['secret_key_valid'] else "[red]❌ NO[/]")
                table.add_row("Futures Permissions", "[green]✅ YES[/]" if status['futures_permissions'] else "[red]❌ NO[/]")
                console.print(table)
                
                if status['api_key_valid'] and status['secret_key_valid'] and status['futures_permissions']:
                    console.print("[bold green]✅ All checks passed! Ready to trade.[/]")
                else:
                    console.print("[bold red]❌ Verification failed. Check API Keys and Futures permissions.[/]")

            elif choice in ("2", "3", "4"):
                symbol = Prompt.ask("Enter Symbol (e.g., BTCUSDT)").upper()
                side = Prompt.ask("Enter Side", choices=["BUY", "SELL"])
                quantity = FloatPrompt.ask("Enter Quantity (e.g., 0.001)")
                
                response = None
                if choice == "2":
                    with console.status(f"Placing MARKET {side} for {quantity} {symbol}...", spinner="dots"):
                        response = order_service.place_market_order(symbol, side, quantity)
                        
                elif choice == "3":
                    price = FloatPrompt.ask("Enter Limit Price")
                    with console.status(f"Placing LIMIT {side} for {quantity} {symbol} @ {price}...", spinner="dots"):
                        response = order_service.place_limit_order(symbol, side, quantity, price)
                        
                elif choice == "4":
                    price = FloatPrompt.ask("Enter Limit Price")
                    stop_price = FloatPrompt.ask("Enter Stop Price")
                    with console.status(f"Placing STOP_LIMIT {side} for {quantity} {symbol} @ {price} (Stop: {stop_price})...", spinner="dots"):
                        response = order_service.place_stop_limit_order(symbol, side, quantity, price, stop_price)

                if response:
                    table = Table(title="Order Response Details", box=box.ROUNDED)
                    table.add_column("Field", style="cyan")
                    table.add_column("Value", style="green")
                    for k, v in vars(response).items():
                        print_val = v.value if hasattr(v, 'value') else v
                        table.add_row(k.replace('_', ' ').title(), str(print_val))
                    console.print(table)
                    console.print("[bold green]✅ Order placed successfully![/]")

            elif choice == "5":
                symbol = Prompt.ask("Enter Symbol (Optional, press Enter for all)", default="")
                with console.status("Fetching open orders...", spinner="dots"):
                    orders = order_service.get_open_orders(symbol.upper() if symbol else None)
                
                if not orders:
                    console.print("[yellow]No open orders found.[/]")
                else:
                    table = Table(title=f"Open Orders {f'({symbol.upper()})' if symbol else ''}", box=box.ROUNDED)
                    table.add_column("Order ID", style="cyan")
                    table.add_column("Symbol")
                    table.add_column("Side")
                    table.add_column("Type")
                    table.add_column("Price")
                    table.add_column("Quantity")
                    table.add_column("Status")
                    for o in orders:
                        status_color = "yellow" if o.status.value == 'NEW' else "cyan"
                        table.add_row(
                            str(o.order_id), 
                            o.symbol, 
                            o.side.value, 
                            o.type.value, 
                            str(o.price), 
                            str(o.quantity),
                            f"[{status_color}]{o.status.value}[/]"
                        )
                    console.print(table)

            elif choice == "6":
                symbol = Prompt.ask("Enter Symbol (e.g., BTCUSDT)").upper()
                limit = FloatPrompt.ask("Number of recent orders", default=20)
                with console.status(f"Fetching order history for {symbol}...", spinner="dots"):
                    orders = order_service.get_order_history(symbol, int(limit))
                
                if not orders:
                    console.print(f"[yellow]No order history found for {symbol}.[/]")
                else:
                    table = Table(title=f"Order History ({symbol})", box=box.ROUNDED)
                    table.add_column("Order ID", style="cyan")
                    table.add_column("Type")
                    table.add_column("Side")
                    table.add_column("Quantity")
                    table.add_column("Status")
                    table.add_column("Price")
                    for o in orders:
                        status_color = "green" if o.status.value == 'FILLED' else "yellow" if o.status.value == 'NEW' else "red"
                        table.add_row(
                            str(o.order_id), 
                            o.type.value, 
                            o.side.value, 
                            str(o.quantity),
                            f"[{status_color}]{o.status.value}[/]", 
                            str(o.price)
                        )
                    console.print(table)

            elif choice == "7":
                console.print("[bold green]Goodbye! 👋[/]")
                break

        except OrderServiceError as e:
            console.print(Panel(f"[bold red]❌ ORDER ERROR[/]\n{e}", border_style="red"))
        except ValueError as e:
            console.print(Panel(f"[bold red]❌ VALIDATION ERROR[/]\n{e}", border_style="red"))
        except Exception as e:
            console.print(Panel(f"[bold red]❌ UNEXPECTED ERROR[/]\n{e}", border_style="red"))
            logger.exception("Unexpected error in interactive mode.")

def main():
    # Setup global application logging
    setup_logging()
    logger = logging.getLogger("cli")

    parser = argparse.ArgumentParser(
        description="Trading Bot Command Line Interface for placing orders on Binance Futures."
    )
    
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Binance API connection and credentials without placing orders"
    )
    
    parser.add_argument(
        "--verify-credentials",
        action="store_true",
        help="Verify API keys and Futures trading permissions securely"
    )
    
    parser.add_argument(
        "--symbol", 
        type=str.upper, 
        help="Trading pair symbol (e.g., BTCUSDT)"
    )
    parser.add_argument(
        "--side", 
        type=str.upper, 
        choices=["BUY", "SELL"], 
        help="Order side (BUY or SELL)"
    )
    parser.add_argument(
        "--type", 
        type=str.upper, 
        choices=["MARKET", "LIMIT", "STOP_LIMIT"], 
        help="Order type (MARKET, LIMIT, or STOP_LIMIT)"
    )
    parser.add_argument(
        "--quantity", 
        type=float, 
        help="Quantity to trade"
    )
    parser.add_argument(
        "--price", 
        type=float, 
        help="Limit price (required if type is LIMIT or STOP_LIMIT)"
    )
    parser.add_argument(
        "--stop-price", 
        type=float, 
        help="Stop price (required if type is STOP_LIMIT)"
    )

    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        run_interactive_mode(logger)
    else:
        args = parser.parse_args()
        run_automated_mode(args, logger)

if __name__ == "__main__":
    main()
