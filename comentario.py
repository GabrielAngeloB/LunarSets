# usuario.py
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import create_connection, close_connection
from flask import session, flash, redirect, url_for, request
from conquistas import Conquistas
from werkzeug.utils import secure_filename
import time
from datetime import datetime

def calcular_tempo_passado(data):
    agora = datetime.now()
    delta = agora - data
    
    if delta.days > 365:
        anos = delta.days // 365
        return f"Há {anos} anos" if anos > 1 else "Há 1 ano"
    elif delta.days > 30:
        meses = delta.days // 30
        return f"Há {meses} meses" if meses > 1 else "Há 1 mês"
    elif delta.days > 0:
        return f"Há {delta.days} dias"
    elif delta.seconds >= 3600:
        horas = delta.seconds // 3600
        return f"Há {horas} horas" if horas > 1 else "Há 1 hora"
    elif delta.seconds >= 60:
        minutos = delta.seconds // 60
        return f"Há {minutos} minutos" if minutos > 1 else "Há 1 minuto"
    else:
        return "Agora mesmo"

class Comentario:
    @staticmethod
    def listarComentario(idFerramenta):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT c.comentario_texto, c.id_comentario, c.horario_comentario, u.nome_usuario, u.img_perfil, u.id_usuario FROM comentarios c JOIN usuarios u on c.id_usuario = u.id_usuario WHERE c.id_ferramenta = %s order by id_comentario desc"
            valores = (idFerramenta,)
            cursor.execute(sql, valores)
            comentarios = cursor.fetchall()
            if comentarios:
                for comentario in comentarios:
                    comentario['hora_comentario'] = comentario['horario_comentario'].strftime('%H:%M') if comentario.get('horario_comentario') else None
                    comentario['data_comentario'] = comentario['horario_comentario'].strftime('%d/%m/%Y') if comentario.get('horario_comentario') else None
            return comentarios
        except Exception as err:
            flash(f"Erro ao buscar dados do usuário: {err}", "danger")
            return None
        finally:
            cursor.close()
            close_connection(conn)

    #------------#
    @staticmethod
    def inserirComentario(comentario, idFerramenta):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "INSERT INTO comentarios(comentario_texto, id_ferramenta, id_usuario) VALUES(%s, %s, %s)"
            valores = (comentario, idFerramenta, session['id_usuario'])
            cursor.execute(sql, valores)
            conn.commit()

            flash("Comentário realizado com sucesso!", "success")
            if Conquistas.conquista(2) == True:
                Conquistas.conquista(3)
            return redirect(request.referrer or url_for('index')) 
        
        
        except Exception as err:
            flash(f"Erro ao publicar comentário, erro: {err}", "danger")
            return None 
        finally:
            cursor.close()
            close_connection(conn)

    @staticmethod
    def deletarComentario(idComentario):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "DELETE FROM comentarios WHERE id_comentario = %s"
            valores = (idComentario,)
            cursor.execute(sql, valores)
            conn.commit()   
            flash("Comentário excluído com sucesso!", "success")
            return redirect(request.referrer or url_for('index')) 
        
        except Exception as err:
            flash(f"Erro ao excluir comentário: {err}", "danger")
            return None
        finally:
            cursor.close()
            close_connection(conn)

    @staticmethod
    def editarComentario(idComentario, novo_texto):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "UPDATE comentarios SET comentario_texto = %s WHERE id_comentario = %s"
            valores = (novo_texto, idComentario)
            cursor.execute(sql, valores)
            conn.commit()
            flash("Comentário atualizado com sucesso!", "success")
            return redirect(request.referrer or url_for('index'))
        
        except Exception as err:
            flash(f"Erro ao atualizar comentário: {err}", "danger")
            return None
        finally:
            cursor.close()
            close_connection(conn)