from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash, send_from_directory
from usuario import Usuario
from conquistas import Conquistas
from comentario import Comentario
from ferramentas import Ferramenta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import zipfile
import io
import imageio
import moviepy.editor
from moviepy.editor import VideoFileClip
import os
import tempfile
from dotenv import load_dotenv
from db_connection import create_connection, close_connection   
import time
from datetime import timedelta



app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
emails = []
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
PASTA_UPLOAD = 'pasta_upload'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
@app.context_processor
def inject_user():
    if 'id_usuario' in session:
        usuario = Usuario.buscarUsuario()  
        ferramenta = Ferramenta.buscarFerramenta()
    else:
        usuario = None  
        ferramenta = None
    return dict(usuario=usuario, ferramenta = ferramenta)

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    flash("Você tentou acessar uma página inválida!", 'error')
    return redirect(url_for('inicio'))


@app.route('/')
def base():
    return render_template('index.html')



@app.route('/inicio')
def inicio():
    ferramenta = Ferramenta.buscarFerramenta()
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
        usuario = Usuario.buscarUsuario()
    if usuario and usuario['email_usuario'] == 'gabridestiny@hotmail.com':
        Ferramenta.limpar_arquivos_antigos()

    return render_template('inicio.html', usuario=usuario, ferramenta = ferramenta)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/adicionar_ferramenta', methods=['GET', 'POST'])
def adicionar_ferramenta():
    if request.method == 'POST':
        nome_ferramenta = request.form['nome_ferramenta']
        nome_menor_ferramenta = request.form['nome_menor_ferramenta']  # Novo campo
        descricao = request.form['descricao']
        nome_pagina = request.form['nome_pagina']
        img_ferramenta = request.files['img_ferramenta']
        
        sucesso = Ferramenta.inserirFerramenta(nome_ferramenta, nome_menor_ferramenta, descricao, nome_pagina, img_ferramenta)
        if sucesso:
            return redirect(url_for('adicionar_ferramenta'))
    
    return render_template('adicionar_ferramenta.html')



@app.route('/logcad', methods=['GET', 'POST'])
def logcad():
    if 'id_usuario' in session:
        flash("Você já está logado!", 'danger')
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            email = request.form['email']
            senha = request.form['senha']
            return Usuario.autenticar(email, senha)
        
        elif action == 'register':
            nome = request.form['nome1']
            email = request.form['email1']
            senha = request.form['senha1']
            confsenha = request.form['confirm_senha']
            return Usuario.registrar(nome, email, senha, confsenha)

    return render_template('logcad.html')


@app.route('/leitor', methods=['GET', 'POST'])
def leitor():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST' and request.form.get('comentario'):
        comentario = request.form['comentario']
        Comentario.inserirComentario(comentario, 2)
        return redirect(url_for('leitor'))
    
    if request.method == 'POST':
        zip_file = request.files['zipfile']
        search_term = request.form['search_term']

        if zip_file and zip_file.filename.endswith('.zip'):
            zip_bytes = io.BytesIO(zip_file.read())
            results = Ferramenta.search_in_zip(zip_bytes, search_term)

            session['results'] = results
            session['search_term'] = search_term

            return redirect(url_for('leitor'))


    results = session.pop('results', None)
    search_term = session.pop('search_term', None)
    comentario = Comentario.listarComentario(2)

    return render_template('leitor.html', results=results, search_term=search_term, usuario=usuario, conquista = 4, comentario = comentario)

@app.route('/conversor', methods=['GET', 'POST'])
def conversor():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST':
        comentario = request.form['comentario']
        Comentario.inserirComentario(comentario, 1)
        return redirect(url_for('conversor'))
    comentario = Comentario.listarComentario(1)
    
    return render_template('conversor.html', usuario=usuario, comentario = comentario)

@app.route('/conversortxt', methods=['GET', 'POST'])
def conversortxt():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST':
        comentario = request.form['comentario']
        Comentario.inserirComentario(comentario, 3)
        return redirect(url_for('conversortxt'))
    comentario = Comentario.listarComentario(3)
    
    return render_template('conversortxt.html', usuario=usuario, comentario = comentario)



@app.route('/convertertxt', methods=['GET', 'POST'])
def convertertxt():
    print("Rota /convertertxt acessada")

    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        print("Usuário não logado")
        return redirect(url_for('logcad'))

    if 'arquivotxt' not in request.files:
        flash("Nenhum arquivo enviado", "warning")
        print("Nenhum arquivo enviado")
        return redirect(url_for('conversortxt'))
    
    arquivotxt = request.files['arquivotxt']
    if arquivotxt.filename == '':
        flash("Nenhum arquivo selecionado", "warning")
        print("Nenhum arquivo selecionado")
        return redirect(url_for('conversortxt'))

    arquivo_final = Ferramenta.convertertxt()

    try:
        print(f"Enviando o arquivo convertido: {arquivo_final}")

        return send_file(arquivo_final, as_attachment=True, download_name=os.path.basename(arquivo_final))
    finally:
        print("Arquivo enviado com sucesso")





@app.errorhandler(413)
def request_entity_too_large(error):
    flash("O arquivo enviado é muito grande! O limite é de 50 MB.", "danger")
    return redirect(url_for('logcad'))

@app.route('/converter', methods=['POST'])
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

    mp3_file_path = Ferramenta.converter()

    if not mp3_file_path:
        return redirect(url_for('conversor'))
    print(mp3_file_path)

    try:
        return send_file(mp3_file_path, as_attachment=True, download_name=os.path.basename(mp3_file_path), mimetype="audio/mpeg")
    finally:
        print("finally do converter")




@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    session.pop('nome_usuario', None)
    session.clear()
    flash("Logout bem sucedido!", "success")
    return redirect(url_for('logcad'))

@app.route('/pagina_usuario')
def pagina_usuario():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    conquistas = Conquistas.verificarConquistas()
    usuario = Usuario.buscarUsuario()
    
    if usuario:
        return render_template("pagina_usuario.html", usuario=usuario, conquistas = conquistas)
    else:
        flash("Erro ao carregar dados do usuário.", "danger")
        return redirect(url_for('inicio')) 
    


@app.route('/editar_usuario', methods=['GET', 'POST'])
def editar_usuario():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        email_usuario = request.form['email_usuario']
        senha_usuario = request.form['senha_usuario']
        bio_usuario = request.form['bio_usuario']
        img_perfil = request.files.get('img_perfil')


        if Usuario.atualizarUsuario(nome_usuario, email_usuario, senha_usuario, bio_usuario, img_perfil):
            return redirect(url_for('pagina_usuario')) 


    usuario = Usuario.buscarUsuario()
    if usuario:
        return render_template("editar_usuario.html", usuario=usuario)
    else:
        flash("Erro ao carregar dados do usuário.", "danger")
        return redirect(url_for('inicio')) 
    
@app.route('/trocar_senha', methods=['GET', 'POST'])
def trocar_senha():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    
    if request.method == 'POST':

        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        Usuario.trocarSenha(senha_atual, nova_senha, confirmar_senha)


    return render_template("trocar_senha.html", usuario=usuario)


@app.route('/contato')
def contato():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    return render_template('contato.html', usuario=usuario)

@app.route('/editar_comentario/<int:comentario_id>', methods=['POST'])
def editar_comentario(comentario_id):
    novo_texto = request.form['novo_texto']
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para editar comentários.", "danger")
        return redirect(url_for('logcad'))


    Comentario.editarComentario(comentario_id, novo_texto)
    flash("Comentário editado com sucesso!", "success")
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(url_for('inicio'))

@app.route('/deletar_comentario/<int:comentario_id>', methods=['POST'])
def deletar_comentario(comentario_id):
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para excluir comentários.", "danger")
        return redirect(url_for('logcad'))

    Comentario.deletarComentario(comentario_id)
 
    next_page = request.args.get('next') 
    if next_page:
        return redirect(next_page)
    return redirect(url_for('inicio'))


@app.route('/comparador', methods=['GET', 'POST'])
def comparador():
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST':
        comentario = request.form['comentario']
        Comentario.inserirComentario(comentario, 4)
        return redirect(url_for('conversor'))
    comentario = Comentario.listarComentario(4)
    
    return render_template('comparador.html', usuario=usuario, comentario = comentario)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)




