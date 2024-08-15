import os
import shutil
import pysftp
import zipfile
from datetime import datetime
from utils import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from inspect import currentframe, getframeinfo

frameinfo = getframeinfo(currentframe())

def zip_files(zip_name, *file_paths):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, arcname=os.path.basename(file_path))

script_path = os.path.dirname(__file__).replace("\\", "/")
script_name = os.path.splitext(os.path.basename(__file__))[0].replace("\\", "/")
init(script_name, script_path)
working_directory_path = get_config(section="Buffer", option="bufferpath")
live_run = get_config(
    section="Parametros", option="live_run", exit_if_not_exist=False, val_type="bool"
)
if live_run is None:
    live_run = False

extlog().error(f"{getframeinfo(currentframe()).lineno}: {getframeinfo(currentframe()).lineno}: LIVE RUN: {live_run}")
now_yyyymmdd = datetime.now().strftime("%Y%m%d")
now_yymmdd = datetime.now().strftime("%y%m%d")
source_path = os.path.join(working_directory_path, now_yyyymmdd)
extlog().debug(f"{getframeinfo(currentframe()).lineno}: source_path: {source_path}")
source_path_uploaded = os.path.join(source_path, 'uploaded')
extlog().debug(f"{getframeinfo(currentframe()).lineno}: source_path_uploaded: {source_path_uploaded}")
source_path_finished = os.path.join(source_path_uploaded, 'finished')
extlog().debug(f"{getframeinfo(currentframe()).lineno}: source_path_finished: {source_path_finished}")
source_file_mask = f'{get_config(section="MASK", option="source_file_mask")}{now_yymmdd}'
extlog().debug(f"{getframeinfo(currentframe()).lineno}: source_file_mask: {source_file_mask}")
source_file_uploaded_mask = get_config(section="MASK", option="source_file_uploaded_mask")
extlog().debug(f"{getframeinfo(currentframe()).lineno}: source_file_uploaded_mask: {source_file_uploaded_mask}")
dest_path = get_config(section="SFTP", option="dest_path")
extlog().debug(f"{getframeinfo(currentframe()).lineno}: dest_path: {dest_path}")
dest_path_in = get_config(section="SFTP", option="dest_path_in")
extlog().debug(f"{getframeinfo(currentframe()).lineno}: dest_path_in: {dest_path_in}")
dest_path_out = get_config(section="SFTP", option="dest_path_out")
extlog().debug(f"{getframeinfo(currentframe()).lineno}: dest_path_out: {dest_path_out}")

hostname = get_config(section="SFTP", option="server")
username = get_config(section="SFTP", option="user")
password = get_config(section="SFTP", option="pass")
cnopts = pysftp.CnOpts(knownhosts=os.path.expanduser(os.path.join('~', '.ssh', 'fake_known_hosts')))
cnopts.hostkeys = None

extlog().debug(f"{getframeinfo(currentframe()).lineno}: Verificando que exista la carpeta {source_path}")
if os.path.exists(source_path) and os.path.isdir(source_path):
    extlog().error(f"{getframeinfo(currentframe()).lineno}: Se encontro la carpeta {source_path}. Buscando archivos para subir")
    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Conectando al SFTP")
    if live_run:
        extlog().debug(f"{getframeinfo(currentframe()).lineno}: Conecta SFTP por live_run {live_run}")
        try:
            sftp = pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
        except Exception as e:
            extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al conectar al SFTP: {e}")
            exit_script(1)
    else:
        extlog().debug(f"{getframeinfo(currentframe()).lineno}: No conecta SFTP por live_run {live_run}")
    
    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Listando los archivos de {source_path}")
    source_files = os.listdir(source_path)

    for source_file in source_files:
        if source_file.startswith(source_file_mask):
            extlog().debug(f"{getframeinfo(currentframe()).lineno}: Sube {source_path}\{source_file} a {dest_path_out}{source_file}")
            if live_run:
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta PUT por live_run {live_run}")
                try:
                    sftp.put(localpath=f'{source_path}\{source_file}', remotepath=f'{dest_path_out}{source_file}')
                except Exception as e:
                    extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al subir el archivo {source_file}: {e}")
                    exit_script(1)
            else:
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta PUT por live_run {live_run}")

            if not os.path.exists(source_path_uploaded):
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Creando la carpeta {source_path_uploaded}")
                os.makedirs(source_path_uploaded)
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Creando la carpeta {source_path_finished}")
                os.makedirs(source_path_finished)

            extlog().debug(f"{getframeinfo(currentframe()).lineno}: Mueve {source_path}\{source_file} a {source_path_uploaded}\{source_file}")
            shutil.move(f'{source_path}\{source_file}', f'{source_path_uploaded}\{source_file}')

            if live_run:
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta sftp.close por live_run {live_run}")
                try:
                    sftp.close()
                except:
                    pass
            else:
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta sftp.close por live_run {live_run}")
    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Verificando si existe la carpeta {source_path_uploaded}")
    if os.path.exists(source_path_uploaded) and os.path.isdir(source_path_uploaded):
        extlog().debug(f"{getframeinfo(currentframe()).lineno}: Se encontro la carpeta {source_path_uploaded}. Buscando archivos de respuesta")
        source_files = os.listdir(source_path_uploaded)

        for source_file in source_files:
            if source_file.startswith(source_file_mask):
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Buscando respuestas para el archivo {source_file}")
                file_name, file_extension = os.path.splitext(source_file)
                response_file_name_1 = f"{source_file_uploaded_mask}1_{file_name}.txt"
                response_file_name_2 = f"{source_file_uploaded_mask}2_{file_name}.507"
                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Conectando al FTP")
                if live_run:
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Conecta SFTP por live_run {live_run}")
                    try:
                        sftp = pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts)
                    except Exception as e:
                        extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al conectar al SFTP: {e}")
                        exit_script(1)
                else:
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: No conecta SFTP por live_run {live_run}")

                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Chequeando si está el archivo {dest_path_in}{response_file_name_1}")
                if sftp.exists(f'{dest_path_in}{response_file_name_1}') if live_run else True:
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Descargando el archivo {dest_path_in}{response_file_name_1} en {source_path_finished}\{response_file_name_1}")
                    if live_run:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta GET por live_run {live_run}")
                        try:
                            sftp.get(f'{dest_path_in}{response_file_name_1}', f'{source_path_finished}\{response_file_name_1}')
                        except Exception as e:
                            extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al descargar el archivo {response_file_name_1}: {e}")
                            exit_script(1)
                    else:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta GET por live_run {live_run}")

                extlog().debug(f"{getframeinfo(currentframe()).lineno}: Chequeando si está el archivo {dest_path_in}{response_file_name_2}")
                if sftp.exists(f'{dest_path_in}{response_file_name_2}') if live_run else True:
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Descargando el archivo {dest_path_in}{response_file_name_2} en {source_path_finished}\{response_file_name_1}")
                    if live_run:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta GET por live_run {live_run}")
                        try:
                            sftp.get(f'{dest_path_in}{response_file_name_2}', f'{source_path_finished}\{response_file_name_2}')
                        except Exception as e:
                            extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al descargar el archivo {response_file_name_2}: {e}")
                            exit_script(1)
                    else:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta GET por live_run {live_run}")

                if os.path.exists(f'{source_path_finished}\{response_file_name_1}') and os.path.exists(f'{source_path_finished}\{response_file_name_2}'):
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Comprimiendo {source_path_finished}\{response_file_name_1} y {source_path_finished}\{response_file_name_2} en {source_path_finished}\{now_yyyymmdd}.zip")
                    try:
                        zip_files(f'{source_path_finished}\{now_yyyymmdd}.zip', f'{source_path_finished}\{response_file_name_1}', f'{source_path_finished}\{response_file_name_2}')
                    except Exception as e:
                        extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al comprimir los archivos de respuesta: {e}")
                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Mueve {source_path_uploaded}\{source_file} a {source_path_finished}\{source_file}")
                    try:
                        shutil.move(f'{source_path_uploaded}\{source_file}', f'{source_path_finished}\{source_file}')
                    except Exception as e:
                        extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al mover el archivo {source_file}: {e}")

                    smtp_server = get_config(section="SMTP", option="server")
                    smtp_port = get_config(section="SMTP", option="port")
                    smtp_user = get_config(section="SMTP", option="user")
                    smtp_password = get_config(section="SMTP", option="pass")
                    from_addr = get_config(section="SMTP", option="user")
                    to_addr = get_config(section="Parametros", option="mail_live" if live_run else "mail_test")
                    subject = 'Respuesta de PAGODIRECTO listo'
                    body = 'El archivo de respuesta de PAGODIRECTO está listo para enviar'
                    file_path = os.path.normpath(f'{source_path_finished}\{now_yyyymmdd}.zip')

                    msg = MIMEMultipart()
                    msg['From'] = from_addr
                    msg['To'] = to_addr
                    msg['Subject'] = subject

                    msg.attach(MIMEText(body, 'plain'))

                    with open(file_path, 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.split(file_path)[-1]}')
                        msg.attach(part)

                    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Enviando correo a {to_addr}")
                    # Enviar el correo
                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_user, smtp_password)
                            server.sendmail(from_addr, to_addr, msg.as_string())
                    except Exception as e:
                        extlog().error(f"{getframeinfo(currentframe()).lineno}: Error al enviar el correo: {e}")
                    if live_run:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta sftp.close por live_run {live_run}")
                        try:
                            sftp.close()
                        except:
                            pass
                    else:
                        extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta sftp.close por live_run {live_run}")
                else:
                    extlog().error(f"{getframeinfo(currentframe()).lineno}: No se encontraron los archivos de respuesta {response_file_name_1} y {response_file_name_2}")
    else:
        extlog().error(f"{getframeinfo(currentframe()).lineno}: No se encontro la carpeta {source_path_uploaded}")
else:
    extlog().error(f"{getframeinfo(currentframe()).lineno}: No se encontro la carpeta {source_path}")
if live_run:
    extlog().debug(f"{getframeinfo(currentframe()).lineno}: Ejecuta sftp.close por live_run {live_run}")
    try:
        sftp.close()
    except:
        pass
else:
    extlog().debug(f"{getframeinfo(currentframe()).lineno}: No ejecuta sftp.close por live_run {live_run}")

# Finaliza Script
logall(f"** Ending Script", "CRITICAL")
closelog()