# NovaOS — Makefile
# Raccourcis : make build / test / check / clean

.PHONY: all build test check clean help

all: build

help:
	@echo "Cibles disponibles :"
	@echo "  make build  — construit l'ISO NovaOS (root requis)"
	@echo "  make test   — démarre l'ISO dans QEMU"
	@echo "  make check  — vérifie la syntaxe des scripts"
	@echo "  make clean  — supprime les artefacts de build"

build:
	./build.sh

test:
	./vm-test.sh

check:
	bash -n build.sh
	bash -n vm-test.sh
	@find config/hooks -name '*.chroot' -exec bash -n {} \;
	@echo "✔ Syntaxe des scripts OK"

clean:
	-sudo lb clean
	sudo rm -rf chroot binary cache auto .build
	sudo rm -f *.iso *.iso.* *.squashfs *.manifest *.packages *.buildlog
