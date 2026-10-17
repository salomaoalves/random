# Plataforma de apps — Python + Flet

Um pacote pai (`core`) e apps filhos (`app_alpha`, `app_beta`) que geram Android e iOS com o Flet 1.0.
O código é todo em inglês; a interface sai em inglês por padrão e no idioma do aparelho quando houver tradução.

```
base-apps/
├── core/                    pacote pai (igual em todos)
│   └── src/core/
│       ├── config.py        contrato AppConfig: tema, logo, rodapé, dados, auth, textos
│       ├── i18n.py          textos por idioma (en padrão, pt, es) e Translator
│       ├── data/            interface Repository + implementação em memória
│       ├── auth/            interface AuthService + implementação em memória
│       ├── ui/              blocos (logo, campo, botões, rodapé, cartão) + login padrão
│       └── app.py           create_main/run_app: idioma do aparelho, troca entre login e app
├── apps/
│   ├── app_alpha/           abas inferiores + lista; usa o login padrão
│   ├── app_beta/            menu lateral + grade; login próprio
│   └── app_bheh/            Bheh, app de idiomas: cursos, áreas, trilha de estações, sugestões
├── scripts/
│   ├── new_app.py           cria um filho novo a partir de outro
│   └── prepare_build.py     copia o core para o app antes do build
└── tests/
```

## O que fica onde

| Muda entre apps (filho) | Igual em todos (pai) |
|---|---|
| `src/app_config.py`: nome, cores, logo, rodapé, credenciais do banco | Login, cadastro, Google, sessão |
| `src/strings.py`: textos do app em cada idioma | Textos do login e mensagens de erro em cada idioma |
| `src/screens.py`: telas, navegação, layout, login próprio (opcional) | Blocos de UI e tela de login padrão |
| | Interface de dados e a implementação do banco |

Como o banco é o mesmo em todos, a implementação dele fica no pai. Cada filho só aponta para a própria instância (`project`, `url`, `key`).

## Idiomas

- Ao abrir, o `core` lê os idiomas do aparelho (`page.get_device_info()`) e usa o primeiro que tiver tradução; sem nenhum, usa inglês. Se o usuário trocar o idioma do sistema com o app aberto (`page.on_locale_change`), a tela é refeita no idioma novo.
- Nas telas, use `ctx.t("chave")` (aceita valores: `ctx.t("dashboard.record", number=3)`). Chave sem tradução cai no inglês e, se nem lá existir, aparece como está, então texto fixo também funciona.
- Conteúdo que carrega a própria tradução (ex.: perguntas) pode ser `{"en": ..., "pt": ...}` e é resolvido com `ctx.i18n.localize(valor)`.
- Para um idioma novo, acrescente o código (ex.: `"fr"`) em `CORE_STRINGS` e no `strings.py` de cada app. Os testes conferem se todos os idiomas têm as mesmas chaves.
- O idioma vem do aparelho, não da conta Google: o login do Google não garante esse dado.

## Rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./core
cd apps/app_alpha && flet run src/main.py     # janela no computador
flet run --android src/main.py               # no celular, via app Flet (mesma rede)
```

Testes (sem abrir janela): `python -m unittest discover tests`

## Gerar Android / iOS

```bash
python scripts/prepare_build.py app_alpha
cd apps/app_alpha
flet build apk          # Android
flet build ipa          # iOS (precisa de macOS + Xcode + conta Apple Developer)
```

O `prepare_build.py` copia o `core` para `src/core` do app, porque o `flet build` empacota só a pasta do app.

## Bheh

`apps/app_bheh` usa o login padrão com a paleta preto/verde neon. Depois de entrar:

- barra superior: menu (configurações e conta) à esquerda, logo no centro, língua que está aprendendo à direita;
- abaixo dela, as áreas (Básico, Comida, Gramática), cada uma com perguntas diferentes;
- no meio, a trilha: estações interligadas com n perguntas cada; a próxima libera quando a anterior é concluída;
- no rodapé, o botão de sugestão, que grava o feedback em `ctx.data` (coleção `feedback`).

O conteúdo fica em `src/content.py`: enunciados e respostas no idioma do usuário vêm em inglês e português; o que está na língua estudada fica como texto simples. Progresso, curso escolhido e sugestões ficam em `ctx.data`.

## Novo app filho

```bash
python scripts/new_app.py app_gamma "App Gamma"                  # copia o app_alpha
python scripts/new_app.py app_gamma "App Gamma" --base app_beta  # copia o app_beta
```

Depois edite `app_config.py`, `strings.py` e `screens.py`, e troque `org`/`product` no `pyproject.toml`.

## Quando o banco for definido

1. Crie `core/src/core/data/<provedor>.py` com uma subclasse de `Repository` (5 métodos: `list`, `get`, `create`, `update`, `delete`).
2. Registre em `core/src/core/data/__init__.py`, em `_PROVIDERS`.
3. Nos filhos, troque `provider="memory"` pelo nome novo. As telas não mudam.

Auth segue o mesmo padrão em `core/src/core/auth/`. O Google real pode usar `page.login()` do Flet dentro de `sign_in_google(page)`. Hoje, em modo memória, ele só simula um usuário. Erros de auth levam uma chave de tradução (`AuthError("auth.invalid_email")`), e a tela mostra o texto no idioma atual.

Credenciais vêm de variáveis de ambiente (`ALPHA_DB_URL`, `ALPHA_DB_KEY`, `ALPHA_GOOGLE_CLIENT_ID`…), nunca escritas no código.

## Pendências

- Implementação real de banco e auth (hoje em memória: os dados somem ao fechar o app).
- Login com Apple, se for publicar na App Store com login social.
