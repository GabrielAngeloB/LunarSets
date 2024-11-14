import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import create_connection, close_connection
from flask import session, flash, redirect, url_for, request, send_file
from werkzeug.utils import secure_filename
import time
import zipfile
import io
import imageio  
from moviepy.editor import VideoFileClip
import moviepy.editor
import os
import tempfile
from conquistas import Conquistas
import mimetypes
from datetime import datetime, timedelta
from docx import Document
from pptx import Presentation
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess
import pythoncom
from win32com import client as win32
import glob

class Ferramenta:
    UPLOAD_FOLDER = 'static/img'
    UPLOAD_ARQUIVO = 'pasta_upload'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    AUDIO_FOLDER = os.path.join(os.getcwd(), "audios")
    ARQUIVOS_FOLDER = os.path.join(os.getcwd(), "pasta_upload")
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Ferramenta.ALLOWED_EXTENSIONS
    
    def allowed_file2(filename, video=False):
        if video:
            return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'mp4'
        return False
    
    def allowed_file3(filename):
        allowed_extensions = {'doc', 'docx', 'ppt', 'pptx'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def buscarFerramenta():
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM ferramentas"
            cursor.execute(sql)
            ferramenta = cursor.fetchall()
            return ferramenta
        except Exception as err:
            flash(f"Erro ao buscar dados das ferramentas: {err}", "danger")
            return None
        finally:
            cursor.close()
            close_connection(conn)


    @staticmethod
    def inserirFerramenta(nome_ferramenta, nome_menor_ferramenta, descricao, nome_pagina, img_ferramenta):

        conn = create_connection()
        cursor = conn.cursor()

        if img_ferramenta and Ferramenta.allowed_file(img_ferramenta.filename):
            filename = secure_filename(img_ferramenta.filename)
            img_path = os.path.join(Ferramenta.UPLOAD_FOLDER, filename)
            img_ferramenta.save(img_path)  
            img_db_path = f"/{img_path}" 
        else:
            flash("Formato de arquivo inválido", "danger")
            return False

        try:

            sql = """
            INSERT INTO ferramentas (nome_ferramenta, nome_menor_ferramenta, descricao, img_ferramenta, nome_pagina)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nome_ferramenta, nome_menor_ferramenta, descricao, img_db_path, nome_pagina))
            conn.commit()
            flash("Ferramenta adicionada com sucesso!", "success")
            return True
        except Exception as err:
            flash(f"Erro ao inserir ferramenta: {err}", "danger")
            return False
        finally:
            cursor.close()
            close_connection(conn)
    @staticmethod
    def converter():
        if 'id_usuario' not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for('logcad'))

        if 'mp4file' not in request.files:
            flash("Nenhum arquivo enviado", "warning")
            return redirect(url_for('conversor'))

        mp4_file = request.files['mp4file']

        if mp4_file.filename == '':
            flash("Nenhum arquivo selecionado", "warning")
            return redirect(url_for('conversor'))

        if not Ferramenta.allowed_file2(mp4_file.filename, video=True):
            flash("Arquivo inválido, envie um arquivo MP4", "warning")
            return redirect(url_for('conversor'))

        try:

            mime_type, encoding = mimetypes.guess_type(mp4_file.filename)
            if mime_type != 'video/mp4':
                flash("Arquivo inválido, o arquivo enviado não é um vídeo MP4", "warning")
                return redirect(url_for('conversor'))


            if not os.path.exists(Ferramenta.AUDIO_FOLDER):
                os.makedirs(Ferramenta.AUDIO_FOLDER)


            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                mp4_file.save(temp_video.name)


                print(f"Arquivo de vídeo temporário salvo em: {temp_video.name}")

                video = VideoFileClip(temp_video.name)


                if video.audio is None:
                    flash("Este vídeo não contém áudio.", "warning")
                    video.close()  
                    return redirect(url_for('conversor'))

                mp4filename, file_extension = os.path.splitext(secure_filename(mp4_file.filename))
                mp3_file_path = os.path.join(Ferramenta.AUDIO_FOLDER, mp4filename + "_audio.mp3")


                audio = video.audio
                audio.write_audiofile(mp3_file_path)


                audio.reader.close_proc() 
                audio.close()
                video.close()

                print(f"Áudio convertido e salvo em: {mp3_file_path}")
                conn = create_connection()
                cursor = conn.cursor(dictionary=True, buffered=True)
                sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
                valores = (session['id_usuario'], "O MÚSICO",)
                cursor.execute(sql, valores)
                conquistas = cursor.fetchone()
                if conquistas['total_conquistas'] == 0:
                    Conquistas.conquista(5)
                cursor.close()
                close_connection(conn)

            return mp3_file_path  

        except Exception as e:
            flash(f"Erro ao processar o vídeo: {str(e)}", "danger")
            print(f"Erro: {str(e)}")
            return redirect(url_for('conversor'))



    def search_in_zip(zip_file, search_term):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        found_files = []
        sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
        valores = (session['id_usuario'], "O LEITOR",)
        cursor.execute(sql, valores)
        conquistas = cursor.fetchone()
        if conquistas['total_conquistas'] == 0:
            Conquistas.conquista(4)
        cursor.close()
        close_connection(conn)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith('/'):
                    continue
                with zip_ref.open(file_name) as file:
                    try:
                        content = file.read().decode('utf-8')
                        lines = content.splitlines()
                        lower_search_term = search_term.lower()
                        file_results = []
                        for line_num, line in enumerate(lines, 1):
                            if lower_search_term in line.lower():
                                file_results.append((line_num, line.strip()))
                        if file_results:
                            found_files.append((file_name, file_results))
                        
                    except UnicodeDecodeError:
                        print(f"Não foi possível decodificar o arquivo: {file_name}")
    
        return found_files
    @staticmethod
    def limpar_arquivos_antigos():
        agora = datetime.now()
        tempo_limite = timedelta(minutes=60)

        for arquivo in os.listdir(Ferramenta.AUDIO_FOLDER):
            caminho_arquivo = os.path.join(Ferramenta.AUDIO_FOLDER, arquivo)

            if os.path.isfile(caminho_arquivo):
                tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                
                if agora - tempo_modificacao > tempo_limite:
                    os.remove(caminho_arquivo)
        for arquivo in os.listdir(Ferramenta.ARQUIVOS_FOLDER):
            caminho_arquivo = os.path.join(Ferramenta.ARQUIVOS_FOLDER, arquivo)

            if os.path.isfile(caminho_arquivo):
                tempo_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                
                if agora - tempo_modificacao > tempo_limite:
                    os.remove(caminho_arquivo)
                    

    
    @staticmethod
    def convertertxt():
        print("Iniciando a função convertertxt()") 
        if 'id_usuario' not in session:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            print("Usuário não logado.")  
            return None

        if 'arquivotxt' not in request.files:
            flash("Nenhum arquivo enviado", "warning")
            print("Nenhum arquivo enviado.") 
            return None

        arquivotxt = request.files['arquivotxt']
        if arquivotxt.filename == '':
            flash("Nenhum arquivo selecionado", "warning")
            print("Arquivo vazio.")  
            return None

        if not Ferramenta.allowed_file3(arquivotxt.filename):
            flash("Arquivo inválido, envie um arquivo permitido.", "warning")
            print("Arquivo inválido.") 
            return None

        try:
            if not os.path.exists(Ferramenta.UPLOAD_ARQUIVO):
                os.makedirs(Ferramenta.UPLOAD_ARQUIVO)

      
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivotxt.filename)[1]) as arquivo_temporario:
                arquivotxt.save(arquivo_temporario.name)
                arquivo_temporario_caminho = arquivo_temporario.name
                print(f"Arquivo temporário salvo em: {arquivo_temporario_caminho}")

            
            try:
                libreoffice = r"C:\Program Files\LibreOffice\program\soffice.exe"
                subprocess.run([
                    libreoffice, '--headless', '--convert-to', 'pdf',
                    '--outdir', Ferramenta.UPLOAD_ARQUIVO, arquivo_temporario_caminho
                ], check=True)

            
                os.remove(arquivo_temporario_caminho)
                print(f"Arquivo temporário deletado: {arquivo_temporario_caminho}")


       
                arquivos_convertidos = glob.glob(os.path.join(Ferramenta.UPLOAD_ARQUIVO, "*.pdf"))
                arquivos_convertidos.sort(key=os.path.getmtime, reverse=True)  


                if arquivos_convertidos:
                    print(f"Arquivo convertido encontrado: {arquivos_convertidos[0]}")
                    conn = create_connection()
                    cursor = conn.cursor(dictionary=True, buffered=True)
                    sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
                    valores = (session['id_usuario'], "AMANTE DE PDF",)
                    cursor.execute(sql, valores)
                    conquistas = cursor.fetchone()
                    if conquistas['total_conquistas'] == 0:
                        Conquistas.conquista(6)
                    cursor.close()
                    close_connection(conn)
                    return arquivos_convertidos[0]
                    
                else:
                    flash("Erro ao converter o arquivo para PDF.", "danger")
                    print("Erro ao converter para PDF.") 
                    return None

            except subprocess.CalledProcessError as e:
                flash(f"Erro na conversão com LibreOffice: {str(e)}", "danger")
                print(f"Erro na conversão com LibreOffice: {str(e)}") 
                return None

        except Exception as e:
            flash(f"Erro ao processar o arquivo: {str(e)}", "danger")
            print(f"Erro ao processar o arquivo: {str(e)}")  
            return None