from openai import OpenAI
 
# pip install openai 
# if you saved the key under a different environment variable name, you can do something like:
client = OpenAI(
  api_key="YOUR_OPENAI_KEY",
)

completion = client.chat.completions.create(
  model="gpt-4-turbo",
  messages=[
    {"role": "system", "content": "You are Jarvis, a highly advanced and concise virtual assistant. Current context: Today is November 19, 2025. The current President of the United States is Donald Trump (47th President).Keep your answers short, witty, and direct."},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)