import json
import requests


def load_vacancies():
    companies = [
        "VK",
        "Яндекс",
        "АО Уфанет",
        "Тинькофф",
        "Тензор",
        "Контур",
        "ASTON",
        "Sber",
        "Альфа-Банк",
        "ТрансТехСервис",
    ]
    vacancies = []

    for company in companies:
        url = "https://api.hh.ru/vacancies"
        params = {'text': company, 'per_page': 100}
        data = requests.get(url, params=params)

        if data.status_code == 200:
            json_data = data.json()
            for item in json_data['items']:
                job_title = item['name']
                link_to_vacancy = item['alternate_url']
                salary = item['salary']
                if salary:
                    salary_from = salary.get('from')
                    salary_to = salary.get('to')
                description = item['snippet']['responsibility']
                requirement = item['snippet']['requirement']

                vacancies.append({
                    "company": company,
                    "job_title": job_title,
                    "link_to_vacancy": link_to_vacancy,
                    "salary_from": salary_from,
                    "salary_to": salary_to,
                    "description": description,
                    "requirement": requirement
                })
        else:
            print(f"Ошибка {data.status_code}")
    return vacancies


if __name__ == "__main__":
    vacancies = load_vacancies()
    for vacancy in vacancies:
        print(vacancy)
        filename = 'vacancy_json.json'
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(vacancies, outfile, ensure_ascii=False, indent=4)