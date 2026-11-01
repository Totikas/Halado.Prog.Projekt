import ollama

with open('webserver_login.log', 'r', encoding='utf-8') as f:
    fajl_tartalma = f.read()

with open('ai_kezdopromt.txt', 'r', encoding='utf-8') as k:
    ai_prompt = k.read()

teljes_prompt = f"{ai_prompt}{fajl_tartalma}"
response = ollama.chat(
    model="llama3.2:3b", messages=[{"role": "user","content": teljes_prompt}]
            )
print(response["message"]["content"])