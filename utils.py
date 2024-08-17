import json
from typing import Any
import requests
import psycopg2
from load_companies import load_vacancies

vacancies = load_vacancies()
for vacancy in vacancies:
    print(vacancy)
    filename = 'vacancies.json'
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(vacancies, outfile, ensure_ascii=False, indent=4)


def get_companies():
    """
    Получает имя компаний и их ID из файла vacancies.json,
    :return: список словарей с информацией о компаниях
    """
    with open('vacancies.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        companies_info = [{"company_id": item.get("company_id"),
                           "company_url": item.get("company_url"),
                           "company": item.get("company")} for item in data]
    return companies_info


def get_vacancies():
    """
    Получает из файла vacancies.json,
    :return: список словарей с информацией
    о вакансиях для каждой компании
    """
    with open('vacancies.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        vacancies_info = [{"job_title": item.get("job_title"),
                           "link_to_vacancy": item.get("link_to_vacancy"),
                           "salary_from": item.get("salary_from",0),
                           "salary_to": item.get("salary_to",0),
                           "description": item.get("description"),
                           "requirement": item.get("requirement")} for item in data]
    return vacancies_info


def create_db(database_name: str, params: dict) -> None:
    """
    Создание базы данных для сохранения данных о компаниях и вакансиях
    """
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(f"DROP DATABASE {database_name}")
    except Exception as e:
        print(f"Ошибка создания базы данных: {e}")
    finally:
        cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE companies (
            company_id integer PRIMARY KEY,
            company_name varchar(50) NOT NULL,
            company_url text
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
            vacancy_id text PRIMARY KEY,
            company_id integer REFERENCES companies(company_id),
            vacancy_name varchar(100) NOT NULL,
            requirement varchar(255),
            salary_min integer,
            salary_max integer,
            currency varchar(50),
            vacancy_url text
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_db(companies_data: list[dict[str, Any]],
                    vacancies_data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о компаниях и вакансиях в базу данных."""
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for company in companies_data:
            company_id = company['company_id']
            company_name = company['company_name']
            company_url = company['company_url']
            cur.execute("""
                INSERT INTO companies (company_id, company_name, company_url)
                VALUES (%s, %s, %s)
            """, (company_id, company_name, company_url))

        for vacancy in vacancies_data:
            vacancy_id = vacancy['id']
            company_id = vacancy['employer']['id']
            vacancy_name = vacancy['name']
            requirement = vacancy['snippet'].get('requirement', None)
            salary = vacancy['salary']
            salary_min = salary.get('from') if salary else None
            salary_max = salary.get('to') if salary else None
            currency = salary.get('currency', None) if salary else None
            vacancy_url = vacancy['alternate_url']
            cur.execute("""
                INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, requirement, salary_min, salary_max,
                currency, vacancy_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (vacancy_id, company_id, vacancy_name, requirement, salary_min, salary_max, currency, vacancy_url))

    conn.commit()
    conn.close()
