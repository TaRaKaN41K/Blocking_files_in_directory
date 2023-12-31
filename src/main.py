import subprocess
import os
import shutil
import argparse
import hashlib
import getpass


parser = argparse.ArgumentParser()

old_name = file_to_delete = source_file = "1.txt"
new_name = "new.txt"
destination_file = "copy.txt"
template_file = "template.tbl"


def copy_create_delete_rename_check():

    # копирование
    try:
        shutil.copy(source_file, destination_file)
        print(f"Файл {source_file} успешно скопирован в {destination_file}")
    except Exception as e:
        print(f"Произошла ошибка при копировании файла: {e}")

    # создание
    try:
        with open("new.txt", "w"):
            pass
        if os.path.exists("new.txt"):
            print("Файл успешно создан.")
        else:
            print("Не удалось создать файл.")
    except Exception as e:
        print(f"Произошла ошибка при создании файла: {e}")

    # удаление
    try:
        os.remove(file_to_delete)
        print(f"Файл {file_to_delete} успешно удален.")
    except FileNotFoundError:
        print(f"Файл {file_to_delete} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при удалении файла: {e}")

    # переименование
    try:
        os.rename(old_name, new_name)
        print(f"Файл {old_name} успешно переименован в {new_name}")
    except FileNotFoundError:
        print(f"Файл {old_name} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при переименовании файла: {e}")


def check_password(file_name: str, password: str) -> bool:

    unlock_temp_commands = [
        f"sudo chflags noschg {file_name}",
        f"chmod a+r {file_name}",
    ]

    lock_temp_commands = [
        f"chmod a-r {file_name}",
        f"sudo chflags schg {file_name}",
    ]

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    for temp_command in unlock_temp_commands:
        subprocess.run(temp_command, shell=True)

    with open(file_name, "r") as file:
        actual_hashed_password = file.readline().strip()

    for temp_command in lock_temp_commands:
        subprocess.run(temp_command, shell=True)

    if hashed_password == actual_hashed_password:
        correct_password = True
    else:
        correct_password = False

    return correct_password

def create_template_file(file_name: str):

    lock_temp_commands = [
        f"chmod a-rw {file_name}",
        f"sudo chflags schg {file_name}",
    ]

    if os.path.exists(file_name):
        return True
    else:
        user_password = getpass.getpass("Set a password: ")
        hashed_password = hashlib.sha256(user_password.encode()).hexdigest()
        file_names_block = input("Enter file names to protect (через пробел): ")

        with open(file_name, "a+") as file:
            file.seek(0)
            first_line = file.readline().strip()
            if not first_line:
                file.write(hashed_password + "\n")

        file_names = file_names_block.split()
        with open(file_name, "a") as file:
            for name in file_names:
                file.write(name + "\n")

        for temp_command in lock_temp_commands:
            subprocess.run(temp_command, shell=True)


def add_files_to_file(file_name, added_files_names):

    unlock_temp_commands = [
        f"sudo chflags noschg {file_name}",
        f"sudo chmod a+rw {file_name}",
    ]

    lock_temp_commands = [
        f"sudo chmod a-rw {file_name}",
        f"sudo chflags schg {file_name}",
    ]

    try:

        for temp_command in unlock_temp_commands:
            subprocess.run(temp_command, shell=True)

        with open(file_name, "r+") as file:
            file_content = file.read()
            for file_to_add in added_files_names:
                if file_to_add not in file_content:
                    file.write(file_to_add + "\n")
        print("The files were added successfully.")

        for temp_command in lock_temp_commands:
            subprocess.run(temp_command, shell=True)

    except Exception as e:
        print(f"Error: {e}")


def get_files_names_string(file_name) -> str:

    unlock_temp_commands = [
        f"sudo chflags noschg {file_name}",
        f"chmod a+r {file_name}",
    ]

    lock_temp_commands = [
        f"chmod a-r {file_name}",
        f"sudo chflags schg {file_name}",
    ]

    for temp_command in unlock_temp_commands:
        subprocess.run(temp_command, shell=True)

    with open(file_name, "r") as file:
        lines = file.readlines()[1:]

    for temp_command in lock_temp_commands:
        subprocess.run(temp_command, shell=True)

    result = "".join(lines)

    result = result.replace("\n", " ")

    return result


parser.add_argument("-l", "--lock", action="store_true")
parser.add_argument("-u", "--unlock", action="store_true")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-a", "--add", nargs="+")

args = parser.parse_args()
current_directory = os.getcwd()




if args.lock:

    create_template_file(template_file)

    password = False

    while not password:
        user_password = getpass.getpass("Enter the password for the utility: ")

        if check_password(template_file, user_password):
            password = True

            lock_files = get_files_names_string(template_file)

            lockCommands = [
                f"sudo chmod a-w {current_directory}",
                f"chmod a-rw {lock_files}",
                f"sudo chflags schg {lock_files}",
            ]

            for command in lockCommands:
                subprocess.run(command, shell=True)
        else:
            print("Incorrect password")

if args.unlock:

    password = False

    while not password:
        user_password = getpass.getpass("Enter the password for the utility: ")

        if check_password(template_file, user_password):
            password = True

            lock_files = get_files_names_string(template_file)

            unlockCommands = [
                f"sudo chflags noschg {lock_files}",
                f"chmod a+rw {lock_files}",
                f"sudo chmod a+w {current_directory}"
            ]

            for command in unlockCommands:
                subprocess.run(command, shell=True)
        else:
            print("Incorrect password")
if args.add:

    password = False

    while not password:
        user_password = getpass.getpass("Enter the password for the utility: ")

        if check_password(template_file, user_password):
            password = True

            files_to_add = args.add
            add_files_to_file(template_file, files_to_add)

        else:
            print("Incorrect password")

if args.test:
    copy_create_delete_rename_check()
