#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создать таблицу с информацией о людях.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS people (
        people_id INTEGER PRIMARY KEY AUTOINCREMENT,
        people_name TEXT NOT NULL,
        phone_number INTEGER NOT NULL
        )
        """
    )
    # Создать таблицу с информацией о дате рождения.
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS dates (        
        date_id INTEGER PRIMARY KEY AUTOINCREMENT,
        birth_year DATE NOT NULL,
        people_id INTEGER NOT NULL,
        phone_number INTEGER NOT NULL,
        FOREIGN KEY(people_id) REFERENCES people(people_id)
        )
        """

    )
    conn.close()


def display_people(people: t.List[t.Dict[str, t.Any]]) -> None:
    if people:
        # Заголовок таблицы.
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 15
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^15} |'.format(
                "№",
                "Ф.И.О.",
                "Дата рождения",
                "Номер"
            )
        )
        print(line)

        # Вывести данные о всех студентах.
        for idx, human in enumerate(people, 1):
            print(
                f"| {idx:>4} |"
                f' {human.get("name", ""):<30} |'
                f' {human.get("birth", 0):<20} |'
                f' {human.get("phone"):<12}    |'
            )
            print(line)

    else:
        print("Список пуст.")


def add_person(
        database_path: Path,
        name: str,
        phone: int,
        birth: str
) -> None:
    """
    Добавить человека в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT people_id FROM people WHERE people_name = ?
        """,
        (name,)
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO people (people_name, phone_number) VALUES (?, ?)
            """,
            (name, phone)
        )
        people_id = cursor.lastrowid

    else:
        people_id = row[0]
    # Добавить информацию о новом человеке.
    cursor.execute(
        """
        INSERT INTO dates (phone_number, people_id, birth_year)
        VALUES (?, ?, ?)
        """,
        (phone, people_id, birth)
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.phone_number, people.people_name, dates.birth_year
        FROM dates
        INNER JOIN people ON people.people_id = dates.people_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[1],
            "phone": row[0],
            "birth": row[2],
        }
        for row in rows
    ]


def find_nomer(
        database_path: Path, num: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Вывод на экран информации о человеке, чей номер был введен
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.phone_number, people.people_name, dates.birth_year
        FROM dates
        INNER JOIN people ON people.people_id = dates.people_id
        WHERE people.phone_number LIKE '%' || ? || '%'
        """,
        (num,)
    )
    rows = cursor.fetchall()
    conn.close()
    if len(rows) == 0:
        return []

    return [
        {
            "name": row[1],
            "phone": row[0],
            "birth": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.cwd() / "Data_ind.db"),
        help="The database file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("people")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления людей.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new person"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The person's name"
    )
    add.add_argument(
        "-p",
        "--phone",
        type=int,
        action="store",
        help="The person's zodiac_sign"
    )
    add.add_argument(
        "-b",
        "--birth",
        action="store",
        required=True,
        help="The person's birth"
    )

    # Создать субпарсер для отображения всех людей.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all people"
    )

    # Создать субпарсер для выбора знака зодиака.
    find = subparsers.add_parser(
        "find",
        parents=[file_parser],
        help="Select person"
    )

    find.add_argument(
        "-s",
        "--phone",
        action="store",
        required=True,
        help="The required zodiac_sign"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    # Добавить работника.
    if args.command == "add":
        add_person(db_path, args.name, args.phone, args.birth)

    # Отобразить всех работников.
    elif args.command == "display":
        display_people(select_all(db_path))

    # Выбрать требуемых работников.
    elif args.command == "find":
        display_people(find_nomer(db_path, args.phone))
        pass


if __name__ == '__main__':
    main()
