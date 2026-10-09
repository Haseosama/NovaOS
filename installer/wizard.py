"""
NovaOS Setup Wizard - Windows 11 Inspired Native OS Installer
Provides step-by-step graphical/terminal installation wizard for deploying NovaOS to disk.
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from installer.disk import NovaDiskManager
from installer.deploy import NovaDeployer

console = Console()

class NovaInstallerWizard:
    """Interactive Windows 11-style installer for NovaOS."""

    def __init__(self):
        self.selected_disk = None
        self.username = "Administrator"
        self.password = ""
        self.security_level = "Zero-Trust Military Grade (LUKS2 AES-256 + TPM 2.0)"
        self.recovery_key = ""

    def show_banner(self):
        console.clear()
        banner_text = """
 [bold cyan]███╗   ██╗ ██████╗ ██╗   ██╗ █████╗      ██████╗ ███████╗[/bold cyan]
 [bold cyan]████╗  ██║██╔═══██╗██║   ██║██╔══██╗    ██╔═══██╗██╔════╝[/bold cyan]
 [bold cyan]██╔██╗ ██║██║   ██║██║   ██║███████║    ██║   ██║███████╗[/bold cyan]
 [bold cyan]██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║    ██║   ██║╚════██║[/bold cyan]
 [bold cyan]██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║    ╚██████╔╝███████║[/bold cyan]
 [bold cyan]╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝     ╚═════╝ ╚══════╝[/bold cyan]
   [bold white]HYPERION 2026 EDITION — WINDOWS 11 SECURE CORE[/bold white]
"""
        console.print(Panel(banner_text, style="cyan on black", subtitle="[bold yellow]NovaOS Setup Wizard v1.0[/bold yellow]"))

    def run(self):
        self.show_banner()
        console.print("[bold green]Welcome to the NovaOS Setup Wizard![/bold green]")
        console.print("This installer will configure partitions, military-grade encryption, and deploy NovaOS.")
        console.print()

        # Step 1: Disk selection
        disks = NovaDiskManager.list_target_disks()
        table = Table(title="[bold cyan]Step 1: Select Target Installation Disk[/bold cyan]", style="cyan")
        table.add_column("#", style="bold yellow")
        table.add_column("Device", style="bold white")
        table.add_column("Model", style="cyan")
        table.add_column("Capacity", style="green")
        table.add_column("Type", style="magenta")

        for idx, d in enumerate(disks, 1):
            table.add_row(str(idx), d["device"], d["model"], f"{d['size_gb']} GB", d["type"])

        console.print(table)
        console.print()
        
        choice = Prompt.ask("Choose target disk number", choices=[str(i) for i in range(1, len(disks) + 1)], default="1")
        self.selected_disk = disks[int(choice) - 1]["device"]
        console.print(f"[bold green]Selected target drive:[/bold green] [bold cyan]{self.selected_disk}[/bold cyan]")
        console.print()

        # Step 2: Partitioning & Encryption preview
        layout = NovaDiskManager.generate_gpt_layout(self.selected_disk, full_disk_encryption=True)
        ptable = Table(title=f"[bold cyan]Proposed GPT Layout on {self.selected_disk}[/bold cyan]", style="cyan")
        ptable.add_column("Partition", style="bold white")
        ptable.add_column("Name", style="yellow")
        ptable.add_column("Filesystem", style="green")
        ptable.add_column("Size", style="cyan")
        ptable.add_column("Encryption", style="magenta")

        for p in layout:
            enc = f"[bold green]{p.get('cipher', 'LUKS2 AES-256')}[/bold green]" if p["encrypted"] else "[dim]None (ESP/Boot)[/dim]"
            ptable.add_row(p["part"], p["name"], p["fs"], str(p["size_mb"]), enc)

        console.print(ptable)
        console.print()

        # Step 3: User credentials & PIN
        console.print("[bold cyan]Step 2: Security & User Configuration[/bold cyan]")
        self.username = Prompt.ask("Enter system administrator username", default="NovaAdmin")
        self.password = Prompt.ask("Enter secure master PIN or password", password=True, default="NovaSecure2026!")
        console.print()

        # Step 4: Confirmation
        confirm = Confirm.ask(
            f"[bold red]WARNING:[/bold red] All data on [bold yellow]{self.selected_disk}[/bold yellow] will be erased and encrypted. Proceed?",
            default=True
        )
        if not confirm:
            console.print("[bold yellow]Installation aborted by user.[/bold yellow]")
            return

        # Step 5: Installation progress
        console.print()
        console.print(f"[bold cyan]Deploying NovaOS Hyperion to {self.selected_disk}...[/bold cyan]")
        
        with Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(complete_style="bold cyan", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Initializing deployment...", total=100)

            def update_cb(pct, desc):
                progress.update(task, completed=pct, description=f"[cyan]{desc}")
                time.sleep(0.05)

            self.recovery_key = NovaDeployer.execute_installation(
                target_disk=self.selected_disk,
                username=self.username,
                passphrase=self.password,
                security_level=self.security_level,
                progress_callback=update_cb
            )

        # Step 6: Installation Complete & Recovery Key
        console.print()
        success_msg = f"""
[bold green]Installation Successfully Completed![/bold green]

[bold white]NovaOS Hyperion 2026 is now installed on {self.selected_disk}[/bold white]

[bold yellow]IMPORTANT — BITLOCKER NEO EMERGENCY RECOVERY KEY:[/bold yellow]
[bold cyan]{self.recovery_key}[/bold cyan]

[bold white]Store this 48-digit key in a secure location (e.g. offline password manager).[/bold white]
[bold white]If hardware changes or TPM measurements fail, this key will unlock your drives.[/bold white]

[bold green]You can now remove the Live CD media and reboot into NovaOS.[/bold green]
"""
        console.print(Panel(success_msg, style="green on black", title="[bold white]NovaOS Deployment Summary[/bold white]"))

def main():
    wizard = NovaInstallerWizard()
    wizard.run()

if __name__ == "__main__":
    main()
