from dataclasses import dataclass


@dataclass
class Employer:
    """Класс для представления работодателя"""

    employer_id: str
    name: str
    url: str
    open_vacancies: int
