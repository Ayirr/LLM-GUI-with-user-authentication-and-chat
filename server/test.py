from decouple import config
import openai

openai.api_key = config("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello from test script"}]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("OpenAI error:", e)
