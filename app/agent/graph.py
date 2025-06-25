# In your chat_agent function
from langgraph.graph import StateGraph, END
from app.tools.write_query import generate_sql, run_sql, generate_answer
from .types import State

async def chat_agent(question: str) -> str:

    try:
        builder = StateGraph(State)
    except Exception as e:
        print(f"Error initializing StateGraph: {e}")

    # Add nodes (tools)
    builder.add_node("generate_sql", generate_sql)
    builder.add_node("run_sql", run_sql)
    builder.add_node("generate_answer", generate_answer)

    # Define flow: question → SQL → run → answer
    builder.set_entry_point("generate_sql")
    builder.add_edge("generate_sql", "run_sql")
    builder.add_edge("run_sql", "generate_answer")
    builder.add_edge("generate_answer", END)

    graph = builder.compile()

    try:
        result = await graph.ainvoke({"question": question})
        return result["answer"]
    except Exception as e:
        import traceback
        print(f"\nFATAL ERROR during graph.invoke: {e}")
        traceback.print_exc() 
        raise 