import openai

# Загрузка API-ключа OpenAI
openai.api_key = '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'

# Функция для анализа кода с помощью ChatGPT
def analyze_code(code):
    prompt = f"Проанализируй этот код на безопасность:\n\n{code}\n\n Напиши рекомендации для улучшения безопасности, а также продублируй проблемные строчки и их улучшение:"

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7
    )

    return response.choices[0].text.strip()

# Чтение и анализ файла .py
def parse_and_analyze_file(filename):
    with open(filename, 'r') as file:
        code = file.read()

    analysis_result = analyze_code(code)

    # Запись результатов в output.txt
    with open('output.txt', 'w') as output_file:
        output_file.write(analysis_result)

    print(f"Анализ файла {filename} завершен. Результаты сохранены в output.txt.")


