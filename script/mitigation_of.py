import os
import subprocess
import time

# 1. Изменение строки в файле /etc/default/grub
def modify_grub_config():
    grub_file = "/etc/default/grub"
    new_grub_cmdline = 'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash pti=off spectre_v1=off spectre_v2=off l1tf=off nospec_store_bypass_disable ibrs=off stibp=off ssbd=off l1d_flush=off mds=off tsx_async_abort=off mitigations=off noibpb no_stf_barrier tsx=on retbleed=off spectre_v2=retpoline,force"\n'
    
    try:
        with open(grub_file, 'r') as file:
            lines = file.readlines()

        for i in range(len(lines)):
            if lines[i].startswith("GRUB_CMDLINE_LINUX_DEFAULT"):
                lines[i] = new_grub_cmdline

        with open(grub_file, 'w') as file:
            file.writelines(lines)

        print("GRUB configuration modified successfully.")
    except Exception as e:
        print(f"Failed to modify GRUB config: {e}")

# 2. Выполнение update-grub
def update_grub():
    try:
        subprocess.run(["sudo", "update-grub"], check=True)
        print("GRUB updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update GRUB: {e}")

# 3. Перезагрузка системы
def reboot_system():
    try:
        print("Rebooting system...")
        subprocess.run(["sudo", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to reboot: {e}")

# 4. Установка spectre-meltdown-checker
def install_spectre_meltdown_checker():
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "spectre-meltdown-checker"], check=True)
        print("spectre-meltdown-checker installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install spectre-meltdown-checker: {e}")

# 5. Выполнение команды spectre-meltdown-checker и вывод результата
def run_spectre_meltdown_checker():
    try:
        result = subprocess.run(["sudo", "spectre-meltdown-checker"], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run spectre-meltdown-checker: {e}")

# Основной процесс
if __name__ == "__main__":
    # 1. Модификация файла GRUB
    modify_grub_config()
    
    # 2. Обновление конфигурации GRUB
    update_grub()

    # 3. Перезагрузка системы (после этого скрипт прерывается)
    reboot_system()

    # Следующие шаги выполните вручную после перезагрузки:
    time.sleep(60)  # Задержка, чтобы система успела перезагрузиться
    
    # 4. Установка spectre-meltdown-checker
    install_spectre_meltdown_checker()

    # 5. Запуск spectre-meltdown-checker и вывод результата
    run_spectre_meltdown_checker()
