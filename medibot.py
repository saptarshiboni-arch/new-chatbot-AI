from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_response(user_input):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192"
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print("Error:", e)
        return "Error generating response"