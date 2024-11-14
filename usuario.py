# usuario.py
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db_connection import create_connection, close_connection
from flask import session, flash, redirect, url_for
from conquistas import Conquistas
from werkzeug.utils import secure_filename
import time


class Usuario:
    @staticmethod
    def autenticar(email, senha):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        try:
            # Busca o usuário pelo nome
            cursor.execute("SELECT * FROM usuarios WHERE email_usuario = %s", (email,))
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario['senha_usuario'], senha):
                session['id_usuario'] = usuario['id_usuario']
                session['email'] = usuario['email_usuario']
                session['nome_usuario'] = usuario['nome_usuario']
                sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s"
                valores = (session['id_usuario'],)
                cursor.execute(sql, valores)
                conquistas = cursor.fetchone()
                flash("Login bem-sucedido!", "success")
                if conquistas['total_conquistas'] == 0:
                    Conquistas.conquista(1) 
                return redirect(url_for('inicio'))
            else:
                flash("Email de usuário ou senha incorretos.", "error")
                return redirect(url_for('logcad'))
        except Exception as er:
            print(er)
        finally:
            cursor.close()
            close_connection(conn)
    
    @staticmethod
    def registrar(nome, email, senha, confsenha):
        conn = create_connection()
        cursor = conn.cursor()
        
        if senha != confsenha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for('logcad'))
        
        if len(senha) <= 7:
            flash("A senha é muito pequena", "danger")
            return redirect(url_for('logcad'))
        
        try:
            # Verifica se já existe um usuário com o mesmo nome ou e-mail
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE nome_usuario = %s OR email_usuario = %s",
                (nome, email)
            )
            if cursor.fetchone()[0] > 0:
                flash("Nome de usuário ou e-mail já cadastrado.", "danger")
                return redirect(url_for('logcad'))
            
            # Se não existir, realiza o cadastro
            senha_hash = generate_password_hash(senha)
            cursor.execute(
                "INSERT INTO usuarios (nome_usuario, email_usuario, senha_usuario) VALUES (%s, %s, %s)",
                (nome, email, senha_hash)
            )
            conn.commit()
            flash("Cadastro realizado com sucesso! Agora faça login.", "success")
            return redirect(url_for('logcad'))
        
        except Exception as err:
            flash(f"Erro ao registrar: {err}", "danger")
            return redirect(url_for('logcad'))
        
        finally:
            cursor.close()
            close_connection(conn)

    @staticmethod
    def atualizarUsuario(nome_usuario, email_usuario, senha_usuario, bio_usuario, img_perfil):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Verificar se já existe outro usuário com o mesmo e-mail ou nome
            sql_verificacao_unico = """
                SELECT id_usuario 
                FROM usuarios 
                WHERE (email_usuario = %s OR nome_usuario = %s) AND id_usuario != %s
            """
            valores_verificacao_unico = (email_usuario, nome_usuario, session['id_usuario'])
            cursor.execute(sql_verificacao_unico, valores_verificacao_unico)
            usuario_existente = cursor.fetchone()
            
            if usuario_existente:
                flash("Já existe um usuário com este e-mail ou nome!", "danger")
                return False

            # Verificar a senha atual do usuário
            sql_verificacao = "SELECT senha_usuario, img_perfil FROM usuarios WHERE id_usuario = %s"
            valores_verificacao = (session['id_usuario'],)
            cursor.execute(sql_verificacao, valores_verificacao)
            usuario_banco = cursor.fetchone()

            if check_password_hash(usuario_banco['senha_usuario'], senha_usuario):
                if img_perfil and img_perfil.filename:
                    nome_original = secure_filename(img_perfil.filename)
                    timestamp = int(time.time())
                    nome_imagem = f"{timestamp}_{nome_original}"
                    img_caminho = os.path.join('static', 'img', 'perfis', nome_imagem)
                    img_perfil.save(img_caminho)

                    caminho_relativo_img = os.path.join('img', 'perfis', nome_imagem).replace("\\", "/")
                else:
                    caminho_relativo_img = usuario_banco['img_perfil']

                sql = """
                    UPDATE usuarios 
                    SET nome_usuario = %s, email_usuario = %s, bio_usuario = %s, img_perfil = %s
                    WHERE id_usuario = %s
                """
                valores = (nome_usuario, email_usuario, bio_usuario, caminho_relativo_img, session['id_usuario'])
                cursor.execute(sql, valores)
                conn.commit()
                flash("Dados atualizados com sucesso!", "success")
                return True
            else:
                flash("Senha incorreta. Por favor, tente novamente.", "danger")
                return False

        except Exception as err:
            flash(f"Erro ao modificar seus dados: {err}", "danger")
            return False
        
        finally:
            cursor.close()
            close_connection(conn)



    @staticmethod
    def buscarUsuario():
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT nome_usuario, email_usuario,
                    horario_criacao,  -- mantenha como datetime
                    bio_usuario, img_perfil 
                FROM usuarios 
                WHERE id_usuario = %s
            """
            valores = (session['id_usuario'],)
            cursor.execute(sql, valores)
            usuario = cursor.fetchone()

            if usuario:
                usuario['hora_criacao'] = usuario['horario_criacao'].strftime('%H:%M') if usuario['horario_criacao'] else None
                usuario['data_criacao'] = usuario['horario_criacao'].strftime('%d/%m/%Y') if usuario['horario_criacao'] else None
                
            return usuario
        except Exception as err:
            flash(f"Erro ao buscar dados do usuário: {err}", "danger")
            return None
        finally:
            cursor.close()
            close_connection(conn)





    @staticmethod
    def trocarSenha(senha_atual, senha_nova, confirm_senha):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        if senha_atual == senha_nova or senha_atual == confirm_senha:
            flash("A nova senha não pode ser igual a senha antiga!", 'danger')
            return redirect(url_for('trocar_senha'))
        if senha_nova == confirm_senha:
            try:
                sql_verificacao = "SELECT senha_usuario FROM usuarios WHERE id_usuario = %s"
                valores_verificacao = (session['id_usuario'],)
                cursor.execute(sql_verificacao, valores_verificacao)
                usuario_banco = cursor.fetchone()
                senha_hash = generate_password_hash(senha_nova)

                if check_password_hash(usuario_banco['senha_usuario'], senha_atual):
                    sql = """
                        UPDATE usuarios 
                        SET senha_usuario = %s
                        WHERE id_usuario = %s
                    """
                    valores = (senha_hash, session['id_usuario'])
                    cursor.execute(sql, valores)
                    conn.commit()
                    flash("Dados atualizados com sucesso!", "success")
                    return redirect(url_for('inicio'))
                else:
                    flash("A senha atual não está correta! Por favor, tente novamente.", "danger")
                    return redirect(url_for('trocar_senha'))
            except Exception as err:
                flash(f"Erro ao modificar seus dados: {err}", "danger")
                return redirect(url_for('trocar_senha'))
            finally:
                cursor.close()
                close_connection(conn)
        else:
            flash("As senhas não coincidem!!", 'danger')
            return redirect(url_for('trocar_senha'))

