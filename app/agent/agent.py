from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from app.config import GOOGLE_API_KEY
from app.agent.tools_registry import get_all_tools

class CoreAgentExecutor:
    """
    A lightweight, custom tool-execution loop built purely on langchain-core 
    to bypass corrupted langchain.agents installations.
    """
    def __init__(self, llm, tools, system_prompt):
        # Bind the tools directly to the Gemini LLM
        self.llm = llm.bind_tools(tools)
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt

    def invoke(self, inputs):
        messages = inputs.get("messages", [])
        
        # 1. Prepend the system prompt to the conversation history
        full_messages = [("system", self.system_prompt)] + messages
        
        # 2. Ask the LLM what to do (it will either answer or request a tool)
        response = self.llm.invoke(full_messages)
        
        # 3. If no tools are requested, return the final answer!
        if not response.tool_calls:
            return {"output": response.content}
        
        # 4. If tools ARE requested, execute them
        full_messages.append(response) # Save the AI's tool request to history
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            # Run the specific tool (RAG or Web Search)
            if tool_name in self.tools:
                try:
                    print(f"🛠️ Agent is using tool: {tool_name}")
                    tool_result = self.tools[tool_name].invoke(tool_args)
                except Exception as e:
                    tool_result = f"Error executing tool: {e}"
            else:
                tool_result = f"Error: Tool {tool_name} not found."
                
            # Append the result of the tool back to the conversation
            full_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
        
        # 5. Send the tool results back to the LLM to formulate the final user answer
        final_response = self.llm.invoke(full_messages)
        
        # Safely extract the text, whether it is a string or a JSON content block
        final_text = ""
        if isinstance(final_response.content, str):
            final_text = final_response.content
        elif isinstance(final_response.content, list):
            # Loop through the blocks and grab only the text parts
            final_text = "".join(
                block.get("text", "") 
                for block in final_response.content 
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            final_text = str(final_response.content)
            
        return {"output": final_text.strip()}


def get_agent(memories: list = None, conversation_id: str = None):
    """Initializes and returns the AI Tutor agent."""
    
    system_prompt = """
        You are the Multimodal AI Tutor, an intelligent educational assistant.
        
        Your goal is to help students learn from structured and unstructured study materials 
        using clear explanations, step-by-step breakdowns, and context-aware answers.

        Tool Usage Rules:
        1. DOCUMENT SEARCH (RAG): Always use the document search tool FIRST if the user asks about 
           their uploaded study materials, textbook concepts, or chapter specific questions. The document search tool has access to the content of their PDFs and notes and images uploaded like diagrams, so it should be your primary resource for answering questions related to those materials.
        2. WEB SEARCH FALLBACK: If the document search returns no relevant context, or if the user 
           asks a general knowledge question outside their notes, fallback to the web search tool.
           
        Response Style:
        - Keep explanations clear and conceptual.
        - Provide step-by-step breakdowns for complex problems or derivations.
        - If the answer is not in the documents, clearly state that you are using external knowledge.
    """
    
    if memories:
        system_prompt += f"""
            ---
            LONG-TERM MEMORY (What this student has shared in past sessions):
            {chr(10).join(f"- {m}" for m in memories)}
            ---
            Use this context to provide personalized tutoring without asking the student to repeat themselves.
        """
        
    # Initialize the core LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.2, 
        google_api_key=GOOGLE_API_KEY
    )

    # Retrieve all registered tools
    tools = get_all_tools(conversation_id)

    # Return our custom, corruption-proof executor
    return CoreAgentExecutor(llm=llm, tools=tools, system_prompt=system_prompt)