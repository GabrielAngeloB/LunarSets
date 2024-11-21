import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from deepface import DeepFace
from PIL import Image


def reconhecer_emocao(img_caminho):
    img = Image.open(img_caminho)
    nome_arquivo = os.path.basename(img.filename)
    nome, extensao = os.path.splitext(nome_arquivo)
    img = img.resize((224, 224))

    img.save(f"{nome}_ajustado{extensao}")
    try:
        result = DeepFace.analyze(
            img_path=f"{nome}_ajustado{extensao}", 
            actions=["emotion", "race"],
            detector_backend="mtcnn",
            enforce_detection=True,
            silent = True
        )
    except Exception as er:
        print(er)

    if isinstance(result, list):
        result = result[0]

    print(result['emotion'])
    print(result['race'])
