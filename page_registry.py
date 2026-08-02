from rich.console import Console
from rich.table import Table
import dash

app = dash.Dash(__name__, use_pages=True)

console = Console()
table = Table(title="Dash page_registry")

table.add_column("Key", style="cyan")
table.add_column("Module", style="cyan")
table.add_column("Name", style="green")
table.add_column("Title", style="yellow")
table.add_column("Path", style="magenta")
table.add_column("Relative_path", style="magenta")
table.add_column("Order", style="blue")

for key, page in dash.page_registry.items():
    table.add_row(
        str(key),
        str(page.get("module")),
        str(page.get("name")),
        str(page.get("title")),
        str(page.get("path")),
        str(page.get("relative_path")),
        str(page.get("order")),
    )

console.print(table)
