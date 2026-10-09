"""
Nova Terminal - Windows 11 Neo Futuristic Cybernetic Shell
Provides an interactive command center with telemetry, security controls, and system commands.
"""

import sys
import os
import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from kernel.sysinfo import NovaSysInfo
from kernel.integrity import IntegrityMonitor
from security.defender import NovaDefender
from security.firewall import NovaWall
from security.vault import NovaVault
from security.shredder import NovaShredder

console = Console()

class NovaTerminal:
    """Futuristic Windows 11 / Cyberpunk command shell."""

    def __init__(self):
        self.defender = NovaDefender()
        self.firewall = NovaWall()
        self.integrity = IntegrityMonitor()
        self.vault = NovaVault()
        self.running = True

    def show_banner(self):
        banner = """[bold cyan]
  _  _                 ___  ____  
 | \| |_____ ____ _   / _ \/ ___| 
 | .` / _ \ V / _` | | | | \___ \ 
 |_|\_\___/\_/ \__,_|  \___/|____/ 
[/bold cyan][bold white] NovaOS Terminal 1.0.0 [Hyperion 2026 Core - PowerShell Neo][/bold white]
[dim cyan] Type 'help' for command list | Type 'install-os' to launch installer | Type 'exit' to quit[/dim cyan]
"""
        console.print(banner)

    def print_neofetch(self):
        info = NovaSysInfo.get_os_info()
        hw = NovaSysInfo.get_hardware_telemetry()
        
        art = """[bold cyan]
      ████████  ████████      
      ████████  ████████      
      ████████  ████████      
      ████████  ████████      
                              
      ████████  ████████      
      ████████  ████████      
      ████████  ████████      
      ████████  ████████      
[/bold cyan]"""
        details = f"""
[bold cyan]NovaAdmin[/bold cyan]@[bold white]NovaOS-Workstation[/bold white]
--------------------------------
[bold cyan]OS:[/bold cyan] {info['name']} {info['edition']}
[bold cyan]Kernel:[/bold cyan] {info['kernel']}
[bold cyan]Uptime:[/bold cyan] {info['uptime_seconds']} seconds
[bold cyan]Shell:[/bold cyan] Nova-PowerShell 1.0 (Cybernetic v26)
[bold cyan]Theme:[/bold cyan] Windows 11 Acrylic Cyan / Void Dark
[bold cyan]CPU:[/bold cyan] {hw['cpu_model']} ({hw['cpu_cores']} Cores)
[bold cyan]Memory:[/bold cyan] {hw['mem_used_mb']} MB / {hw['mem_total_mb']} MB ({hw['mem_percent']}%)
[bold cyan]Disk:[/bold cyan] {hw['disk_used_gb']} GB / {hw['disk_total_gb']} GB ({hw['disk_percent']}%)
[bold cyan]Security:[/bold cyan] {info['security_mode']}
[bold cyan]TPM:[/bold cyan] {hw['tpm_version']}
[bold cyan]Storage Guard:[/bold cyan] {hw['bitlocker_neo_status']}
"""
        table = Table(show_header=False, box=None)
        table.add_column("Logo", width=32)
        table.add_column("Details")
        table.add_row(art, details)
        console.print(table)

    def print_help(self):
        table = Table(title="[bold cyan]NovaOS Built-in Commands[/bold cyan]", style="cyan")
        table.add_column("Command", style="bold yellow")
        table.add_column("Category", style="magenta")
        table.add_column("Description", style="white")

        cmds = [
            ("novafetch / neofetch", "System", "Display futuristic Windows 11 system telemetry"),
            ("sysinfo", "System", "Full hardware, memory, CPU and disk statistics"),
            ("install-os", "Installer", "Launch interactive NovaOS Setup Wizard"),
            ("defender", "Security", "Display Nova Defender status and threat telemetry"),
            ("scan [path]", "Security", "Run heuristic malware & threat scan"),
            ("firewall", "Security", "View NovaWall zero-trust rules and packet stats"),
            ("integrity", "Security", "Inspect TPM 2.0 PCR registers and measured boot chain"),
            ("vault init <pwd>", "Storage", "Initialize BitLocker Neo Encrypted Drive V:"),
            ("vault status", "Storage", "Display encrypted vault state"),
            ("shred <file>", "Security", "DoD 5220.22-M 7-pass military-grade file shredding"),
            ("matrix", "Fun", "Stream holographic cyberpunk cyber matrix"),
            ("clear", "Console", "Clear screen buffer"),
            ("exit / quit", "System", "Exit terminal shell"),
        ]
        for c, cat, desc in cmds:
            table.add_row(c, cat, desc)
        console.print(table)

    def run_matrix(self, duration=2.0):
        chars = "01NovaOSSecureCryptoAES256TPM20ZeroTrustHyperion"
        console.print("[bold green]Engaging Quantum Matrix Feed... (Press Ctrl+C to stop)[/bold green]")
        end_time = time.time() + duration
        try:
            while time.time() < end_time:
                line = "".join(random.choice(chars) if random.random() > 0.4 else " " for _ in range(75))
                console.print(f"[green]{line}[/green]")
                time.sleep(0.04)
        except KeyboardInterrupt:
            pass

    def execute_command(self, cmd_line: str):
        parts = cmd_line.strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("exit", "quit"):
            self.running = False
        elif cmd in ("help", "?"):
            self.print_help()
        elif cmd in ("neofetch", "novafetch"):
            self.print_neofetch()
        elif cmd == "clear":
            console.clear()
            self.show_banner()
        elif cmd == "sysinfo":
            hw = NovaSysInfo.get_hardware_telemetry()
            table = Table(title="[bold cyan]NovaOS Hardware & Security Telemetry[/bold cyan]")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            for k, v in hw.items():
                table.add_row(k.replace('_', ' ').title(), str(v))
            console.print(table)
        elif cmd == "defender":
            st = self.defender.get_status()
            table = Table(title="[bold cyan]Nova Defender - Real-Time Protection Hub[/bold cyan]")
            table.add_column("Feature", style="cyan")
            table.add_column("State", style="bold green")
            for k, v in st.items():
                table.add_row(k.replace('_', ' ').title(), str(v))
            console.print(table)
        elif cmd == "scan":
            target = args[0] if args else "/tmp"
            console.print(f"[bold cyan]Nova Defender scanning {target}...[/bold cyan]")
            res = self.defender.run_quick_scan(target)
            console.print(f"[bold green]Scan finished:[/bold green] {res['scanned_files']} files inspected, {res['threats_found']} threats detected.")
        elif cmd == "firewall":
            fw_st = self.firewall.get_status()
            console.print(Panel(
                f"[bold cyan]Status:[/bold cyan] {fw_st['status']}\n"
                f"[bold cyan]Active Rules:[/bold cyan] {fw_st['rule_count']}\n"
                f"[bold green]Allowed Packets:[/bold green] {fw_st['allowed_packets']}\n"
                f"[bold red]Dropped / Blocked Packets:[/bold red] {fw_st['dropped_packets']}\n"
                f"[bold yellow]Stealth Mode:[/bold yellow] Engaged (ICMP Echo Ignored)",
                title="[bold white]NovaWall Zero-Trust Firewall[/bold white]",
                style="cyan"
            ))
        elif cmd == "integrity":
            st = self.integrity.verify_system_state()
            table = Table(title="[bold cyan]TPM 2.0 PCR Measured Boot Registers[/bold cyan]")
            table.add_column("PCR #", style="bold yellow")
            table.add_column("Description", style="cyan")
            table.add_column("SHA-256 Digest", style="white")
            pcr_desc = {
                0: "UEFI Core Firmware",
                1: "Platform Motherboard Config",
                2: "Option ROMs / GPU",
                4: "NovaOS Stage-1/2 Bootloader",
                7: "Secure Boot Policy & Keys",
                8: "Kernel Arguments & Hardening",
                9: "Cryptographic Initramfs"
            }
            for pcr_num, digest in st["pcr_snapshot"].items():
                table.add_row(f"PCR[{pcr_num}]", pcr_desc.get(pcr_num, "Extension"), digest[:32] + "...")
            console.print(table)
        elif cmd == "install-os":
            from installer.wizard import NovaInstallerWizard
            wizard = NovaInstallerWizard()
            wizard.run()
            self.show_banner()
        elif cmd == "vault":
            sub = args[0] if args else "status"
            if sub == "init":
                pwd = args[1] if len(args) > 1 else "NovaVaultKey2026!"
                rec = self.vault.initialize(pwd)
                console.print(f"[bold green]Encrypted Vault initialized at {self.vault.vault_path}![/bold green]")
                console.print(f"[bold yellow]BitLocker Neo Recovery Key: [bold cyan]{rec}[/bold cyan][/bold yellow]")
            elif sub == "status":
                console.print(f"Vault Status: {'[bold green]UNLOCKED (Mounted at Drive V:)[/bold green]' if self.vault.is_unlocked else '[bold red]LOCKED (Encrypted with AES-256-GCM)[/bold red]'}")
            elif sub == "lock":
                self.vault.lock()
                console.print("[bold yellow]Vault locked and memory cleared.[/bold yellow]")
            else:
                console.print("[red]Usage: vault init <password> | vault status | vault lock[/red]")
        elif cmd == "shred":
            if not args:
                console.print("[red]Usage: shred <filepath>[/red]")
            else:
                target = args[0]
                if not os.path.exists(target):
                    console.print(f"[red]File not found: {target}[/red]")
                else:
                    NovaShredder.shred_file(target)
                    console.print(f"[bold green]File {target} shredded with DoD 5220.22-M (7 passes)![/bold green]")
        elif cmd == "matrix":
            self.run_matrix(3.0)
        else:
            console.print(f"[red]Unknown command: '{cmd}'. Type 'help' for available commands.[/red]")

    def run_interactive(self):
        console.clear()
        self.show_banner()
        while self.running:
            try:
                prompt_text = "[bold cyan]NovaOS[/bold cyan]:[bold green]~[/bold green]$ "
                cmd_line = console.input(prompt_text)
                self.execute_command(cmd_line)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Exiting NovaOS Terminal...[/bold yellow]")
                break
