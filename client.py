

# 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 


from groq import Groq

# Corrected API key (remove leading space!)
client = Groq(api_key="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")

# Send chat request
response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": "Tell me about Brainware University"
        }
    ]
)

# Print the response
print(response.choices[0].message.content)
