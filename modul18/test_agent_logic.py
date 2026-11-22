from agent_logic import parse_agent_response

def test_parse_action_success():
    llm_output = "Thought: Gw butuh cek database.\nAction: query_db[SELECT * FROM users]"
    result = parse_agent_response(llm_output)
    
    # Validasi ekspektasi
    assert result["type"] == "action"
    assert result["tool"] == "query_db"
    assert result["input"] == "SELECT * FROM users"

def test_parse_final_answer_success():
    llm_output = "Thought: Udah dapet infonya.\nFinal Answer: Ibukota Prancis adalah Paris."
    result = parse_agent_response(llm_output)
    
    assert result["type"] == "final_answer"
    assert result["content"] == "Ibukota Prancis adalah Paris."

def test_parse_invalid_format():
    llm_output = "Halo, gw bingung mau ngapain nih."
    result = parse_agent_response(llm_output)
    
    assert result["type"] == "error"