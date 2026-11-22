from unittest.mock import MagicMock
from agent_service import query_llm_agent

def test_query_llm_agent_success(mocker):
    # 1. BIKIN STRUKTUR OBJECT PALSU (Mock Response)
    # Meniru struktur asli: response.choices[0].message.content
    mock_message = MagicMock()
    mock_message.content = "Halo Tobblez, ini adalah respon palsu dari Mock LLM!"
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    # 2. BAJAK METHOD chat.completions.create MILIK GROQ
    # Apapun yang dikirim ke Groq, paksa return mock_response di atas
    mock_create = mocker.patch("groq.resources.chat.completions.Completions.create", return_value=mock_response)
    
    # 3. JALANKAN FUNGSI AGENT ASLI (Tanpa API Key asli & tanpa internet!)
    prompt_input = "Siapa nama gw?"
    result = query_llm_agent(prompt_input)
    
    # 4. ASSERTION (Validasi)
    # A. Pastikan fungsinya terpanggil tepat 1 kali
    assert mock_create.call_count == 1
    
    # B. Pastikan teks yang dihasilkan sama dengan isi mock kita
    assert result == "Halo Tobblez, ini adalah respon palsu dari Mock LLM!"
    assert "Tobblez" in result