import rclpy #damit kann meine Hauptdatei ros2 initialisieren und einen Node starten. rclpy ist die ROS2 Python API
from langchain_google_genai import ChatGoogleGenerativeAI #LangChain-Schnittstelle zu Gemini.

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

import ros_tools
import os
import getpass

from rag import RAG

from langchain_core.messages import HumanMessage, AIMessage

rclpy.init()
#initialisiert ROS2 für den Python Programm.

#ros_tools.ros_object = ros_tools.ROSGoalPublisher()
publisher = ros_tools.ROSGoalPublisher()
ros_tools.ros_object = publisher
#damit ist jetzt ROS-Node bereit. -> Ros-Node erstellt

# API-Key abfragen
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass(
        "Enter API key for Google Gemini: "
    )

rag = RAG("Angabe.tex")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.2,
    top_p=0.8 #begrenzt zusätzlich, aus welchem Wahrscheinlichkeitsbereich das Modell Tokens auswählt.
)

# Systemprompt
system_prompt = (
    "Du steuerst einen mobilen Roboter per ROS2.\n"
    "Verwende nur die Informationen aus der Wissensbasis.\n"
    "Wenn ein Ziel eindeutig bestimmt werden kann und x, y und theta bekannt sind, "
    "verwende das Tool ROS_send_goal.\n"
    "Wenn das Ziel nicht eindeutig ist, frage den Benutzer nach."
)


# Prompt für den Agenten
full_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])


tools = [ros_tools.ROS_send_goal]
#tools, die der Agent verwenden darf

# Agent erstellen
agent = create_tool_calling_agent(llm,tools,full_prompt)


# Agent ausführen können
LLM_agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

chat_history = []

def ask_agent(user_input):

    relevant_chunks = rag.search(user_input)

    context = "\n".join(relevant_chunks)

    full_input = f"""User-Anfrage: {user_input} Informationen aus der Wissensbasis:{context}"""

    result = LLM_agent_executor.invoke({
        "input": full_input,
        "chat_history": chat_history
    })

    output = result["output"]

    # Falls Gemini strukturierten Inhalt zurückgibt
    if isinstance(output, list):
        response_text = output[0].get("text", str(output))
    else:
        response_text = str(output)

    # Chat-History aktualisieren
    chat_history.append(
        HumanMessage(content=user_input)
    )

    chat_history.append(
        AIMessage(content=response_text)
    )

    return response_text


if __name__ == "__main__":

    while True:
        user_input = input("Du: ")

        if user_input.lower() == "exit":
            break

        response = ask_agent(user_input)

        print("Bot:", response)