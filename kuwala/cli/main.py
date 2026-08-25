"""
Kuwala Command Line Interface.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Kuwala Quantitative Options & Volatility CLI")
console = Console()


@app.command()
def version():
    """Print the installed Kuwala version."""
    import kuwala
    console.print(f"[bold green]Kuwala version:[/bold green] {kuwala.__version__}")


@app.command()
def fetch(
    symbol: str = typer.Argument(..., help="Underlying ticker symbol (e.g. SPY, AAPL)"),
    source: str = typer.Option("yahoo", help="Data source adapter"),
):
    """Fetch options chain for a symbol and print summary."""
    import kuwala
    console.print(f"[cyan]Fetching options chain for {symbol} from {source}...[/cyan]")
    chain = kuwala.data.fetch(symbol, source=source)
    console.print(f"[green]Retrieved {len(chain)} option quotes for {symbol} (Spot: ${chain.spot:.2f})[/green]")


@app.command()
def fit(
    symbol: str = typer.Argument(..., help="Underlying ticker symbol (e.g. SPY)"),
    model: str = typer.Option("ssvi", help="Surface model (ssvi)"),
):
    """Calibrate volatility surface and display arbitrage diagnostics."""
    import kuwala
    console.print(f"[cyan]Calibrating {model.upper()} surface for {symbol}...[/cyan]")
    chain = kuwala.data.fetch(symbol)
    surf = kuwala.volatility.surface(chain, model=model)
    diag = surf.diagnostics()
    console.print(diag.summary())


@app.command()
def vrp(
    symbol: str = typer.Argument(..., help="Underlying ticker symbol"),
    window: int = typer.Option(20, help="Realized volatility lookback window"),
):
    """Calculate Volatility Risk Premium (VRP)."""
    import kuwala
    chain = kuwala.data.fetch(symbol)
    surf = kuwala.volatility.surface(chain)
    vrp_df = kuwala.signals.vrp(surf, realized_window=window)
    console.print(vrp_df.to_string(index=False))


if __name__ == "__main__":
    app()
