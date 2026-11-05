#!/bin/bash
# ============================================================
# lab_recon.sh
# Script de apoio para reconhecimento inicial do ambiente de
# laboratório (Kali Linux -> Metasploitable 2 / DVWA)
#
# USO EXCLUSIVO EM AMBIENTE DE LABORATÓRIO ISOLADO (host-only)
# Não execute contra hosts que você não tenha autorização
# explícita para testar.
# ============================================================

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Uso: $0 <IP_DO_ALVO>"
  exit 1
fi

TARGET="$1"
OUTDIR="recon_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "[*] Alvo: $TARGET"
echo "[*] Resultados serão salvos em: $OUTDIR"

echo "[*] Etapa 1/3 - Descoberta de portas e serviços (nmap)"
nmap -sV -p21,22,80,139,445 -oN "$OUTDIR/nmap_scan.txt" "$TARGET"

echo "[*] Etapa 2/3 - Enumeração de compartilhamentos/usuários SMB"
enum4linux -a "$TARGET" | tee "$OUTDIR/enum4linux.txt"

echo "[*] Etapa 3/3 - Finalizado. Revise os arquivos em $OUTDIR"
echo "    Em seguida, utilize o Medusa conforme documentado no README.md"
