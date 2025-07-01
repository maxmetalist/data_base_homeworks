import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config.config import Config


class DBCreator:
    """Класс для создания БД и таблиц"""

    @staticmethod
    def create_database() :
        """Статик-метод для создания БД"""
        conn = psycopg2.connect(
            dbname="postgres",
            user=Config.DB_USER,
            password=Config.DB_PASSWORD.encode("utf-8").decode("unicode_escape"),
            host=Config.DB_HOST,
            port=Config.DB_PORT,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        try:
            cursor.execute(sql.SQL(f"CREATE DATABASE {Config.DB_NAME}"))
            print(f"База данных {Config.DB_NAME} успешно создана")
        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create_tables():
        """Статик-метод для создания таблиц"""
        conn = psycopg2.connect(Config.get_db_url())
        cursor = conn.cursor()

        try:
            # Таблица employers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    url VARCHAR(100),
                    open_vacancies INTEGER
                )
            """
            )

            # Таблица vacancies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id VARCHAR(20) PRIMARY KEY,
                    employer_id VARCHAR(20) REFERENCES employers(employer_id),
                    title VARCHAR(100) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    url VARCHAR(100),
                    description TEXT
                )
            """
            )

            conn.commit()
            print("Таблицы успешно созданы")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
