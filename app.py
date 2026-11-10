from pathlib import Path
import chainlit as cl
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from config import MARITACA_API_KEY, SYSTEM_PROMPT
from tools import ALL_TOOLS


@cl.on_chat_start
async def on_chat_start():
    """Inicializa a sessão do agente HarpiaSec ao conectar um novo usuário."""
    llm = ChatOpenAI(
        model="s5",
        api_key=MARITACA_API_KEY,
        base_url="https://chat.maritaca.ai/api",
        default_headers={"X-Maritaca-Route": "flex", "reasoning_effort": "none"},
    )

    memory = MemorySaver()
    agent_app = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    # Armazena as instâncias na sessão individual do cliente
    cl.user_session.set("agent_app", agent_app)
    cl.user_session.set(
        "config", {"configurable": {"thread_id": f"session_{cl.context.session.id}"}}
    )

    await cl.Message(
        content="🛡️ **HarpiaSec Ativo no Chainlit!**\n\nPronto para executar auditorias de rede, fuzzing com HTTPX, consultas OUI/CVE e relatórios em PDF."
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Processa a mensagem do usuário executando o grafo do LangGraph."""
    agent_app = cl.user_session.get("agent_app")
    config = cl.user_session.get("config")

    msg = cl.Message(content="")
    await msg.send()

    try:
        # Associa o CallbackHandler do Chainlit para renderizar as ferramentas e o raciocínio em tempo real
        cb = cl.LangchainCallbackHandler()
        config["callbacks"] = [cb]

        # Invocação assíncrona do LangGraph
        output = await agent_app.ainvoke(
            {"messages": [("user", message.content)]},
            config=config,
        )

        final_message = output["messages"][-1]
        msg.content = final_message.content
        await msg.update()

        # Verifica se novos PDFs foram criados e disponibiliza como anexo no chat
        pdf_files = list(Path.cwd().glob("*.pdf"))
        if pdf_files:
            # Pega o PDF gerado mais recentemente
            ultimo_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
            elements = [
                cl.File(
                    name=ultimo_pdf.name,
                    path=str(ultimo_pdf),
                    display="inline",
                )
            ]
            await cl.Message(
                content=f"📄 **Relatório de Auditoria:** `{ultimo_pdf.name}`",
                elements=elements,
            ).send()

    except Exception as e:
        msg.content = f"❌ Ocorreu um erro durante a execução: {str(e)}"
        await msg.update()
