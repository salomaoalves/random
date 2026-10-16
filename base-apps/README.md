# Plataforma de apps — Python + Flet

Um pacote pai (`nucleo`) e apps filhos (`app_alfa`, `app_beta`) que geram Android e iOS com o Flet 1.0.

```
plataforma-apps/
├── nucleo/                  pacote pai (igual em todos)
│   └── src/nucleo/
│       ├── config.py        contrato AppConfig: tema, logo, rodapé, dados, auth
│       ├── dados/           interface Repositorio + implementação em memória
│       ├── auth/            interface ServicoAuth + implementação em memória
│       ├── ui/              blocos (logo, campo, botões, rodapé, cartão) + login padrão
│       └── app.py           iniciar_app: troca entre login e app pelo estado de auth
├── apps/
│   ├── app_alfa/            abas inferiores + lista; usa o login padrão
│   └── app_beta/            menu lateral + grade; login próprio
├── scripts/
│   ├── novo_app.py          cria um filho novo a partir de outro
│   └── preparar_build.py    copia o nucleo para o app antes do build
└── tests/
```

## O que fica onde

| Muda entre apps (filho) | Igual em todos (pai) |
|---|---|
| `src/config_app.py`: nome, cores, logo, rodapé, credenciais do banco | Login, cadastro, esqueci a senha, Google, sessão |
| `src/telas.py`: telas, navegação, layout, login próprio (opcional) | Blocos de UI e tela de login padrão |
| | Interface de dados e a implementação do banco |

Como o banco é o mesmo em todos, a implementação dele fica no pai. Cada filho só aponta para a própria instância (`projeto`, `url`, `chave`).

## Rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./nucleo
cd apps/app_alfa && flet run src/main.py     # janela no computador
flet run --android src/main.py               # no celular, via app Flet (mesma rede)
```

Testes (sem abrir janela): `python -m unittest discover tests`

## Gerar Android / iOS

```bash
python scripts/preparar_build.py app_alfa
cd apps/app_alfa
flet build apk          # Android
flet build ipa          # iOS (precisa de macOS + Xcode + conta Apple Developer)
```

O `preparar_build.py` copia o `nucleo` para `src/nucleo` do app, porque o `flet build` empacota só a pasta do app.

## Novo app filho

```bash
python scripts/novo_app.py app_gama "App Gama"                  # copia o app_alfa
python scripts/novo_app.py app_gama "App Gama" --base app_beta  # copia o app_beta
```

Depois edite `config_app.py` e `telas.py`, e troque `org`/`product` no `pyproject.toml`.

## Quando o banco for definido

1. Crie `nucleo/src/nucleo/dados/<provedor>.py` com uma subclasse de `Repositorio` (5 métodos: `listar`, `obter`, `criar`, `atualizar`, `remover`).
2. Registre em `nucleo/src/nucleo/dados/__init__.py`, em `_PROVEDORES`.
3. Nos filhos, troque `provedor="memoria"` pelo nome novo. As telas não mudam.

Auth segue o mesmo padrão em `nucleo/src/nucleo/auth/`. O Google real pode usar `page.login()` do Flet dentro de `entrar_google(page)`. Hoje, em modo memória, ele só simula um usuário.

Credenciais vêm de variáveis de ambiente (`ALFA_DB_URL`, `ALFA_DB_CHAVE`, `ALFA_GOOGLE_CLIENT_ID`…), nunca escritas no código.

## Pendências

- Implementação real de banco e auth (hoje em memória: os dados somem ao fechar o app).
- Login com Apple, se for publicar na App Store com login social.
