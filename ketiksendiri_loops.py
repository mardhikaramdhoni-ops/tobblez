#ketik manual list LLM

daftar_llm = ['gpt-4o', 'claude-3-5', 'llama-3', 'gemini-pro']


for model in daftar_llm:
    if model == 'gpt-4o':
        print (model, '- INI MODEL UTAMA GW')
    else:
        print (model, '- INI MODEL CADANGAN')