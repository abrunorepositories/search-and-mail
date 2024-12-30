from typing import Optional, List
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from src.tools.tracing import LangfuseTracer


class Worker:
    def __init__(
            self,
            tracer: LangfuseTracer,
            worker_name: str,
            worker_prompt: str,
            supervisor,
            tools: Optional[List[BaseTool]] = None,
            model: Optional[ChatOpenAI] = None,
            max_iterations: Optional[int] = None
    ):
        self.name = worker_name
        self.prompt = worker_prompt
        self.tracer = tracer
        self.supervisor = supervisor
        self.tools = tools or []
        self.model = model or (supervisor.model if supervisor else None)
        self.max_iterations = max_iterations or 3

        if supervisor:
            supervisor.register_worker(self)

    def execute_task(self, input_data: str, person_name: str) -> str:
        """Executa a tarefa específica do worker"""
        formatted_prompt = self.prompt.replace("[person_name]", person_name)
        # Adiciona o input anterior ao prompt
        full_prompt = f"{formatted_prompt}\n\nInput anterior: {input_data}\n\nPor favor, processe este input de acordo com suas instruções."

        # Trace do início da tarefa
        self.tracer.trace_worker(
            self.name,
            "Starting task",
            "Task initiated",
            [tool.name for tool in self.tools] if self.tools else []
        )
        # Se for o Research Specialist, usa as ferramentas
        if self.name == "Internet Research Specialist" and self.tools:
            additional_info = ""
            for tool in self.tools:
                search_result = tool._run(person_name)
                self.tracer.trace_tool_usage(
                    tool.name,
                    person_name,
                    search_result
                )
                additional_info += f"\nResultados da pesquisa:\n{search_result}\n"
            full_prompt += f"\n{additional_info}"
        # Trace da execução principal
        response = self.model.invoke(full_prompt)
        result = response.content if hasattr(response, 'content') else str(response)

       # Trace do resultado final
        self.tracer.trace_worker(
            self.name,
            full_prompt,
            result,
            [tool.name for tool in self.tools] if self.tools else []
        )

        return result