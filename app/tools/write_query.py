# app/tools/write_query.py

from app.config.db import get_conn, get_table_info
from app.config.gemini import llm
from app.agent.prompts import query_prompt_template
from app.agent.types import State, QueryOutput

async def generate_sql(state: State) -> State:
    try:
        # Load table schema
        table_info = await get_table_info()

        # Format the prompt
        prompt = query_prompt_template.format_messages(
            dialect="PostgreSQL",
            top_k=10,
            table_info=table_info,
            input=state["question"]
        )

        # Generate SQL query with Gemini
        structured_llm = llm.with_structured_output(QueryOutput)
        response = structured_llm.invoke(prompt) 
        query = response['query'].strip()

        return {**state, "query": query}

    except Exception as e:
        print(f"ERROR in generate_sql: {str(e)}") 
        # Consider logging the full traceback here for better debugging
        import traceback
        traceback.print_exc()
        return {**state, "query": f"-- Error generating SQL: {str(e)}"}

async def run_sql(state: State) -> State:
    pool = await get_conn()
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(state["query"])
            result = [dict(row) for row in rows]
            return {**state, "result": str(result)}
    except Exception as e:
        return {**state, "result": f"❌ Error: {str(e)}"}

async def generate_answer(state: State) -> State:
    if "result" not in state or not state["result"]:
        return {**state, "answer": "No result found to answer the question."}

    if "query" in state and state["query"].startswith("-- Error"):
        return {**state, "answer": f"❌ SQL Error: {state['query']}"}

    # Prompt template
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question clearly and concisely.\n\n"
        f"Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['result']}\n\n"
        "Answer:"
    )

    try:
        response = await llm.ainvoke(prompt)
        answer = response.content.strip()
        return {**state, "answer": answer}
    except Exception as e:
        return {**state, "answer": f"❌ Failed to generate answer: {str(e)}"}