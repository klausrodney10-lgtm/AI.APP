else:
    load_dotenv()
    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=os.getenv("AI_TOKEN"),
    )
    r = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    st.write(r.choices[0].message.content)