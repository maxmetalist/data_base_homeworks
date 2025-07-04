from typing import List, Optional

import requests

from src.models.employer import Employer
from src.models.vacancy import Vacancy


class HeadHunterAPI:
    """Класс для запросов к API HeadHunter"""

    BASE_URL = "https://api.hh.ru/"

    def __init__(self):
        self.session = requests.Session()

    def get_employer(self, employer_id: str) -> Optional[Employer]:
        """Получаем информацию о работодателе по его ID"""
        url = f"{self.BASE_URL}employers/{employer_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            return Employer(
                employer_id=data["id"],
                name=data["name"],
                url=data["alternate_url"],
                open_vacancies=data["open_vacancies"],
            )
        return None

    def get_vacancies(self, employer_id: str) -> List[Vacancy]:
        """Получаем вакансии работодателя по его ID"""
        url = f"{self.BASE_URL}vacancies"
        params = {"employer_id": employer_id, "per_page": 100, "only_with_salary": True}
        response = self.session.get(url, params=params)
        vacancies = []

        if response.status_code == 200:
            data = response.json()
            for item in data["items"]:
                salary = item.get("salary")
                salary_from = salary.get("from") if salary else None
                salary_to = salary.get("to") if salary else None

                vacancies.append(
                    Vacancy(
                        vacancy_id=item["id"],
                        employer_id=employer_id,
                        title=item["name"],
                        salary_from=salary_from,
                        salary_to=salary_to,
                        url=item["alternate_url"],
                        description=item.get("snippet", {}).get("requirement", ""),
                    )
                )

        return vacancies
