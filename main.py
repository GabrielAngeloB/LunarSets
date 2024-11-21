from gevent import monkey
monkey.patch_all()

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
from animais_dados import dadosAnimal, animal_names, iucn_portuguese, iucn_english
from flask_socketio import SocketIO, emit
import base64
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import numpy as np
from gtts import gTTS
import yt_dlp
import os






app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")


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
    if usuario and session['email'] == 'gabridestiny@hotmail.com':
        Ferramenta.limpar_arquivos_antigos()

    return render_template('inicio.html', usuario=usuario, ferramenta = ferramenta)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/adicionar_ferramenta', methods=['GET', 'POST'])
def adicionar_ferramenta():
    if session['email'] != "gabridestiny@hotmail.com":
        return redirect(url_for("inicio"))
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


def info_animal():
    random_animal = dadosAnimal.get_random_animal()  # Pega um animal aleatório
    print(f"Buscando informações para o animal: {random_animal}")
    animal_info = dadosAnimal.get_animal_data(random_animal)  # Obtém as informações
    if not animal_info["iucn_status"]:
        animal_info["iucn_status"] = "Não Disponível"
    if animal_info == False:
        return False


    if animal_info and animal_info["iucn_status"] in iucn_portuguese or animal_info["iucn_status"] in iucn_english:
        return animal_info  # Exibe as informações se encontrar o IUCN status válido
    else:
        return False  # Mensagem caso o status não seja encontrado

@socketio.on("data_animal")
def handle_data_animal():
    data = info_animal()
    while data == False:
        data = info_animal()
        time.sleep(1)
    if data != False:
        emit("update_animal_data", data)



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


@app.route('/animais_aleatorio', methods=['GET', 'POST'])
def animais_aleatorio():
    
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST':
        comentario = request.form['comentario']
        Comentario.inserirComentario(comentario, 4)
        return redirect(url_for('animais_aleatorio'))
    comentario = Comentario.listarComentario(4)
    conn = create_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
    valores = (session['id_usuario'], "O ZOÓLOGO",)
    cursor.execute(sql, valores)
    conquistas = cursor.fetchone()
    if conquistas['total_conquistas'] == 0:
        Conquistas.conquista(7)
    cursor.close()
    close_connection(conn)
    
    
    return render_template('animais_aleatorio.html', usuario=usuario, comentario = comentario)
    

@socketio.on('dados_comparador')
def calcular_similaridade(dados):
    img1 = dados.get('img1')
    img2 = dados.get('img2')
    

    if img1 and img2:
        # Salva a primeira imagem
        image1_bytes = base64.b64decode(img1['content'], validate=False)
        image1_path = f"static/uploads/{session['nome_usuario']}{img1['filename']}"
        os.makedirs(os.path.dirname(image1_path), exist_ok=True)
        with open(image1_path, 'wb') as f:
            f.write(image1_bytes)

        # Salva a segunda imagem
        image2_bytes = base64.b64decode(img2['content'], validate=False)
        image2_path = f"static/uploads/{session['id_usuario']}{14451}{img2['filename']}"
        with open(image2_path, 'wb') as f:
            f.write(image2_bytes)

        # Calcula a similaridade entre as imagens
        resultado = Ferramenta.calcular_similaridade(image1_path, image2_path)
        print(resultado)
        conn = create_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
        valores = (session['id_usuario'], "O MÍMICO",)
        cursor.execute(sql, valores)
        conquistas = cursor.fetchone()
        if conquistas['total_conquistas'] == 0:
            Conquistas.conquista(8)
        cursor.close()
        close_connection(conn)

        # Envia o resultado ao cliente (pode ser o valor da similaridade)
        emit('dados_similaridade', {'resultado': resultado})
    else:
        emit('dados_similaridade', {'erro': "Erro: Imagens não enviadas ou inválidas."})

@app.route('/comparador_rostos', methods=['GET', 'POST'])
def comparador_rostos():
    
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST' and request.form.get('comentario') != None:
        comentario = request.form.get('comentario')
        Comentario.inserirComentario(comentario, 5)
        return redirect(url_for('comparador_rostos'))
    comentario = Comentario.listarComentario(5)

    return render_template('comparador_rostos.html', usuario=usuario, comentario = comentario)



@app.route('/analise_emocao', methods=['GET', 'POST'])
def analise_emocao():
    
    usuario = Usuario.buscarUsuario()
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))
    if request.method == 'POST' and request.form.get('comentario') != None:
        comentario = request.form.get('comentario')
        Comentario.inserirComentario(comentario, 6)
        return redirect(url_for('analise_emocao'))
    comentario = Comentario.listarComentario(6)

    return render_template('analise_emocao.html', usuario=usuario, comentario = comentario)


def convert_numpy_to_json_serializable(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_to_json_serializable(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_json_serializable(v) for k, v in obj.items()}
    return obj  




@socketio.on('dados_analise')
def analise_emocao(dados):
    img1 = dados.get('img1')
    

    if img1:
        # Salva a primeira imagem
        image1_bytes = base64.b64decode(img1['content'], validate=False)
        image1_path = f"static/uploads/{session['nome_usuario']}{img1['filename']}"
        os.makedirs(os.path.dirname(image1_path), exist_ok=True)
        with open(image1_path, 'wb') as f:
            f.write(image1_bytes)

        # Calcula a similaridade entre as imagens
        resultado = Ferramenta.reconhecer_emocao(image1_path)
       
        resultado_serializable = convert_numpy_to_json_serializable(resultado)
        if resultado != False:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            sql = "SELECT COUNT(*) as total_conquistas from conquistas WHERE id_usuario = %s and nome_conquista = %s"
            valores = (session['id_usuario'], "O DETETIVE",)
            cursor.execute(sql, valores)
            conquistas = cursor.fetchone()
            if conquistas['total_conquistas'] == 0:
                Conquistas.conquista(9)
            cursor.close()
            close_connection(conn)
            emit('dados_analise', {'resultado': resultado_serializable})
        else:
            emit('dados_analise', {'erro': "Erro: Não foi encontrado um rosto na imagem."})
    else:
        emit('dados_analise', {'erro': "Erro: Imagens não enviadas ou inválidas."})




@app.route('/texto_voz', methods=['GET', 'POST'])
def texto_voz():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))

    if request.method == 'POST':
        texto = request.form.get('texto')  # Pegando o texto enviado pelo usuário
        if not texto:
            flash("Nenhum texto enviado", "warning")
            return redirect(url_for('texto_voz'))

        # Converter o texto em áudio
        try:
            tts = gTTS(text=texto, lang='pt', slow=False)
            
            # Salvar o áudio em um arquivo temporário
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_audio.name)

            # Retornar o arquivo para o usuário
            return send_file(temp_audio.name, as_attachment=True, download_name="texto_para_audio.mp3", mimetype="audio/mpeg")
        
        except Exception as e:
            flash(f"Ocorreu um erro ao gerar o áudio: {str(e)}", "danger")
            return redirect(url_for('texto_voz'))
    
    return render_template('texto_voz.html')

def pegar_mp4(url):
    # Definir o diretório de destino
    download_dir = 'pasta_upload'
    
    # Criar o diretório se não existir
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # Caminho completo
        'max_filesize': 50 * 1024 * 1024,  # Limitar a 50MB
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        flash(f"Erro ao tentar baixar MP4: {str(e)}", "danger")
        raise

# Função para pegar MP3
def pegar_mp3(url):
    # Definir o diretório de destino
    download_dir = 'pasta_upload'
    
    # Criar o diretório se não existir
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # Caminho completo
        'postprocessors': [{
            'key': 'FFmpegAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        flash(f"Erro ao tentar baixar MP3: {str(e)}", "danger")
        raise


@app.route('/baixar_site_misterioso', methods=['GET', 'POST'])
def baixar_site_misterioso():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.", "danger")
        return redirect(url_for('logcad'))

    if request.method == 'POST':
        url = request.form.get('url')  # Pegando a URL enviada pelo usuário
        formato = request.form.get('formato')  # Pegando o formato escolhido (mp3 ou mp4)

        if not url:
            flash("Nenhuma URL fornecida", "warning")
            return redirect(url_for('baixar_site_misterioso'))

        if not formato or formato not in ['mp4', 'mp3']:
            flash("Formato inválido. Escolha entre MP3 ou MP4.", "danger")
            return redirect(url_for('baixar_site_misterioso'))

        try:
            # Realiza o download com base no formato escolhido
            if formato == 'mp4':
                pegar_mp4(url)
                flash("Download do MP4 iniciado!", "success")
            elif formato == 'mp3':
                pegar_mp3(url)
                flash("Download do MP3 iniciado!", "success")

            # Após o download, redireciona para a página onde o usuário pode visualizar o progresso ou resultados
            return redirect(url_for('baixar_site_misterioso'))

        except Exception as e:
            flash(f"Erro ao processar o arquivo: {str(e)}", "danger")
            return redirect(url_for('baixar_site_misterioso'))

    return render_template('baixar_site_misterioso.html')



if __name__ == '__main__':
    print("Servidor iniciado em http://0.0.0.0:8000")
    http_server = WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()




