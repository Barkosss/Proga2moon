import telebot

def handler_common_command(command: str, args: list[str]):
    print("Command: " + command)
    print(args)
