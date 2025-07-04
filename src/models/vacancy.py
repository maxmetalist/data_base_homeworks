from dataclasses import dataclass


@dataclass
class Vacancy:
    """Класс для представления вакансии"""

    vacancy_id: str
    employer_id: str
    title: str
    salary_from: int | None
    salary_to: int | None
    url: str
    description: str

    @property
    def avg_salary(self) -> float:
        """Средняя зарплата вакансии"""
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        elif self.salary_from:
            return self.salary_from
        elif self.salary_to:
            return self.salary_to
        return 0
