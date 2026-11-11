import ollama

response = ollama.chat(
model="qwen2.5-coder:1.5b",
messages=[{"role": "user", "content": "Write a 1-line Python code to print current date and time."}]
)

print("\n--- AI Output ---")
print(response["message"]["content"])
print("-----------------")
