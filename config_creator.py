import sys
import os
import configparser


def create_config(config_path: str):
    config = configparser.RawConfigParser()

    config.add_section("Parametros")
    config.set("Parametros", "live_run", "False")
    config.set("Parametros", "mail_test", "")
    config.set("Parametros", "mail_live", "")

    config.add_section("Buffer")
    config.set("Buffer", "bufferdisk", "")
    config.set("Buffer", "bufferrootfolder", "")
    config.set("Buffer", "buffername", "")
    config.set(
        "Buffer", "bufferpath", "%(bufferdisk)s%(bufferrootfolder)s%(buffername)s"
    )

    config.add_section("Logs")
    config.set("Logs", "logdisk", "")
    config.set("Logs", "logrootfolder", "")
    config.set("Logs", "logname", "")
    config.set("Logs", "logpath", "%(logdisk)s%(logrootfolder)s%(logname)s")
    config.set("Logs", "loglevel", "ERROR")

    config.add_section("SMTP")
    config.set("SMTP", "server", "")
    config.set("SMTP", "port", "")
    config.set("SMTP", "user", "")
    config.set("SMTP", "pass", "")

    with open(config_path, "w") as configfile:
        config.write(configfile)


def main():
    # Parametro 1 = path donde dejar el config
    try:
        config_path = sys.argv[1]
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        config_name = f"config.ini"
    except Exception:
        config_path = f"{os.path.dirname(__file__)}"
        config_name = input("Nombre del script (config): ")
        config_name = f"config_{config_name}"
        if config_name[-4:] != ".ini":
            config_name += ".ini"
    finally:
        config_path += f"{config_path}\\{config_name}"

    create_config(config_path=config_path)


if __name__ == "__main__":
    main()
