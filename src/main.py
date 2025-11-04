from Lab_2_Consoleapp_Python.src.ruletka_shell import RuletkaShell

def main() -> None:
    """Стартовая функция для запуска оболочки. Создает класс RuletkaShell
    и запускает его через цикличную функцию run. Ничего не возвращает"""
    shell = RuletkaShell()
    shell.run()

if __name__ == "__main__":
    main()