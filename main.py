import os
import threading
import flet as ft
from google import genai
from gtts import gTTS
import speech_recognition as sr

# INSIRA SUA CHAVE DA API DO GEMINI AQUI:
API_KEY = "AQ.Ab8RN6Ie-fxVchE7lLG5IgoMKZvymy8ehXtZfhXOqApjSNWoZw"

# Inicializa o cliente do Gemini
client = genai.Client(api_key=API_KEY) if API_KEY != "SUA_CHAVE_AQUI" else None

SYSTEM_INSTRUCTION = """
Você é o J.A.R.V.I.S. (Just A Rather Very Intelligent System), o assistente pessoal 
inteligente criado por Tony Stark. 
Responda sempre em português do Brasil, mantendo um tom formal, altamente eficiente, 
extremamente leal, polido e com um toque sutil de ironia inteligente. 
Trate o usuário como "senhor". Seja direto, útil e mantenha as respostas curtas 
para facilitar a fala em voz alta.
"""

def main(page: ft.Page):
    page.title = "J.A.R.V.I.S. - Sistema Central"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0F19"

    titulo = ft.Text("J.A.R.V.I.S. v3.0", size=22, weight=ft.FontWeight.BOLD, color="#00E5FF")
    status_label = ft.Text("Sistemas operacionais online", size=11, color="#64748B")

    chat_historico = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

    campo_entrada = ft.TextField(
        hint_text="Digite ou clique no microfone...",
        border_color="#00E5FF",
        focused_border_color="#00FFCC",
        color=ft.colors.WHITE,
        expand=True,
        on_submit=lambda e: processar_texto(campo_entrada.value)
    )

    def adicionar_mensagem(remetente, texto):
        cor_texto = "#00FFCC" if remetente == "J.A.R.V.I.S." else ft.colors.WHITE
        chat_historico.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{remetente}:", size=11, weight=ft.FontWeight.BOLD, color="#00E5FF"),
                    ft.Text(texto, size=14, color=cor_texto)
                ]),
                padding=10,
                border_radius=8,
                bgcolor="#1E293B" if remetente == "J.A.R.V.I.S." else "#334155",
            )
        )
        page.update()

    def falar_texto(texto):
        try:
            tts = gTTS(text=texto, lang='pt', tld='com.br')
            arquivo_audio = "jarvis_fala.mp3"
            tts.save(arquivo_audio)
            
            if os.name == 'posix':
                os.system(f"am start -a android.intent.action.VIEW -d file://{os.path.abspath(arquivo_audio)} -t audio/mp3 > /dev/null 2>&1")
            else:
                os.system(f"start {arquivo_audio}")
        except Exception as e:
            print(f"[Aviso de Áudio]: {e}")

    def enviar_para_ia(texto_usuario):
        if not texto_usuario.strip():
            return
        
        adicionar_mensagem("Senhor", texto_usuario)
        page.update()

        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=texto_usuario,
                    config={'system_instruction': SYSTEM_INSTRUCTION}
                )
                resposta_ia = response.text
            except Exception as ex:
                resposta_ia = f"Erro de conexão: {ex}"
        else:
            resposta_ia = "Por favor, configure sua chave de API do Gemini no código."

        adicionar_mensagem("J.A.R.V.I.S.", resposta_ia)
        status_label.value = "Sistemas operacionais online"
        status_label.color = "#64748B"
        page.update()

        threading.Thread(target=falar_texto, args=(resposta_ia,)).start()

    def processar_texto(texto):
        campo_entrada.value = ""
        page.update()
        threading.Thread(target=enviar_para_ia, args=(texto,)).start()

    def escutar_microfone(e):
        def ouvir_tarefa():
            status_label.value = "Ouvindo o senhor... Fale agora."
            status_label.color = "#00FFCC"
            botao_mic.icon_color = "#00FFCC"
            page.update()

            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5)
                
                comando = recognizer.recognize_google(audio, language="pt-BR")
                
                status_label.value = "Processando comando..."
                page.update()
                
                enviar_para_ia(comando)
                
            except Exception as ex:
                status_label.value = "Erro no microfone ou áudio não compreendido."
                status_label.color = "#FF5555"
            finally:
                botao_mic.icon_color = "#00E5FF"
                page.update()

        threading.Thread(target=ouvir_tarefa).start()

    botao_enviar = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color="#00E5FF",
        tooltip="Enviar Texto",
        on_click=lambda e: processar_texto(campo_entrada.value)
    )

    botao_mic = ft.IconButton(
        icon=ft.icons.MIC_ROUNDED,
        icon_color="#00E5FF",
        tooltip="Falar",
        on_click=escutar_microfone
    )

    page.add(
        ft.Column([
            ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([status_label], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color="#1E293B"),
            chat_historico,
            ft.Row([campo_entrada, botao_mic, botao_enviar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], expand=True)
    )

    saudação_inicial = "Sistemas operacionais integrados. Núcleo de voz e inteligência ativos, senhor."
    adicionar_mensagem("J.A.R.V.I.S.", saudação_inicial)
    threading.Thread(target=falar_texto, args=(saudação_inicial,)).start()

ft.app(target=main)
