from agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ============================================================
    # STEP 1 - SEARCH AGENT
    # ============================================================

    print("\n" + " =" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            (
                "user",
                f"Find recent, reliable and detailed information about: {topic}"
            )
        ]
    })

    # Debug: see the complete search-agent response
    print("\nFULL SEARCH AGENT RESPONSE:")
    print(search_result)

    # Get all messages
    messages = search_result.get("messages", [])

    if not messages:
        raise ValueError("Search agent returned no messages.")

    # ------------------------------------------------------------
    # Get the actual result returned by web_search tool
    # instead of passing the large final AI response.
    # ------------------------------------------------------------

    tool_messages = [
        message
        for message in messages
        if getattr(message, "type", None) == "tool"
    ]

    if not tool_messages:
        raise ValueError("Search agent did not return any tool results.")

    # Take the latest tool result
    search_content = tool_messages[-1].content

    # Limit the amount of data passed to the next agent
    state["search_results"] = search_content[:1000]

    print("\nsearch result:")
    print(state["search_results"])


    # ============================================================
    # STEP 2 - READER AGENT
    # ============================================================

    print("\n" + " =" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"""
Based on the following search results about:

{topic}

Choose the most relevant URL and scrape it for deeper content.

Search Results:

{state["search_results"]}
"""
            )
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\nscraped content:\n")
    print(state["scraped_content"])


    # ============================================================
    # STEP 3 - WRITER
    # ============================================================

    print("\n" + " =" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n"
        f"{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n"
        f"{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n")
    print(state["report"])


    # ============================================================
    # STEP 4 - CRITIC
    # ============================================================

    print("\n" + " =" * 50)
    print("step 4 - critic is reviewing the report")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\ncritic report:\n")
    print(state["feedback"])


    # ============================================================
    # RETURN STATE
    # ============================================================

    return state

