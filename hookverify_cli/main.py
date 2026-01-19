"""HookVerify CLI - Main entry point."""
import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from datetime import datetime

from . import __version__
from .config import save_credentials, load_credentials, clear_credentials, get_api_key, get_api_url
from .listener import listen_for_webhooks

app = typer.Typer(
    name="hookverify",
    help="HookVerify CLI - Receive webhooks locally during development.",
    add_completion=False
)
console = Console()


@app.command()
def login(
    api_key: str = typer.Option(..., "--api-key", "-k", prompt="Enter your API key", help="Your HookVerify API key"),
    api_url: str = typer.Option("https://hookverify.com", "--url", "-u", help="HookVerify API URL")
):
    """Authenticate with HookVerify."""
    save_credentials(api_key, api_url)
    console.print(f"[green]✓[/green] Credentials saved to ~/.hookverify/credentials.json")
    console.print(f"  API URL: {api_url}")
    console.print(f"  API Key: {api_key[:12]}...{api_key[-4:]}")


@app.command()
def logout():
    """Remove stored credentials."""
    clear_credentials()
    console.print("[green]✓[/green] Credentials removed.")


@app.command()
def status():
    """Check connection status and stored credentials."""
    creds = load_credentials()
    
    if not creds:
        console.print("[yellow]Not logged in.[/yellow] Run: hookverify login --api-key YOUR_KEY")
        return
    
    table = Table(title="HookVerify CLI Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    api_key = creds.get("api_key", "")
    masked_key = f"{api_key[:12]}...{api_key[-4:]}" if len(api_key) > 16 else "***"
    
    table.add_row("API URL", creds.get("api_url", "https://hookverify.com"))
    table.add_row("API Key", masked_key)
    table.add_row("Config File", "~/.hookverify/credentials.json")
    
    console.print(table)


@app.command()
def listen(
    port: int = typer.Argument(..., help="Local port to forward webhooks to"),
    path: str = typer.Option("/", "--path", "-p", help="Local path to forward to"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key (uses stored key if not provided)")
):
    """
    Listen for webhooks and forward to localhost.
    
    Example:
        hookverify listen 3000
        hookverify listen 8080 --path /webhooks/stripe
    """
    key = api_key or get_api_key()
    
    if not key:
        console.print("[red]Error:[/red] No API key found. Run: hookverify login --api-key YOUR_KEY")
        raise typer.Exit(1)
    
    api_url = get_api_url()
    
    console.print(f"\n[bold blue]HookVerify CLI[/bold blue] v{__version__}")
    console.print(f"Forwarding webhooks to: [cyan]http://localhost:{port}{path}[/cyan]")
    console.print(f"Connecting to: [dim]{api_url}[/dim]\n")
    
    def on_connect(data):
        console.print(f"[green]✓ Connected![/green] Waiting for webhooks...\n")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    def on_webhook(webhook_data, result):
        timestamp = datetime.now().strftime("%H:%M:%S")
        delivery_id = webhook_data.get("deliveryId", "unknown")
        
        if result.get("success"):
            status_code = result.get("status_code", "???")
            color = "green" if 200 <= status_code < 300 else "yellow"
            console.print(f"[dim]{timestamp}[/dim] [{color}]→[/{color}] {delivery_id} [cyan]{status_code}[/cyan]")
        else:
            error = result.get("error", "Unknown error")
            console.print(f"[dim]{timestamp}[/dim] [red]✗[/red] {delivery_id} - {error}")
    
    def on_error(error):
        console.print(f"[red]Error:[/red] {error}")
        console.print("[dim]Reconnecting in 5 seconds...[/dim]")
    
    try:
        asyncio.run(listen_for_webhooks(
            api_key=key,
            api_url=api_url,
            port=port,
            path=path,
            on_connect=on_connect,
            on_webhook=on_webhook,
            on_error=on_error
        ))
    except KeyboardInterrupt:
        console.print("\n[yellow]Disconnected.[/yellow]")


@app.command()
def version():
    """Show CLI version."""
    console.print(f"HookVerify CLI v{__version__}")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
    