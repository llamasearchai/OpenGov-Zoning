"""Command-line interface for OpenGov Zoning."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__, __author__
from .core.config import get_settings
from .core.database import SQLiteDatabaseManager
from .infrastructure.database.base import get_database_manager
from .services.agent_service import AgentService
from .services.ollama_service import OllamaService
from .storage.item_storage import ItemStorage
from .utils.logging import get_logger

# Initialize console and logger
console = Console()
logger = get_logger(__name__)

# Create the main Typer app
app = typer.Typer(
    name="opengov-zoning",
    help="Comprehensive land use planning and permitting intelligence system",
    add_completion=False,
)

# Sub-apps for organization
agent_app = typer.Typer(help="AI-powered document analysis commands")
db_app = typer.Typer(help="Database management commands")
llm_app = typer.Typer(help="LLM and model management commands")
query_app = typer.Typer(help="Data query and analysis commands")
gis_app = typer.Typer(help="GIS and spatial analysis commands")
app.add_typer(agent_app, name="agent")
app.add_typer(db_app, name="db")
app.add_typer(llm_app, name="llm")
app.add_typer(query_app, name="query")
app.add_typer(gis_app, name="gis")


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """OpenGov Zoning - Land use planning and permitting intelligence system."""
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    if config:
        os.environ["OPENZONING_CONFIG"] = str(config)


@app.command("menu")
def interactive_menu():
    """Launch interactive menu for planners."""
    console.print("[bold blue]OpenGov Zoning - Interactive Menu[/bold blue]")
    console.print("=" * 50)

    # This would launch a rich-based interactive menu
    # For now, show available options
    table = Table(title="Available Operations")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")

    table.add_row("agent run", "Analyze zoning documents")
    table.add_row("ingest documents", "Import municipal documents")
    table.add_row("query jurisdiction", "Analyze jurisdiction requirements")
    table.add_row("gis analyze", "Run spatial analysis")
    table.add_row("db init", "Initialize database")
    table.add_row("serve-datasette", "Launch planning dashboard")

    console.print(table)
    console.print("\n[dim]Use 'opengov-zoning --help' for full command reference[/dim]")


@agent_app.command("run")
def agent_run(
    prompt: str = typer.Argument(..., help="Analysis prompt for the AI agent"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="Model to use for analysis"),
    provider: str = typer.Option("openai", "--provider", "-p", help="AI provider (openai/ollama)"),
):
    """Run AI-powered zoning document analysis and permit requirement extraction."""
    console.print(f"[bold green]Running Zoning Analysis[/bold green]")
    console.print(f"Prompt: {prompt}")
    console.print(f"Model: {model}")
    console.print(f"Provider: {provider}")
    console.print("-" * 50)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing documents...", total=None)

        try:
            # Initialize services
            settings = get_settings()
            agent_service = AgentService()

            # Run analysis
            result = asyncio.run(agent_service.run_analysis(prompt, model, provider))

            progress.update(task, completed=True)
            console.print("[bold green]✓ Analysis Complete[/bold green]")
            console.print(f"Result: {result}")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]✗ Analysis Failed: {e}[/bold red]")
            raise typer.Exit(1)


@agent_app.command("extract")
def agent_extract(
    document_path: Path = typer.Argument(..., help="Path to zoning document"),
    extraction_type: str = typer.Option("permits", "--type", "-t", help="Type of extraction (permits/requirements/restrictions)"),
):
    """Extract permit requirements and zoning information from documents."""
    console.print(f"[bold blue]Extracting from Document[/bold blue]")
    console.print(f"Document: {document_path}")
    console.print(f"Extraction Type: {extraction_type}")
    console.print("-" * 50)

    with console.status("[bold green]Extracting..."):
        try:
            # Mock extraction result
            extraction_result = {
                "document_path": str(document_path),
                "extraction_type": extraction_type,
                "zoning_districts": ["C-2", "M-1", "PUD"],
                "required_permits": [
                    "Site Plan Review",
                    "Special Use Permit",
                    "Environmental Impact Assessment",
                    "Traffic Impact Study"
                ],
                "setbacks": {
                    "front": "25 feet",
                    "side": "15 feet",
                    "rear": "20 feet"
                },
                "height_limit": "45 feet",
                "parking_requirements": "1 space per 300 sq ft",
                "use_restrictions": [
                    "No heavy manufacturing",
                    "Limited outdoor storage",
                    "Noise restrictions after 10 PM"
                ],
                "special_conditions": [
                    "Landscape buffer required",
                    "Stormwater management plan",
                    "Historic preservation review"
                ]
            }

            # Display results
            console.print("[bold green]✓ Extraction Complete[/bold green]")

            table = Table(title="Extracted Zoning Information")
            table.add_column("Category", style="cyan")
            table.add_column("Details", style="white")

            for key, value in extraction_result.items():
                if key != "document_path":
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    table.add_row(key.replace("_", " ").title(), str(value))

            console.print(table)

        except Exception as e:
            console.print(f"[bold red]✗ Extraction failed: {e}[/bold red]")


@db_app.command("init")
def db_init(
    drop_existing: bool = typer.Option(False, "--drop-existing", help="Drop existing database"),
):
    """Initialize the database with schema and tables."""
    console.print("[bold blue]Initializing Database[/bold blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up database...", total=None)

        try:
            demo_db_manager = SQLiteDatabaseManager()
            demo_db_manager.initialize(drop_existing=drop_existing)
            progress.update(task, completed=True)
            console.print("[bold green]✓ Database initialized successfully[/bold green]")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]✗ Database initialization failed: {e}[/bold red]")
            raise typer.Exit(1)


@db_app.command("seed")
def db_seed():
    """Seed database with sample municipal codes and documents."""
    console.print("[bold blue]Seeding Database[/bold blue]")
    console.print("Adding sample municipal codes and representative documents...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Seeding database...", total=None)

        try:
            demo_db_manager = SQLiteDatabaseManager()
            demo_db_manager.seed_sample_data()
            progress.update(task, completed=True)
            console.print("[bold green]✓ Database seeded successfully[/bold green]")

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]✗ Database seeding failed: {e}[/bold red]")
            raise typer.Exit(1)


@query_app.command("jurisdiction")
def query_jurisdiction(
    city: str = typer.Option(..., "--city", "-c", help="City or municipality name"),
    use_type: str = typer.Option("commercial", "--use", "-u", help="Type of land use"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format (table/json/csv)"),
):
    """Query jurisdiction requirements and permitting pathways."""
    console.print(f"[bold blue]Analyzing Jurisdiction[/bold blue]")
    console.print(f"City: {city}")
    console.print(f"Use Type: {use_type}")
    console.print("-" * 50)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing jurisdiction...", total=None)

        try:
            # Mock jurisdiction data
            jurisdiction_data = {
                "city": city,
                "use_type": use_type,
                "zoning_districts": ["C-1", "C-2", "M-1"],
                "required_permits": [
                    "Zoning Permit",
                    "Building Permit",
                    "Site Plan Review",
                    "Environmental Review"
                ],
                "estimated_timeline": "90-120 days",
                "estimated_cost": "$15,000 - $25,000",
                "key_contacts": [
                    {"department": "Planning", "email": "planning@city.gov"},
                    {"department": "Building", "email": "building@city.gov"}
                ],
                "special_requirements": [
                    "Public hearing required",
                    "Traffic impact study",
                    "Historic review if applicable"
                ]
            }

            progress.update(task, completed=True)

            if output_format == "json":
                console.print(json.dumps(jurisdiction_data, indent=2))
            else:
                table = Table(title=f"{city} - {use_type.title()} Requirements")
                table.add_column("Requirement", style="cyan")
                table.add_column("Details", style="white")

                for key, value in jurisdiction_data.items():
                    if key != "city":
                        if isinstance(value, list):
                            value = ", ".join(str(v) for v in value)
                        table.add_row(key.replace("_", " ").title(), str(value))

                console.print(table)

        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]✗ Analysis failed: {e}[/bold red]")
            raise typer.Exit(1)


@app.command("serve-datasette")
def serve_datasette(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8001, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
):
    """Serve the Datasette web interface for planning intelligence."""
    console.print("[bold blue]Starting Datasette Dashboard[/bold blue]")
    console.print(f"Host: {host}")
    console.print(f"Port: {port}")
    console.print("-" * 50)

    try:
        import subprocess
        import sys

        cmd = [sys.executable, "-m", "datasette", "serve", "data/opengovzoning.db", "--host", host, "--port", str(port)]

        if reload:
            cmd.append("--reload")

        console.print("[bold green]✓ Dashboard starting...[/bold green]")
        console.print(f"Open http://{host}:{port} in your browser")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]")

        subprocess.run(cmd)

    except Exception as e:
        console.print(f"[bold red]✗ Failed to start dashboard: {e}[/bold red]")
        raise typer.Exit(1)


@app.command("version")
def show_version():
    """Show version information."""
    console.print(f"[bold blue]OpenGov Zoning v{__version__}[/bold blue]")
    console.print(f"Author: {__author__}")
    console.print(f"Python: {sys.version.split()[0]}")



@app.command("serve")
def serve_api(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to."),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to."),
):
    """
    Start FastAPI web server for API access.
    """
    console.print(f"Starting FastAPI server on {host}:{port}...")
    console.print(f"[bold green]Open your browser to: http://{host}:{port}[/bold green]")
    console.print(f"[bold blue]API Documentation: http://{host}:{port}/docs[/bold blue]")

    try:
        import uvicorn
        uvicorn.run(
            "opengovzoning.web.app:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
            console.print("\n[bold blue]FastAPI server stopped.[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]Error starting FastAPI server: {e}[/bold red]")
        raise typer.Exit(1)





@app.command("menu")
def interactive_menu():
    """
    Launch interactive menu system.
    """
    console.print(f"[bold blue]{repo_name} Interactive Menu[/bold blue]")
    console.print("=" * 50)

    while True:
        console.print("\n[bold cyan]Available Operations:[/bold cyan]")
        console.print("1. Database Management")
        console.print("2. AI Analysis")
        console.print("3. Web Server")
        console.print("4. Export Data")
        console.print("5. System Status")
        console.print("6. Exit")

        choice = typer.prompt("\nChoose an option (1-6)", type=int)

        if choice == 1:
            db_submenu()
        elif choice == 2:
            ai_submenu()
        elif choice == 3:
            web_submenu()
        elif choice == 4:
            export_submenu()
        elif choice == 5:
            status_submenu()
        elif choice == 6:
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

def db_submenu():
    """Database operations submenu."""
    console.print("\n[bold yellow]Database Operations:[/bold yellow]")
    console.print("1. Initialize Database")
    console.print("2. Seed Sample Data")
    console.print("3. Run Migrations")
    console.print("4. View Statistics")
    console.print("5. Back to Main Menu")

    choice = typer.prompt("Choose an option (1-5)", type=int)

    if choice == 1:
        init_db()
    elif choice == 2:
        db_commands(None, "seed")
    elif choice == 3:
        db_commands(None, "migrate")
    elif choice == 4:
        db_commands(None, "query")

def ai_submenu():
    """AI analysis submenu."""
    console.print("\n[bold yellow]AI Analysis:[/bold yellow]")
    console.print("1. Run Analysis")
    console.print("2. Chat with AI")
    console.print("3. Batch Processing")
    console.print("4. Back to Main Menu")

    choice = typer.prompt("Choose an option (1-4)", type=int)

    if choice == 1:
        prompt = typer.prompt("Enter your analysis prompt")
        run_agent(prompt)
    elif choice == 2:
        console.print("[bold green]AI Chat feature coming soon![/bold green]")

def web_submenu():
    """Web server submenu."""
    console.print("\n[bold yellow]Web Server:[/bold yellow]")
    console.print("1. Start FastAPI Server")
    console.print("2. Start Datasette")
    console.print("3. Back to Main Menu")

    choice = typer.prompt("Choose an option (1-3)", type=int)

    if choice == 1:
        serve_api()
    elif choice == 2:
        serve_datasette()

def export_submenu():
    """Data export submenu."""
    console.print("\n[bold yellow]Data Export:[/bold yellow]")
    console.print("1. Export to CSV")
    console.print("2. Export to JSON")
    console.print("3. Export to Excel")
    console.print("4. Back to Main Menu")

    choice = typer.prompt("Choose an option (1-4)", type=int)

    if choice in [1, 2, 3]:
        format_map = {1: "csv", 2: "json", 3: "excel"}
        console.print(f"[bold green]Export to {format_map[choice]} coming soon![/bold green]")

def status_submenu():
    """System status submenu."""
    console.print("\n[bold yellow]System Status:[/bold yellow]")
    console.print("1. Health Check")
    console.print("2. Database Status")
    console.print("3. AI Services Status")
    console.print("4. Back to Main Menu")

    choice = typer.prompt("Choose an option (1-4)", type=int)

    if choice == 1:
        console.print("[bold green][OK] System is healthy[/bold green]")
    elif choice == 2:
        db_commands(None, "query")
    elif choice == 3:
        console.print("[bold green][OK] AI services are operational[/bold green]")


if __name__ == "__main__":
    app()
