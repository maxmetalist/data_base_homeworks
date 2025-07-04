from src.api.hh_api import HeadHunterAPI
from src.database.db_creator import DBCreator
from src.database.db_manager import DBManager


def main():
    """Основная функция с менюшкой для юзера1"""
    # Создаем базу данных и таблицы
    DBCreator.create_database()
    DBCreator.create_tables()

    # ID компаний для парсинга (примеры, всего 10 штук)
    company_ids = [
        '1740',  # Яндекс
        '3529',  # Сбер
        '78638',  # Тинькофф
        '2748',  # Ростелеком
        '3776',  # МТС
        '41862',  # ВКонтакте
        '87021',  # Wildberries
        '2180',  # Ozon
        '4934',  # Билайн
        '1122462'  # СберТех
    ]

    # Получаем данные с hh.ru и сохраняем в БД
    hh_api = HeadHunterAPI()
    db_manager = DBManager()

    for company_id in company_ids:
        employer = hh_api.get_employer(company_id)
        if employer:
            db_manager.insert_employer(employer)
            vacancies = hh_api.get_vacancies(company_id)
            for vacancy in vacancies:
                db_manager.insert_vacancy(vacancy)
            print(f"Добавлен работодатель {employer.name} с {len(vacancies)} вакансиями")

    # Взаимодействие с пользователем
    while True:
        print("\nВыбирай действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Список всех вакансий")
        print("3. Средняя зарплата по вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход из этого болота")

        choice = input("Твой выбор: ")

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['company']}: {company['vacancies_count']} вакансий")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            for vacancy in vacancies:
                salary = ""
                if vacancy['salary_from'] and vacancy['salary_to']:
                    salary = f"от {vacancy['salary_from']} до {vacancy['salary_to']}"
                elif vacancy['salary_from']:
                    salary = f"от {vacancy['salary_from']}"
                elif vacancy['salary_to']:
                    salary = f"до {vacancy['salary_to']}"
                else:
                    salary = "не указана"

                print(f"{vacancy['company']}: {vacancy['title']} - {salary}")
                print(f"Ссылка: {vacancy['url']}\n")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата по вакансиям: {avg_salary:.2f} руб.")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            print(f"Найдено {len(vacancies)} вакансий с зарплатой выше средней:")
            for vacancy in vacancies:
                salary = ""
                if vacancy['salary_from'] and vacancy['salary_to']:
                    salary = f"от {vacancy['salary_from']} до {vacancy['salary_to']}"
                elif vacancy['salary_from']:
                    salary = f"от {vacancy['salary_from']}"
                elif vacancy['salary_to']:
                    salary = f"до {vacancy['salary_to']}"

                print(f"{vacancy['company']}: {vacancy['title']} - {salary}")
                print(f"Ссылка: {vacancy['url']}\n")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print(f"Найдено {len(vacancies)} вакансий по запросу '{keyword}':")
            for vacancy in vacancies:
                salary = ""
                if vacancy['salary_from'] and vacancy['salary_to']:
                    salary = f"от {vacancy['salary_from']} до {vacancy['salary_to']}"
                elif vacancy['salary_from']:
                    salary = f"от {vacancy['salary_from']}"
                elif vacancy['salary_to']:
                    salary = f"до {vacancy['salary_to']}"
                else:
                    salary = "не указана"

                print(f"{vacancy['company']}: {vacancy['title']} - {salary}")
                print(f"Ссылка: {vacancy['url']}\n")

        elif choice == "0":
            break

        else:
            print("Неверный ввод. Попробуйте еще раз.")


if __name__ == "__main__":
    main()
