# =====================================================================
# NovaOS — Futuristic Windows 11 Inspired Secure Operating System
# Build System & Live CD Packaging
# =====================================================================

PYTHON := python3
REPO_ROOT := $(shell pwd)

.PHONY: all iso verify test run-live install-os terminal defender clean help

all: iso

## iso: Build bootloader, initramfs, and bootable El Torito ISO image
iso:
	@echo ">>> Building NovaOS Live CD & Installer ISO..."
	$(PYTHON) tools/build_iso.py

## verify: Validate ISO 9660 and El Torito boot structures
verify:
	@echo ">>> Verifying NovaOS ISO Compliance..."
	$(PYTHON) tools/verify_iso.py

## test: Run full unit and security compliance test suite
test:
	@echo ">>> Running NovaOS Automated Test Suite..."
	$(PYTHON) -m unittest discover -s tests -v

## run-live: Boot into NovaOS Live CD Environment (Native Desktop Shell)
run-live:
	@./bin/novaos

## install-os: Launch NovaOS Setup Wizard (Deploy to NVMe/SSD)
install-os:
	@./bin/novaos-installer

## terminal: Launch NovaOS Cybernetic PowerShell Neo Terminal
terminal:
	@./bin/novaos-terminal

## defender: Launch Nova Defender Security Center
defender:
	@./bin/novaos-defender

## clean: Remove build artifacts and temporary files
clean:
	@echo ">>> Cleaning build artifacts..."
	rm -f boot/*.o boot/*.so boot/*.bin boot/BOOTX64.EFI boot/vmlinuz-novaos boot/initrd-novaos.img boot/efiboot.img
	rm -rf dist/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo ">>> Clean completed."

## help: Display available make targets
help:
	@echo "NovaOS Build and Execution Commands:"
	@echo "  make iso         - Compile bootloaders and generate bootable Live CD ISO"
	@echo "  make verify      - Validate ISO El Torito / UEFI structure"
	@echo "  make test        - Run all cryptographic and security test cases"
	@echo "  make run-live    - Run NovaOS Futuristic Windows 11 Desktop natively"
	@echo "  make install-os  - Run NovaOS Setup Wizard to install to disk"
	@echo "  make terminal    - Open Nova Terminal"
	@echo "  make defender    - Open Nova Defender Security Center"
	@echo "  make clean       - Remove compiled files"
