"""Layout do app Idiomas.

Barra superior: menu de configurações/conta (esq.), logo (centro), língua (dir.).
Logo abaixo, as áreas (Básico, Comida, Gramática…). No meio, a trilha de estações,
cada uma com n perguntas. No rodapé, o botão de sugestão para mandar feedback.
"""

from __future__ import annotations

import flet as ft

import conteudo as ct
from nucleo import Contexto, Registro, componentes as c

PROGRESSO, PREFERENCIAS, FEEDBACK = "progresso", "preferencias", "feedback"
COR_ACERTO, COR_ERRO = "#16A34A", "#DC2626"


class AppIdiomas:
    def __init__(self, ctx: Contexto) -> None:
        self.ctx, self.page, self.tema = ctx, ctx.page, ctx.config.tema
        self.lingua = ct.lingua(self._lingua_salva())
        self.area = self.lingua.areas[0]
        self.conteudo = ft.SafeArea(content=ft.Container(), expand=True)

    # ---- dados ---------------------------------------------------------------

    @property
    def _dono(self) -> dict[str, str]:
        return {"dono": self.ctx.usuario.id}

    def _lingua_salva(self) -> str:
        prefs = self.ctx.dados.listar(PREFERENCIAS, self._dono)
        return prefs[0]["lingua"] if prefs else ct.LINGUAS[0].id

    def _salvar_lingua(self) -> None:
        prefs = self.ctx.dados.listar(PREFERENCIAS, self._dono)
        if prefs:
            self.ctx.dados.atualizar(PREFERENCIAS, prefs[0]["id"], {"lingua": self.lingua.id})
        else:
            self.ctx.dados.criar(PREFERENCIAS, {**self._dono, "lingua": self.lingua.id})

    def _concluidas(self) -> dict[int, Registro]:
        filtros = {**self._dono, "lingua": self.lingua.id, "area": self.area.id}
        return {r["estacao"]: r for r in self.ctx.dados.listar(PROGRESSO, filtros)}

    def _salvar_progresso(self, indice: int, acertos: int, total: int) -> None:
        anterior = self._concluidas().get(indice)
        if anterior is None:
            self.ctx.dados.criar(PROGRESSO, {**self._dono, "lingua": self.lingua.id, "area": self.area.id,
                                             "estacao": indice, "acertos": acertos, "total": total})
        elif acertos > anterior["acertos"]:
            self.ctx.dados.atualizar(PROGRESSO, anterior["id"], {"acertos": acertos})

    # ---- estrutura -----------------------------------------------------------

    def montar(self) -> None:
        page, tema = self.page, self.tema
        page.appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.MENU, tooltip="Menu", on_click=self._abrir_menu),
            title=self._logo_barra(),
            center_title=True,
            bgcolor=tema.cor_superficie,
            actions=[self._menu_linguas()],
        )
        page.drawer = ft.NavigationDrawer(
            selected_index=0,
            on_change=self._ao_escolher_menu,
            controls=[
                ft.Container(c.titulo(self.ctx.config.nome, tema, 18), padding=ft.Padding.all(20)),
                ft.NavigationDrawerDestination(icon=ft.Icons.ROUTE_OUTLINED, label="Trilha"),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Configurações"),
                ft.NavigationDrawerDestination(icon=ft.Icons.PERSON_OUTLINE, label="Conta"),
            ],
        )
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.FEEDBACK_OUTLINED, tooltip="Enviar sugestão", on_click=self.abrir_sugestao,
            bgcolor=tema.cor_primaria, foreground_color=tema.cor_sobre_primaria,
        )
        page.floating_action_button_location = ft.FloatingActionButtonLocation.START_FLOAT
        page.add(self.conteudo)
        self.mostrar_trilha(atualizar=False)

    def _logo_barra(self) -> ft.Control:
        logo = self.ctx.config.logo
        if logo.src:
            return ft.Image(src=logo.src, height=32, fit=ft.BoxFit.CONTAIN)
        return ft.Row([ft.Icon(c.icone(logo.icone), color=self.tema.cor_primaria),
                       ft.Text(self.ctx.config.nome, weight=ft.FontWeight.BOLD, color=self.tema.cor_texto)],
                      tight=True, spacing=8)

    def _menu_linguas(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            icon=ft.Icons.TRANSLATE,
            icon_color=self.tema.cor_primaria,
            tooltip="Língua que estou aprendendo",
            items=[ft.PopupMenuItem(content=x.nome, checked=x.id == self.lingua.id,
                                    on_click=lambda _, id_=x.id: self.trocar_lingua(id_))
                   for x in ct.LINGUAS],
        )

    def _mostrar(self, controle: ft.Control, com_sugestao: bool, atualizar: bool = True) -> None:
        self.conteudo.content = controle
        self.page.floating_action_button.visible = com_sugestao
        if atualizar:
            self.page.update()

    async def _abrir_menu(self, _=None) -> None:
        await self.page.show_drawer()

    async def _ao_escolher_menu(self, e) -> None:
        await self.page.close_drawer()
        [self.mostrar_trilha, self.mostrar_configuracoes, self.mostrar_conta][e.control.selected_index]()

    # ---- ações ---------------------------------------------------------------

    def trocar_lingua(self, id_: str) -> None:
        self.lingua = ct.lingua(id_)
        self.area = self.lingua.area(self.area.id)
        self._salvar_lingua()
        self.page.appbar.actions = [self._menu_linguas()]
        self.mostrar_trilha()

    def trocar_area(self, id_: str) -> None:
        self.area = self.lingua.area(id_)
        self.mostrar_trilha()

    # ---- trilha --------------------------------------------------------------

    def mostrar_trilha(self, _=None, atualizar: bool = True) -> None:
        self._mostrar(ft.Column([self._seletor_areas(), self._trilha()], expand=True, spacing=16),
                      com_sugestao=True, atualizar=atualizar)

    def _seletor_areas(self) -> ft.Row:
        tema = self.tema
        chips = []
        for a in self.lingua.areas:
            ativa = a.id == self.area.id
            chips.append(ft.Chip(
                label=ft.Text(a.nome, color=tema.cor_sobre_primaria if ativa else tema.cor_texto),
                leading=ft.Icon(c.icone(a.icone), color=tema.cor_sobre_primaria if ativa else tema.cor_primaria),
                selected=ativa, show_checkmark=False,
                selected_color=tema.cor_primaria, bgcolor=tema.cor_superficie,
                on_select=lambda _, id_=a.id: self.trocar_area(id_),
            ))
        return ft.Row(chips, scroll=ft.ScrollMode.AUTO, spacing=8)

    def _trilha(self) -> ft.ListView:
        tema, estacoes = self.tema, self.area.estacoes
        feitas = self._concluidas()
        itens: list[ft.Control] = [
            c.titulo(f"{self.lingua.nome} · {self.area.nome}", tema, 20),
            ft.Text(f"{len(feitas)} de {len(estacoes)} estações concluídas", color=tema.cor_texto,
                    opacity=0.7, text_align=ft.TextAlign.CENTER),
            ft.Container(height=12),
        ]
        for i, estacao in enumerate(estacoes):
            liberada = i == 0 or (i - 1) in feitas
            if i:
                itens.append(ft.Container(width=4, height=32, border_radius=ft.BorderRadius.all(2),
                                          bgcolor=tema.cor_primaria if liberada else tema.cor_superficie))
            itens.append(self._estacao(i, estacao, feitas.get(i), liberada))
        return ft.ListView(
            [ft.Column(itens, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)],
            expand=True, padding=ft.Padding.only(bottom=96),
        )

    def _estacao(self, indice: int, estacao: ct.Estacao, feita: Registro | None, liberada: bool) -> ft.Control:
        tema = self.tema
        if feita:
            icone, fundo, cor, borda = ft.Icons.CHECK, tema.cor_primaria, tema.cor_sobre_primaria, tema.cor_primaria
            detalhe = f"{feita['acertos']}/{feita['total']} acertos"
        elif liberada:
            icone, fundo, cor, borda = ft.Icons.PLAY_ARROW, tema.cor_superficie, tema.cor_primaria, tema.cor_primaria
            detalhe = f"{len(estacao.perguntas)} perguntas"
        else:
            icone, fundo, cor, borda = ft.Icons.LOCK_OUTLINE, tema.cor_superficie, tema.cor_texto, tema.cor_superficie
            detalhe = "Conclua a anterior"
        no = ft.Container(
            content=ft.Icon(icone, color=cor, size=32), width=76, height=76, bgcolor=fundo,
            border=ft.Border.all(3, borda), border_radius=ft.BorderRadius.all(38), alignment=ft.Alignment.CENTER,
            on_click=(lambda _: self.abrir_estacao(indice)) if liberada else None,
            opacity=1 if liberada else 0.5, tooltip=estacao.titulo,
        )
        return ft.Column(
            [no, ft.Text(f"{indice + 1}. {estacao.titulo}", weight=ft.FontWeight.BOLD, color=tema.cor_texto),
             ft.Text(detalhe, size=12, color=tema.cor_texto, opacity=0.7)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
        )

    # ---- estação (perguntas) -------------------------------------------------

    def abrir_estacao(self, indice: int) -> None:
        tema, estacao = self.tema, self.area.estacoes[indice]
        perguntas, estado = estacao.perguntas, {"atual": 0, "acertos": 0}
        corpo = ft.Column(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO,
                          horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        def avancar(_=None) -> None:
            estado["atual"] += 1
            renderizar()
            self.page.update()

        def renderizar() -> None:
            n, i = len(perguntas), estado["atual"]
            if i == n:
                self._salvar_progresso(indice, estado["acertos"], n)
                corpo.controls = [
                    ft.Icon(ft.Icons.EMOJI_EVENTS_OUTLINED, size=72, color=tema.cor_primaria),
                    c.titulo("Estação concluída!", tema),
                    ft.Text(f"{estado['acertos']} de {n} acertos", color=tema.cor_texto,
                            text_align=ft.TextAlign.CENTER),
                    c.botao_primario("Voltar à trilha", self.mostrar_trilha, tema),
                ]
                return
            pergunta = perguntas[i]
            resultado = ft.Text("", visible=False, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
            proxima = c.botao_primario("Próxima" if i + 1 < n else "Ver resultado", avancar, tema)
            proxima.visible = False
            opcoes: list[ft.Button] = []

            def responder(escolha: int) -> None:
                certo = escolha == pergunta.correta
                estado["acertos"] += certo
                for j, botao in enumerate(opcoes):
                    botao.disabled = True
                    if j == pergunta.correta:
                        botao.bgcolor = COR_ACERTO
                    elif j == escolha:
                        botao.bgcolor = COR_ERRO
                resultado.value = "Isso!" if certo else f"Resposta certa: {pergunta.opcoes[pergunta.correta]}"
                resultado.color = COR_ACERTO if certo else COR_ERRO
                resultado.visible = proxima.visible = True
                self.page.update()

            opcoes.extend(
                ft.Button(content=texto, on_click=lambda _, j=j: responder(j), bgcolor=tema.cor_superficie,
                          color=tema.cor_texto, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                                                     padding=ft.Padding.symmetric(vertical=16)))
                for j, texto in enumerate(pergunta.opcoes)
            )
            corpo.controls = [
                ft.Row([ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Sair da estação", on_click=self.mostrar_trilha),
                        ft.Text(f"{estacao.titulo} · {i + 1}/{n}", color=tema.cor_texto, expand=True)]),
                ft.ProgressBar(value=i / n, color=tema.cor_primaria, bgcolor=tema.cor_superficie),
                ft.Text(pergunta.enunciado, size=20, weight=ft.FontWeight.BOLD, color=tema.cor_texto),
                *opcoes,
                resultado,
                proxima,
            ]

        renderizar()
        self._mostrar(corpo, com_sugestao=False)

    # ---- configurações e conta -----------------------------------------------

    def mostrar_configuracoes(self) -> None:
        tema = self.tema
        grupo = ft.RadioGroup(
            value=self.lingua.id,
            on_change=lambda e: self.trocar_lingua(e.control.value),
            content=ft.Column([ft.Radio(value=x.id, label=x.nome, active_color=tema.cor_primaria)
                               for x in ct.LINGUAS]),
        )
        self._mostrar(ft.Column([c.titulo("Configurações", tema),
                                 ft.Text("Língua que estou aprendendo", color=tema.cor_texto, opacity=0.7), grupo],
                                spacing=16), com_sugestao=True)

    def mostrar_conta(self) -> None:
        tema, usuario = self.tema, self.ctx.usuario
        self._mostrar(ft.Column([c.titulo("Conta", tema),
                                 c.cartao(usuario.nome or "Sem nome", usuario.email, tema),
                                 c.botao_primario("Sair", self.ctx.sair, tema)],
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=16),
                      com_sugestao=True)

    # ---- sugestão ------------------------------------------------------------

    def abrir_sugestao(self, _=None) -> None:
        tema, page = self.tema, self.page
        campo = c.campo("O que podemos melhorar?", tema)
        campo.multiline, campo.min_lines, campo.max_lines = True, 3, 6
        erro = c.mensagem_erro()

        def enviar(_=None) -> None:
            texto = (campo.value or "").strip()
            if not texto:
                erro.value, erro.visible = "Escreva sua sugestão antes de enviar.", True
                page.update()
                return
            self.ctx.dados.criar(FEEDBACK, {**self._dono, "texto": texto,
                                            "lingua": self.lingua.id, "area": self.area.id})
            page.pop_dialog()
            page.show_dialog(ft.SnackBar(ft.Text("Obrigado! Sugestão enviada.")))

        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Enviar sugestão"),
            content=ft.Column([campo, erro], tight=True, spacing=8),
            actions=[ft.TextButton(content="Cancelar", on_click=lambda _: page.pop_dialog()),
                     c.botao_primario("Enviar", enviar, tema)],
        ))


def montar_app(ctx: Contexto) -> None:
    AppIdiomas(ctx).montar()
