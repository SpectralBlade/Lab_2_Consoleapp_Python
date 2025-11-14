from Lab_2_Consoleapp_Python.src.ruletka_shell import RuletkaShell

def main() -> None:
    """
    Стартовая точка для запуска консольной оболочки.
    :return: Данная функция ничего не возвращает.
    """
    shell = RuletkaShell().create()
    shell.run()

if __name__ == "__main__":
    main()