from typing import Dict, List

import psycopg2

from config.config import Config


class DBManager:
    """Класс для работы с БД"""

    def __init__(self):
        self.conn = psycopg2.connect(Config.get_db_url())

    def __del__(self):
        self.conn.close()

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """
        Получаем список всех компаний и количество вакансий у каждой компании (просто название и количество),
        группируем по названию в порядке убывания количества вакансий
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
                ORDER BY vacancies_count DESC
            """
            )
            result = []
            for row in cursor.fetchall():
                result.append({"company": row[0], "vacancies_count": row[1]})
            return result

    def get_all_vacancies(self) -> List[Dict]:
        """
        Тут получаем список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                ORDER BY e.name, COALESCE(v.salary_from, v.salary_to, 0) DESC
            """
            )
            result = []
            for row in cursor.fetchall():
                result.append(
                    {"company": row[0], "title": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                )
            return result

    def get_avg_salary(self) -> float:
        """
        Тут вычисляем среднюю зарплату по всем найденным вакансиям
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG((COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """
            )
            return cursor.fetchone()[0] or 0

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """
        Тут получаем список всех вакансий, у которых зарплата выше средней по всем вакансиям (метод
        get_avg_salary)
        """
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE (COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2 > %s
                ORDER BY (COALESCE(v.salary_from, v.salary_to) + COALESCE(v.salary_to, v.salary_from)) / 2 DESC
            """,
                (avg_salary,),
            )
            result = []
            for row in cursor.fetchall():
                result.append(
                    {"company": row[0], "title": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                )
            return result

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """
        Здесь получаем список вакансий по ключевому слову от юзера (запрос слова в модуле main)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE LOWER(v.title) LIKE %s
                ORDER BY e.name, COALESCE(v.salary_from, v.salary_to, 0) DESC
            """,
                (f"%{keyword.lower()}%",),
            )
            result = []
            for row in cursor.fetchall():
                result.append(
                    {"company": row[0], "title": row[1], "salary_from": row[2], "salary_to": row[3], "url": row[4]}
                )
            return result

    def insert_employer(self, employer) -> None:
        """Добавляем работодателя в БД"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employers (employer_id, name, url, open_vacancies)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
            """,
                (employer.employer_id, employer.name, employer.url, employer.open_vacancies),
            )
            self.conn.commit()

    def insert_vacancy(self, vacancy) -> None:
        """Добавляем вакансию в БД"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vacancies (vacancy_id, employer_id, title, salary_from, salary_to, url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING
            """,
                (
                    vacancy.vacancy_id,
                    vacancy.employer_id,
                    vacancy.title,
                    vacancy.salary_from,
                    vacancy.salary_to,
                    vacancy.url,
                    vacancy.description,
                ),
            )
            self.conn.commit()
