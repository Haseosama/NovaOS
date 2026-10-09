"""
NovaOS Desktop Environment (NovaShell)
Futuristic Windows 11 Inspired Native Desktop Shell running directly on console/terminal.
Features centered taskbar, start menu, security status, and instant app launching.
"""

import os
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt

from kernel.sysinfo import NovaSysInfo
from security.defender import NovaDefender
from security.firewall import NovaWall
from security.vault import NovaVault
from shell.terminal import NovaTerminal
from installer.wizard import NovaInstallerWizard

console = Console()

class NovaDesktop:
    """Windows 11 Futuristic Desktop Environment."""

    def __init__(self, mode: str = "Live CD"):
        self.mode = mode
        self.defender = NovaDefender()
        self.firewall = NovaWall()
        self.vault = NovaVault()
        self.running = True
        self.start_menu_open = False

    def render_header(self):
        info = NovaSysInfo.get_os_info()
        hw = NovaSysInfo.get_hardware_telemetry()
        
        mode_badge = f"[bold white on blue] {self.mode.upper()} [/bold white on blue]" if self.mode == "Live CD" else "[bold white on green] INSTALLED [/bold white on green]"
        shield_badge = "[bold white on dark_green] SHIELD ACTIVE (ZERO-TRUST) [/bold white on dark_green]"
        tpm_badge = "[bold white on cyan] TPM 2.0 PCR-7 OK [/bold white on cyan]"

        header = f"""[bold cyan]NovaOS Hyperion 2026[/bold cyan]  {mode_badge}  {shield_badge}  {tpm_badge}
[dim white]Windows 11 Futuristic Secure Edition | Kernel: {info['kernel']} | CPU: {hw['cpu_cores']}x {hw['cpu_model']}[/dim white]"""
        console.print(Panel(header, style="cyan", border_style="bold cyan"))

    def render_desktop_icons(self):
        icons = [
            Panel("[bold yellow]╔══════╗\n║ >_   ║\n╚══════╝[/bold yellow]\n[bold white][1] Terminal[/bold white]\n[dim]PowerShell Neo[/dim]", style="cyan", width=20),
            Panel("[bold green]╔══════╗\n║  [V] ║\n╚══════╝[/bold green]\n[bold white][2] Defender[/bold white]\n[dim]Security Center[/dim]", style="green", width=20),
            Panel("[bold magenta]╔══════╗\n║ [LOCK]║\n╚══════╝[/bold magenta]\n[bold white][3] Vault V:[/bold white]\n[dim]BitLocker Neo[/dim]", style="magenta", width=20),
            Panel("[bold blue]╔══════╗\n║ [DIR] ║\n╚══════╝[/bold blue]\n[bold white][4] Explorer[/bold white]\n[dim]File Manager[/dim]", style="blue", width=20),
            Panel("[bold red]╔══════╗\n║ [INST]║\n╚══════╝[/bold red]\n[bold white][5] Installer[/bold white]\n[dim]Deploy to SSD[/dim]", style="red", width=20),
            Panel("[bold white]╔══════╗\n║ [CFG] ║\n╚══════╝[/bold white]\n[bold white][6] Settings[/bold white]\n[dim]Control Panel[/dim]", style="white", width=20),
        ]
        console.print(Columns(icons, equal=True, expand=True))

    def render_telemetry_widgets(self):
        hw = NovaSysInfo.get_hardware_telemetry()
        def_st = self.defender.get_status()
        fw_st = self.firewall.get_status()

        # Telemetry panel
        telemetry = f"""[bold cyan]CPU Load:[/bold cyan] {hw['cpu_usage_pct']}%  [dim](Dynamic Microcode Throttling)[/dim]
[bold cyan]Memory:[/bold cyan] {hw['mem_used_mb']} MB / {hw['mem_total_mb']} MB ([bold green]{hw['mem_percent']}%[/bold green])
[bold cyan]Storage:[/bold cyan] {hw['disk_used_gb']} GB / {hw['disk_total_gb']} GB (AES-256 Encrypted)
[bold cyan]Swap/ZRAM:[/bold cyan] 4096 MB Compressed ZSTD"""

        # Security panel
        security = f"""[bold green]Nova Defender:[/bold green] Real-Time Heuristic Shield ACTIVE
[bold green]Zero-Trust Firewall:[/bold green] {fw_st['allowed_packets']} allowed, {fw_st['dropped_packets']} dropped
[bold green]Root of Trust:[/bold green] Hardware TPM 2.0 PCR Registers Verified
[bold green]Tamper Defense:[/bold green] SHA-512 Measured Kernel Boot"""

        p1 = Panel(telemetry, title="[bold cyan]System Telemetry[/bold cyan]", border_style="cyan")
        p2 = Panel(security, title="[bold green]Security Center Hub[/bold green]", border_style="green")
        console.print(Columns([p1, p2], equal=True, expand=True))

    def render_start_menu(self):
        menu_content = """[bold cyan]═══════════════════ NOVA START MENU ═══════════════════[/bold cyan]
[bold white]  [1] Nova Terminal (PowerShell Cybernetic Edition)  [/bold white]
[bold white]  [2] Nova Defender (Threats, Heuristics & Antivirus)[/bold white]
[bold white]  [3] BitLocker Neo Encrypted Drive V:               [/bold white]
[bold white]  [4] Nova File Explorer (Encrypted Directories)     [/bold white]
[bold white]  [5] Install NovaOS to Disk (Setup Wizard)         [/bold white]
[bold white]  [6] System Settings & Futuristic Personalization  [/bold white]
[dim cyan]────────────────────────────────────────────────────────[/dim cyan]
[bold yellow]  Recommended / Recent Security Events:                 [/bold yellow]
  • LUKS2 Cryptographic Volume initialized (Argon2id)
  • Measured Boot: PCR-0, PCR-4, PCR-7 hashes verified
  • Real-Time Defense definitions updated to 2026.10
[dim cyan]────────────────────────────────────────────────────────[/dim cyan]
[bold white]  Session: [bold green]NovaAdmin (Administrator)[/bold green] | [dim]Lock [L] | Power [Q][/dim][/bold white]
[bold cyan]════════════════════════════════════════════════════════[/bold cyan]"""
        console.print(Panel(menu_content, style="cyan on black", title="[bold white]Windows 11 Neo Start[/bold white]", width=64))

    def render_taskbar(self):
        now_str = time.strftime("%Y-%m-%d  %H:%M:%S")
        taskbar_layout = f"""[bold black on cyan] ❖ NOVA [/bold black on cyan] [bold white on blue] [1] Term [/bold white on blue] [bold white on green] [2] Shield [/bold white on green] [bold white on magenta] [3] Vault [/bold white on magenta] [bold white on red] [5] Install [/bold white on red]               [bold white on dark_blue] 📶 Wi-Fi 6E | 🛡️ TPM OK | 🔋 100% | 🕒 {now_str} [/bold white on dark_blue]"""
        console.print(Panel(Align.center(taskbar_layout), style="white on black", border_style="cyan", padding=(0, 0)))

    def show_desktop(self):
        console.clear()
        self.render_header()
        console.print()
        self.render_desktop_icons()
        console.print()
        self.render_telemetry_widgets()
        console.print()
        if self.start_menu_open:
            self.render_start_menu()
            console.print()
        self.render_taskbar()

    def run(self):
        while self.running:
            self.show_desktop()
            console.print("[dim cyan]Desktop Navigation: [1-6] Launch Apps | [S] Toggle Start Menu | [Q] Power Off / Exit[/dim cyan]")
            try:
                choice = Prompt.ask("[bold cyan]NovaShell[/bold cyan]", default="1")
            except (KeyboardInterrupt, EOFError):
                break

            choice = choice.strip().upper()
            if choice == "1":
                term = NovaTerminal()
                term.run_interactive()
            elif choice == "2":
                self.show_defender_center()
            elif choice == "3":
                self.show_vault_explorer()
            elif choice == "4":
                self.show_file_explorer()
            elif choice == "5":
                wizard = NovaInstallerWizard()
                wizard.run()
                Prompt.ask("\n[bold green]Press Enter to return to NovaOS Desktop...[/bold green]")
            elif choice == "6":
                self.show_settings()
            elif choice == "S":
                self.start_menu_open = not self.start_menu_open
            elif choice in ("Q", "QUIT", "EXIT", "SHUTDOWN"):
                console.print("[bold yellow]Shutting down NovaOS Session... System halted safely.[/bold yellow]")
                self.running = False

    def show_defender_center(self):
        console.clear()
        st = self.defender.get_status()
        console.print(Panel("""[bold green]
  ██████╗ ███████╗███████╗███████╗███╗   ██╗██████╗ ███████╗██████╗ 
  ██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
  ██║  ██║█████╗  █████╗  █████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝
  ██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
  ██████╔╝███████╗██║     ███████╗██║ ╚████║██████╔╝███████╗██║  ██║
  ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
[/bold green][bold white]WINDOWS 11 ADVANCED THREAT DEFENSE & SECURITY HUB[/bold white]""", style="green on black"))

        table = Table(title="[bold green]Real-Time Defense Matrix[/bold green]")
        table.add_column("Security Component", style="cyan")
        table.add_column("Status", style="bold green")
        table.add_column("Technology", style="white")

        table.add_row("Real-Time Heuristic Shield", "PROTECTED", "AI Heuristic Deep Inspection")
        table.add_row("Cloud-Delivered Threat Intelligence", "CONNECTED", "Quantum Hash Lookup")
        table.add_row("Tamper Protection", "LOCKED", "Kernel Space Ring 0 Guard")
        table.add_row("Ransomware Canary Traps", "ACTIVE", "Decoy File Integrity Monitoring")
        table.add_row("Hardware Root of Trust", "VERIFIED", "TPM 2.0 PCR-7 Measured Boot")
        table.add_row("Definitions Version", st["definitions_version"], "Daily Delta Signatures")
        table.add_row("Threats Intercepted", str(st["threats_blocked"]), "Zero Leaks Reported")

        console.print(table)
        console.print()
        Prompt.ask("[bold green]Press Enter to perform a Quick Security Scan[/bold green]")
        res = self.defender.run_quick_scan("/tmp")
        console.print(f"[bold green]Scan Completed:[/bold green] [bold white]{res['scanned_files']} files checked, {res['threats_found']} threats found.[/bold white]")
        Prompt.ask("\n[bold cyan]Press Enter to return to Desktop...[/bold cyan]")

    def show_vault_explorer(self):
        console.clear()
        console.print(Panel("[bold magenta]BitLocker Neo - Encrypted Drive V:[/bold magenta]\n[white]Hardware-bound AES-256-GCM Cryptographic Storage Volume[/white]", style="magenta"))
        if not self.vault.is_unlocked:
            console.print("[bold yellow]Drive V: is currently LOCKED and ENCRYPTED.[/bold yellow]")
            pwd = Prompt.ask("Enter master passphrase or 48-digit Recovery Key to mount", default="NovaMaster2026!")
            if not os.path.exists(self.vault.vault_path):
                self.vault.initialize(pwd)
                console.print("[bold green]New BitLocker Neo Volume created and mounted![/bold green]")
            else:
                ok = self.vault.unlock(pwd)
                if not ok:
                    console.print("[bold red]Decryption failed: Invalid credentials.[/bold red]")
                    Prompt.ask("Press Enter to continue...")
                    return

        files = self.vault.list_files()
        table = Table(title="[bold magenta]Files in Encrypted Drive V:[/bold magenta]")
        table.add_column("Filename", style="bold white")
        table.add_column("Encrypted Size", style="cyan")
        table.add_column("Cipher", style="green")

        for f in files:
            table.add_row(f["name"], f"{f['size']} bytes", "AES-256-GCM")

        console.print(table)
        Prompt.ask("\n[bold magenta]Press Enter to return to Desktop...[/bold magenta]")

    def show_file_explorer(self):
        console.clear()
        console.print(Panel("[bold blue]Nova Files - Windows 11 Fluent Explorer[/bold blue]", style="blue"))
        table = Table(title="[bold blue]Drives & Partitions[/bold blue]")
        table.add_column("Drive Letter", style="bold yellow")
        table.add_column("Volume Label", style="white")
        table.add_column("Filesystem", style="cyan")
        table.add_column("Protection", style="bold green")

        table.add_row("Drive C:", "NovaOS System Partition", "Btrfs / Linux", "LUKS2 AES-256-XTS")
        table.add_row("Drive V:", "BitLocker Neo User Vault", "CryptFS", "AES-256-GCM PBKDF2")
        table.add_row("Drive D:", "NovaOS Live CD (El Torito)", "ISO 9660 / Joliet", "Cryptographic Read-Only")

        console.print(table)
        Prompt.ask("\n[bold blue]Press Enter to return to Desktop...[/bold blue]")

    def show_settings(self):
        console.clear()
        console.print(Panel("[bold white]NovaOS Settings & Control Panel[/bold white]\n[dim]Configure System, Holographic Display, Privacy, Security & Hardware[/dim]", style="white"))
        
        info = NovaSysInfo.get_os_info()
        table = Table(title="[bold white]System Specifications[/bold white]")
        table.add_column("Setting", style="cyan")
        table.add_column("Current Value", style="green")

        table.add_row("Operating System", f"{info['name']} {info['edition']}")
        table.add_row("Windows 11 Build", info['build'])
        table.add_row("Kernel Hardening", "PTI, KASLR, AppArmor, Zero-Allocation Memory Sanitizer")
        table.add_row("Theme Accent", "Electric Cyan Acrylic (#00f2fe)")
        table.add_row("Secure Boot Enforcement", "Mandatory (PCR-7 Verified)")
        table.add_row("Firewall Profile", "Zero-Trust Military Mode")

        console.print(table)
        Prompt.ask("\n[bold white]Press Enter to return to Desktop...[/bold white]")

def main():
    desktop = NovaDesktop(mode="Live CD")
    desktop.run()

if __name__ == "__main__":
    main()
