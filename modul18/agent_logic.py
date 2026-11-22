import re

def parse_agent_response(response_text: str) -> dict:
    """
    Membedakan apakah LLM mau manggil Tool atau memberikan Final Answer.
    """
    if "Action:" in response_text:
        # Cari nama tool di dalam format Action: tool_name[input]
        match = re.search(r"Action:\s*(\w+)\[(.*)\]", response_text)
        if match:
            tool_name = match.group(1)
            tool_input = match.group(2)
            return {"type": "action", "tool": tool_name, "input": tool_input}
        return {"type": "error", "message": "Format action salah"}
    
    elif "Final Answer:" in response_text:
        answer = response_text.split("Final Answer:")[1].strip()
        return {"type": "final_answer", "content": answer}
    
    return {"type": "error", "message": "Output tidak dikenali"}