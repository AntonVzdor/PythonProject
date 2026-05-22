"""
Библиотека для демонстрации расширенных возможностей SQL в рамках курса по SQL.
Автор: Никита Шультайс
Сайт: https://shultais.education/
Лицензия: BSD
"""

import MySQLdb
import time
from texttable import Texttable
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import TerminalFormatter


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ExecuteError(Exception):
    pass


class MySQL:
    """
    Основной класс для работы с MySQL.
    """

    def __init__(self, echo=True, show_errors=False, auto_commit=False):
        """
        :param echo: печатает SQL запросы. 
        :param show_errors: печатает ошибки.
        """
        
        self.echo = echo
        self.show_errors = show_errors
        self.auto_commit = auto_commit

        self.db = MySQLdb.connect(host="127.0.0.1", user="", passwd="", db="", charset='utf8')
        self.cursor = self.db.cursor()

    def execute(self, sql):
        """
        Выполняет SQL запрос.
        """
        execute_error = False

        try:
            self.cursor.execute(sql)
        except Exception as e:
            execute_error = True
            if self.show_errors:
                print(e)

        if self.echo:
            self.print_sql(self.cursor._last_executed.decode(), error=execute_error)

        if execute_error:
            raise ExecuteError

    def get_value(self, sql):
        self.cursor.execute(sql)
        if self.echo:
            self.print_sql(self.cursor._last_executed.decode())
        return self.cursor.fetchone()[0]

    def print_table(self, sql):
        self.cursor.execute(sql)
        if self.echo:
            self.print_sql(self.cursor._last_executed.decode())

        table = Texttable()
        table.add_rows(self.cursor.fetchall())
        print(table.draw())

    def print_sql(self, sql, error=False):
        """
        Выводит SQL запрос.
        """
        result = highlight(sql, SqlLexer(), TerminalFormatter())
        if error:
            result = "\033[91mERROR:\033[0m {}".format(result)
        print(result, end="")

    def call(self, name, args):
        """
        Вызов хранимой процедуры.
        """
        execute_error = False
        self.cursor.callproc(name, args)

        try:
            self.cursor.callproc(name, args)
        except Exception as e:
            execute_error = True
            if self.show_errors:
                print(e)

        if self.echo:
            self.print_sql(self.cursor._last_executed.decode(), error=execute_error)

    def __del__(self):
        self.close()

    def close(self):
        if self.auto_commit:
            self.db.commit()
        self.cursor.close()

    def sleep(self, seconds):
        if self.echo:
            print("\033[92msleep {} second{}\033[0m".format(seconds, "s" if seconds > 1 else ""))
        time.sleep(seconds)
