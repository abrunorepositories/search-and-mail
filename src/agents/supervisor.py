from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from src.tools.tracing import LangfuseTracer


def _summarize_conversation(conversation_history):
    summary = "\n\n".join([
        f"{step['worker']}:\n{step['result']}"
        for step in conversation_history
    ])
    return summary


def _format_results(conversation_history: List[Dict]) -> str:
    sections = []

    for entry in conversation_history:
        sections.append(f"=== {entry['worker']} ===\n{entry['result']}\n")

    return "\n".join(sections)


class Supervisor:
    def __init__(
            self,
            model: ChatOpenAI,
            tracer: LangfuseTracer,
            supervisor_name: str = "Supervisor",
            supervisor_prompt: str = None,
            summarization: bool = False,
            recursion_limit: int = 100,
            memory: Optional[ConversationBufferMemory] = None
    ):
        self.model = model
        self.name: str = supervisor_name
        self.tracer = tracer
        self.prompt: Optional[str] = supervisor_prompt
        self.summarize: bool = summarization
        self.recursion_limit: int = recursion_limit
        self.memory: ConversationBufferMemory = memory or ConversationBufferMemory()
        self.workers = {}

    def register_worker(self, worker):
        self.workers[worker.name] = worker

    def manage_conversation(self, person_name: str) -> str:
        user_request = f"Pesquise informações sobre {person_name}."
        conversation_history = []
        current_data = user_request

        # Trace do início da conversação
        self.tracer.trace_supervisor(
            self.name,
            "Starting conversation",
            f"Initial request: {user_request}"
        )
        worker_sequence = [
            "Internet Research Specialist",
            "Profile Writer",
            "Email Correspondent"
        ]
        for worker_name in worker_sequence:
            worker = self.workers.get(worker_name)
            if not worker:
                continue

            # Trace da passagem de dados para o worker
            self.tracer.trace_supervisor(
                self.name,
                f"Delegating to {worker_name}",
                current_data
            )

            result = worker.execute_task(current_data, person_name)
            current_data = result

            conversation_history.append({
                "worker": worker_name,
                "result": result
            })

            # Trace do resultado do worker
            self.tracer.trace_supervisor(
                self.name,
                f"Received result from {worker_name}",
                result
            )

        formatted_result = _format_results(conversation_history)
        self.tracer.trace_supervisor(
            self.name,
            "Conversation completed",
            formatted_result
        )
        return formatted_result