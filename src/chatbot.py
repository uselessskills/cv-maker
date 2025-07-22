import os
import textwrap

import chainlit as cl
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader

from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langchain.schema.runnable.config import RunnableConfig
# from langgraph.types import StateSnapshot

from cv_maker_tool import create_resume_pdf
from models.resume_models import ResumeData

load_dotenv("../dev.env")

model = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_MODEL", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)


@tool
async def generate_resume(resume_data: ResumeData) -> str:
    """
    Generate a PDF resume/CV based on the provided information.

    Args:
        resume_data (ResumeData): An object containing the data required to populate the resume, such as personal details, work experience, education, and skills.        
    
    Returns:
        A string message confirming the resume creation and location of the PDF file.
    """
    try:
        filepath = await create_resume_pdf(resume_data)
        return f"Resume successfully created and saved to: {filepath}"
    except Exception as e:
        return f"Error creating resume: {str(e)}"

@tool
async def download_link(filepath: str) -> str:
    """
    Publishes a link to download the generated resume PDF.
    
    Args:
        filepath (str): The path to the generated PDF file.

    Returns:
        None
    """
    
    filename = os.path.basename(filepath)
    elements = [
        cl.Pdf(name=filename, path=filepath, display="inline", page=1),
        # cl.File(name=filename, path=filepath, display="inline"),
    ]

    await cl.Message(
        content=f"{filename}:",
        elements=elements
    ).send()
    


@cl.on_chat_start
async def start():
    welcome_message = """Welcome to the ATS-Friendly CV Maker! Give me the job position you want to apply for, and I will help you create a tailored resume in PDF format. You can also upload your existing CV or any relevant documents to help me understand your background better."""
    await cl.Message(content=welcome_message).send()
    
    memory = MemorySaver()
    tools = [generate_resume, download_link]
    agent : CompiledStateGraph = create_react_agent(
        model,
        tools=tools,
        checkpointer=memory,
        prompt=textwrap.dedent("""\
            You are a helpful assistant that creates ATS-friendly resumes / CV in PDF format. 
            Tailor the resume to the job position / role provided by the user. 
            
            ### Guidelines:
            *   Use standard ATS-friendly formatting (no graphics, columns, or tables).
            *   Make the experiences and skills in the CV **ultra relevant** for the role.
            *   Keep all the companies the user worked at, don't skip any employment periods.
            *   Include relevant keywords from the job description.
            *   Focus on quantifiable achievements where possible.
            *   Order work experiences in reverse chronological order.
            *   The resulting PDF resume should be 1 page max.
        """),
    )
    cl.user_session.set("agent", agent)


@cl.on_message
async def handle_message(message: cl.Message):
    agent: CompiledStateGraph = cl.user_session.get("agent")

    if message.elements:
        try:
            await file_loader(message)            
        except Exception as e:
            await cl.Message(author="System", content="An error occurred while reading the file. Please try again.").send()
    
    result = await agent.ainvoke(
        {
            "messages": [("human", message.content)],
            "recursion_limit": 5,
        },
        config=RunnableConfig(
            configurable={"thread_id": cl.context.session.id}, 
            callbacks=[cl.AsyncLangchainCallbackHandler()]
        )
    )
    response_content = result["messages"][-1].content
    await cl.Message(response_content).send()


# @cl.on_message
# async def handle_message_streaming(message: cl.Message):
    
#     if message.elements:
#         try:
#             await file_loader(message)            
#         except Exception as e:
#             await cl.Message(
#                 author="System",
#                 content="An error occurred while reading the file. Please try again.",
#             ).send()

#     # memory: MemorySaver = cl.user_session.get("memory")
#     # config = {"configurable": {"thread_id": '123'}}
#     # print('memory.list()', memory.list(config))
#     # state = memory.get(config) or {"messages": []}
    
#     agent: CompiledStateGraph = cl.user_session.get("agent")

#     answer = cl.Message(content="")
#     await answer.send()

#     # cb = cl.AsyncLangchainCallbackHandler() # cb = cl.LangchainCallbackHandler()
#     # config: RunnableConfig = {"configurable": {"thread_id": cl.context.session.id}}
#     config: RunnableConfig = {"configurable": {"thread_id": message.thread_id}}
#     for msg, metadata in agent.stream({"messages": [HumanMessage(content=message.content)]}, stream_mode="messages", config=config):
#         if isinstance(msg, AIMessageChunk):
#             answer.content += msg.content  # type: ignore
#             await answer.update()
            

@cl.step(type="tool")
async def file_loader(message: cl.Message):
    """
    This function processes the files uploaded by the user for further use by the chat application.
    """

    documents = []
    for element in message.elements:
        print("Loading document:", element.path, element.name)
        if element.name.endswith(".pdf"):
            loader = PyMuPDFLoader(element.path)
        else:
            loader = TextLoader(element.path)
        docs = await cl.make_async(loader.load)()
        print("Loaded document:", element.path, docs)

        for doc in docs:
            doc.metadata["thread_id"] = cl.context.session.id  # message.thread_id
            doc.metadata["title"] = element.name
            documents.append(doc)

    # Insert the document's content into the chat history as a "context" field
    agent: CompiledStateGraph = cl.user_session.get("agent")
    for single_doc in documents:
        context_message = ("user", f"context: page_content={single_doc.page_content}, title={single_doc.metadata.get('title', None)}")
        # result = agent.invoke(
        #         {
        #             "messages": [
        #                 # ("system", f"Adding document context: {doc.metadata['title']}"), 
        #                 context_message,
        #             ],
        #             "recursion_limit": 1,  # Minimum value to prevent actual reasoning
        #         },
        #         config={"configurable": {"thread_id": doc.metadata["thread_id"]}}
        #     )
        # response_content = result["messages"][-1].content
        # print("Responsed on Context added:", response_content)
        
        # state: StateSnapshot = agent.get_state(config={"configurable": {"thread_id": doc.metadata["thread_id"]}})  
        # print("STATE 1:", len(state.values.get("messages", [])), "\n".join(map(str, state.values.get("messages", []))), sep="\n")
        agent.update_state(
            config={"configurable": {"thread_id": doc.metadata["thread_id"]}},
            values={"messages": [context_message]}
        )
        # state: StateSnapshot = agent.get_state(config={"configurable": {"thread_id": doc.metadata["thread_id"]}})  
        # print("STATE 2:", len(state.values.get("messages", [])), "\n".join(map(str, state.values.get("messages", []))), sep="\n")
    cl.user_session.set("agent", agent)

    await cl.Message(author="System", content="Done reading and memorizing files.").send()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Expected format: USERS=username1:password1,username2:password2
    users_env = os.getenv("USERS")
    allowed_users = dict(
        userpass.split(":", 1) for userpass in users_env.split(",") if ":" in userpass
    )
    if username in allowed_users and password == allowed_users[username]:
        return cl.User(identifier=username, metadata={"role": "admin", "provider": "credentials"})
    else:
        return None
    

# @cl.set_starters
# async def set_starters():
#     return [
#         cl.Starter(
#             label="Create a resume",
#             message=textwrap.dedent("""\
#                 Create an ATS-friendly resume tailored to the following job position: [Insert Job Title].
#                 Requirements:
#                 *   Use standard ATS-friendly formatting (no graphics, columns, or tables).
#                 *   Include relevant keywords from the job description.
#                 *   Use clear section headings (Work Experience, Education, Skills).
#                 *   Focus on quantifiable achievements where possible.
#                 *   Keep the resume concise (1 page max).
#             """),
#             icon="/public/write.svg",
#             )
#         ]

# Run Chainlit
# chainlit run your_script.py -w --port 8000
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)