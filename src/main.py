from dotenv import load_dotenv
load_dotenv()
import os
from langchain_openai import ChatOpenAI
from agents.supervisor import Supervisor
from agents.worker import Worker
from src.tools.tracing import LangfuseTracer
from tools.serper import SerperSearchTool

def run_search(person_name: str):

    chat_model = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.9,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
#
    serper = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))

    tracer = LangfuseTracer(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY")
    )

    supervisor = Supervisor(
        model=chat_model,
        tracer=tracer,
        supervisor_name="Supervisor",
        supervisor_prompt="""You are a supervisor tasked with managing a conversation between the following workers: {team_members}.
                                Given the following user request, respond with the worker to act next.
                                Each worker will perform a task and respond with their results and status.
                                When finished, respond with FINISH.
                                Select strategically to minimize the number of steps taken.
                                
                                Always start with the Internet Research Specialist, then pass the information to the Profile Writer and lastly, pass the information from the Profile Writer to the Email Correspondent."""
        )

    # Initialize Workers
    research_specialist = Worker(
        worker_name="Internet Research Specialist",
        tracer=tracer,
        worker_prompt="""As an Internet Research Specialist, your task is to conduct a thorough search of the internet to gather comprehensive information about a specified individual.
        Using the SerperAPI, explore various platforms such as GitHub, X (formerly Twitter), Wikipedia, and other relevant sites.
        Your objective is to collect detailed insights into the individual's career history, recent activities, and ongoing projects.
        Focus on obtaining accurate and current information about [person_name], including their past employment, current endeavors, and any significant projects they are currently involved in. Ensure that all data is sourced from credible and reliable platforms.
        Compile a detailed report summarizing your findings, emphasizing key achievements, recent activities, and ongoing projects. This report will be forwarded to the Profile Writer for further processing.
        Improvements Made:
            Added placeholders like [person_name] for clarity and to specify where dynamic input should be inserted
            Streamlined language for clarity and conciseness.
            Emphasized the importance of credible sources.
            Pass this information to the Profile Writer.""",
        supervisor=supervisor,
        tools=[serper]
    )

    profile_writer = Worker(
        worker_name="Profile Writer",
        tracer=tracer,
        worker_prompt="""As a Profile Writer, your role is to develop a comprehensive and engaging description of an individual using the information provided by the Internet Research Specialist.
                        Your writing should encapsulate the essence of the person's professional journey, highlighting their career trajectory, recent accomplishments, and ongoing projects.
                        Utilize the detailed report from the Internet Research Specialist to craft a complete profile of [person_name].
                        Ensure the description is well-structured, informative, and engaging, providing a thorough understanding of the individual's professional life.
                        The final output should be a polished and cohesive profile suitable for various uses. This profile will then be passed to the Email Correspondent.
                        Improvements Made:
                            Added placeholders like [person_name] for clarity.
                            Enhanced language for better readability and engagement.
                            Clarified the purpose and flow of information.
                            Pass this information to the Email Correspondent""",
        supervisor=supervisor
    )

    email_correspondent = Worker(
        worker_name="Email Correspondent",
        tracer=tracer,
        worker_prompt="""As an Email Correspondent, your responsibility is to compose personalized and engaging emails that resonate with the recipient.
        Using the profile provided by the Profile Writer, your task is to reach out to [person_name] with a thoughtful and professional email.
        Begin the email with a sincere compliment about [person_name]'s recent accomplishments or projects, as highlighted in the profile. 
        Follow this with a courteous inquiry about any potential job openings or collaboration opportunities they might have.
        Ensure the email is respectful, concise, and tailored to the individual's recent achievements.
        The final output should be a well-crafted email that opens the door for potential professional engagement, maintaining a tone that is both respectful and enthusiastic.
        Improvements Made:
            Added placeholders like [person_name] for clarity.
            Refined language for precision and effectiveness.
            Emphasized the importance of personalization and professionalism.""",
        supervisor=supervisor
    )

    final_result = supervisor.manage_conversation(person_name)
    return final_result

if __name__ == "__main__":
    person_name = input("Enter the name of the person to research: ")
    print("\nFinal Result:", run_search(person_name))
