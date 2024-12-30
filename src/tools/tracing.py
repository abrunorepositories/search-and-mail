from langfuse import Langfuse

class LangfuseTracer:
    def __init__(self, public_key: str, secret_key: str):
        self.langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key
        )
        self.current_trace = None

    def trace_supervisor(self, supervisor_name: str, prompt: str, response: str):
        """
        Rastreia ações do supervisor com mais detalhes
        """
        if not self.current_trace:
            self.current_trace = self.langfuse.trace(name="supervisor_execution")

        span = self.current_trace.span(
            name=f"{supervisor_name}_action",
            input={
                "prompt": prompt,
                "role": "supervisor"
            },
            output={
                "response": response,
                "status": "completed"
            },
            metadata={
                "supervisor_name": supervisor_name,
                "type": "supervisor_action"
            }
        )
        return span

    def trace_worker(self, worker_name: str, input_data: str, output_data: str, tools_used: list):
        """
        Rastreia ações do worker com mais detalhes
        """
        if not self.current_trace:
            self.current_trace = self.langfuse.trace(name=f"{worker_name}_execution")

        span = self.current_trace.span(
            name=f"{worker_name}_task",
            input={
                "data": input_data,
                "role": "worker",
                "tools": tools_used
            },
            output={
                "result": output_data,
                "status": "completed"
            },
            metadata={
                "worker_name": worker_name,
                "tools_used": tools_used,
                "type": "worker_action"
            }
        )
        return span

    def trace_tool_usage(self, tool_name: str, input_query: str, output_result: str):
        """
        Rastreia uso específico de ferramentas
        """
        if not self.current_trace:
            self.current_trace = self.langfuse.trace(name=f"{tool_name}_usage")

        span = self.current_trace.span(
            name=f"{tool_name}_execution",
            input={
                "query": input_query,
                "role": "tool"
            },
            output={
                "result": output_result,
                "status": "completed"
            },
            metadata={
                "tool_name": tool_name,
                "type": "tool_usage"
            }
        )
        return span
