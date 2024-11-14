import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import create_connection, close_connection
from flask import session, flash, redirect, url_for
from werkzeug.utils import secure_filename
import time



class Conquistas:
    def conquista(numconquista):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        if numconquista == 1:
            try:
                sql = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                valores = ("PRIMEIRO LOGIN", "Você realizou seu primeiro Login!", session['id_usuario'],)
                cursor.execute(sql, valores)
                conn.commit()
                flash("Nova conquista! 'PRIMEIRO LOGIN', Veja seu perfil.", 'success')
                print("Conquista enviada!")
            except Exception as er:
                print(er)
            finally:
                cursor.close()
                close_connection(conn)
        if numconquista == 2:
            try:
                # Verificar se o usuário já possui a conquista
                sql = "SELECT COUNT(*) as total FROM conquistas WHERE nome_conquista = %s AND id_usuario = %s"
                valores = ("PRIMEIRO COMENTÁRIO", session['id_usuario'],)
                cursor.execute(sql, valores)
                resultado = cursor.fetchone()
                # Garantir que o resultado seja tratado corretamente
                if resultado and resultado['total'] == 0:
                    # Inserir a nova conquista
                    sql = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                    valores = ("PRIMEIRO COMENTÁRIO", "Você fez seu primeiro comentário!", session['id_usuario'],)
                    cursor.execute(sql, valores)
                    conn.commit()
                    flash("Nova conquista! 'PRIMEIRO COMENTÁRIO', Veja seu perfil.", 'success')
                    print("Conquista enviada!")
                elif resultado and resultado['total'] > 0:
                    print("Usuário já possui essa conquista.")
                    return True
                else:
                    print("Erro inesperado ou sem registros.")
            except Exception as er:
                print(f"Erro: {er}")
            finally:
                cursor.close()
                close_connection(conn)
        if numconquista == 3:
            try:
                # Verificar se o usuário já possui a conquista
                sql = "SELECT COUNT(*) as total FROM conquistas WHERE nome_conquista = %s AND id_usuario = %s"
                valores = ("O COMENTADOR", session['id_usuario'],)
                cursor.execute(sql, valores)
                resultado_conquista = cursor.fetchone()

                # Garantir que o resultado não seja None e verificar a contagem
                if resultado_conquista and resultado_conquista['total'] == 0:
                    # Verificar se o usuário tem exatamente 5 comentários
                    sql = "SELECT COUNT(*) as total FROM comentarios WHERE id_usuario = %s"
                    valores = (session['id_usuario'],)
                    cursor.execute(sql, valores)
                    resultado_comentarios = cursor.fetchone()

                    # Garantir que o resultado não seja None e verificar a contagem
                    if resultado_comentarios and resultado_comentarios['total'] == 5:
                        sql_insert = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                        valores_insert = ("O COMENTADOR", "Você realizou seu 5º comentário!", session['id_usuario'],)
                        cursor.execute(sql_insert, valores_insert)
                        conn.commit()
                        flash("Nova conquista! 'O COMENTADOR', Veja seu perfil.", 'success')
                        print("Conquista enviada!")
                    else:
                        print(f"Usuário tem {resultado_comentarios['total'] if resultado_comentarios else 0} comentários. Conquista não enviada.")
                else:
                    print("Usuário já possui essa conquista.")
            except Exception as er:
                print(f"Erro: {er}")
            finally:
                cursor.close()
                close_connection(conn)

                
        if numconquista == 4:
            try:
                sql = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                valores = ("O LEITOR", "Você utilizou o leitor pela primeira vez!", session['id_usuario'],)
                cursor.execute(sql, valores)
                conn.commit()
                flash("Nova conquista! 'O LEITOR', Veja seu perfil.", 'success')
                print("Conquista enviada!")
            except Exception as er:
                print(er)
            finally:
                cursor.close()
                close_connection(conn)


        if numconquista == 5:
            try:
                sql = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                valores = ("O MÚSICO", "Você converteu um arquivo MP4 pela primeira vez!", session['id_usuario'],)
                cursor.execute(sql, valores)
                conn.commit()
                flash("Nova conquista! 'O MÚSICO', Veja seu perfil.", 'success')
                print("Conquista enviada!")
            except Exception as er:
                print(er)
            finally:
                cursor.close()
                close_connection(conn)

        if numconquista == 6:
            try:
                sql = "INSERT INTO conquistas (nome_conquista, descricao_conquista, id_usuario) VALUES (%s, %s, %s)"
                valores = ("AMANTE DE PDF", "Você converteu um arquivo em PDF pela primeira vez!", session['id_usuario'],)
                cursor.execute(sql, valores)
                conn.commit()
                flash("Nova conquista! 'AMANTE DE PDF', Veja seu perfil.", 'success')
                print("Conquista enviada!")
            except Exception as er:
                print(er)
            finally:
                cursor.close()
                close_connection(conn)
                


    def verificarConquistas():
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = "SELECT nome_conquista, descricao_conquista, data_conquista FROM conquistas WHERE id_usuario = %s"
            valores = (session['id_usuario'],)
            cursor.execute(sql, valores)
            conquistas = cursor.fetchall()  # Alterado para fetchall() para obter todas as conquistas do usuário
            
            for conquista in conquistas:
                if conquista['data_conquista']:
                    conquista['data_conquista_formatada'] = conquista['data_conquista'].strftime('%d/%m/%Y %H:%M')

            return conquistas
        except Exception as er:
            print(er)
            flash("DEU ERRO MANÉ", 'error')
            return er
        finally:
            cursor.close()
            close_connection(conn)


    
        




        
