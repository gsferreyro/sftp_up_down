import os
from datetime import datetime
import confighandler
import logginghandler

# Filtrar UserWarning de openpyxl
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
global internallog
global log_level
global externallog
global configuration


def init(script_name: str, script_folder: str):
    global internallog
    global configuration
    global log_level
    global externallog

    intlog_folder = os.path.normpath(f"{script_folder}/log/")
    internallog = logginghandler.LoggingHandler(script_name, intlog_folder, "ERROR")
    config_folder = os.path.normpath(f"{script_folder}/config/{script_name}/")
    configuration = confighandler.ConfigHandler(script_name, config_folder)
    internallog.critical(f"Leyendo config en {configuration.filepath}")
    log_level = configuration.get("Logs", "loglevel")
    logfolder = os.path.normpath(configuration.get("Logs", "logpath"))
    logname = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{script_name}.log'
    externallog = logginghandler.LoggingHandler(logname, logfolder, log_level)
    internallog.critical(f"Escribiendo logs en {externallog.filepath}")


def intlog():
    return internallog


def extlog():
    return externallog


def config():
    return configuration


def get_loglevel():
    return log_level


def get_config(
    section,
    option,
    exit_if_not_exist: bool = True,
    val_type: str = "str",
    dict_separator: str = ",",
):
    return configuration.get(
        section=section,
        option=option,
        exit_if_not_exist=exit_if_not_exist,
        val_type=val_type,
        dict_separator=dict_separator,
    )


def intlogging(msg: str, level: str = None):
    if level is None:
        level = log_level
    level = internallog.get_level_number(level=level)
    internallog.log(msg=msg, level=level)


def extlogging(msg: str, level: str = None):
    if level is None:
        level = log_level
    level = externallog.get_level_number(level=level)
    externallog.log(msg=msg, level=level)


def logall(msg: str, level: str = None):
    if level is None:
        level = log_level
    intlogging(msg=msg, level=level)
    extlogging(msg=msg, level=level)


def closelog(log: logginghandler.LoggingHandler = None):
    if log is None:
        externallog.close()
        internallog.close()
    else:
        log.close()


def exit_script(exit_code: int = 0):
    logall(f"Exit code: {exit_code}", "CRITICAL")
    closelog()
    exit(exit_code)

def x_to_float(value, decimals: int = 2):
    try:
        float_value = float(value)
        return round(float_value, decimals)
    except (ValueError, TypeError):
        # Handle conversion errors
        raise ValueError(f"The value '{value}' cannot be converted to float.")