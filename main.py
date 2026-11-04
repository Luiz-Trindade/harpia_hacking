from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from rich.markdown import Markdown
from rich.panel import Panel
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, RichLog, Static

from config import MARITACA_API_KEY, SYSTEM_PROMPT
from tools import ALL_TOOLS


class HarpiaSecApp(App):
    CSS = """
    Screen {
        background: $surface-darken-3;
    }

    #chat-log {
        height: 1fr;
        border: solid green;
        background: $surface;
        padding: 1;
    }

    #status-bar {
        height: auto;
        display: none;
        padding: 0 1;
        color: $warning;
        background: $surface-darken-1;
    }

    Input {
        dock: bottom;
        border: solid cyan;
    }
    """

    TITLE = "🛡️ HarpiaSec - IA Agent para Ethical Hacking"
    SUB_TITLE = "LangGraph Engine | Textual TUI"

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="chat-log", wrap=True, highlight=True, markup=True)
        yield Static("⚙️ Executando fluxo do grafo e ferramentas...", id="status-bar")
        yield Input(
            placeholder="Digite seu comando para o HarpiaSec (ex: 'Analise minha rede local')...",
            id="user-input",
        )
        yield Footer()

    def on_mount(self) -> None:
        # LLM mantido com as configurações exatas fornecidas
        self.llm = ChatOpenAI(
            model="s5",
            api_key=MARITACA_API_KEY,
            base_url="https://chat.maritaca.ai/api",
            default_headers={"X-Maritaca-Route": "flex", "reasoning_effort": "none"},
        )

        memory = MemorySaver()
        self.agent_app = create_react_agent(
            model=self.llm,
            tools=ALL_TOOLS,
            prompt=SYSTEM_PROMPT,
            checkpointer=memory,
        )
        self.config = {"configurable": {"thread_id": "harpiasec_session"}}

        log = self.query_one("#chat-log", RichLog)
        log.write(
            "[bold cyan]🛡️ HarpiaSec TUI ativo![/bold cyan] Digite sua solicitação no campo abaixo."
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return

        input_widget = self.query_one("#user-input", Input)
        input_widget.value = ""

        if user_text.lower() in ["sair", "exit", "quit"]:
            self.exit()
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold blue]Analista:[/bold blue] {user_text}\n")

        status_bar = self.query_one("#status-bar", Static)
        status_bar.styles.display = "block"

        self.process_agent_response(user_text)

    @work(exclusive=True, thread=True)
    def process_agent_response(self, user_text: str) -> None:
        try:
            output = self.agent_app.invoke(
                {"messages": [("user", user_text)]},
                config=self.config,
            )
            final_message = output["messages"][-1]
            content = final_message.content
        except Exception as e:
            content = f"❌ Ocorreu um erro durante a execução: {e}"

        self.call_from_thread(self.update_ui_with_response, content)

    def update_ui_with_response(self, content: str) -> None:
        status_bar = self.query_one("#status-bar", Static)
        status_bar.styles.display = "none"

        log = self.query_one("#chat-log", RichLog)
        log.write(
            Panel(
                Markdown(content),
                title="[bold green]HarpiaSec Output[/bold green]",
                border_style="green",
                expand=False,
            )
        )


def main():
    app = HarpiaSecApp()
    app.run()


if __name__ == "__main__":
    main()
