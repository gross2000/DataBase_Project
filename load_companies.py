import requests


def load_vacancies():
    company_id = None
    company_url = None
    company = "Неизвестная компания"
    job_title = "Неизвестная вакансия"
    link_to_vacancy = None
    salary_from = 0  # Значение по умолчанию
    salary_to = 0  # Значение по умолчанию
    description = "Нет описания"
    requirement = "Нет требований"

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
        "ТрансТехСервис"]
    vacancies = []

    for company in companies:
        url = "https://api.hh.ru/vacancies"
        params = {'text': company, 'per_page': 100}
        data = requests.get(url, params=params)

        if data.status_code == 200:
            json_data = data.json()
            for item in json_data['items']:
                company_id = item['id']
                company_url = f"https://hh.ru/employer/{company_id}"
                job_title = item['name']
                link_to_vacancy = item['alternate_url']
                salary = item['salary']
                if salary:
                    salary_from = salary.get('from', 0)
                    salary_to = salary.get('to', 0)
                description = item['snippet']['responsibility']
                requirement = item['snippet']['requirement']

                vacancies.append({
                    "company_id": company_id,
                    "company_url": company_url,
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
