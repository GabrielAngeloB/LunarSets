import face_recognition
import dlib

def calcular_similaridade(imagem1, imagem2):
    imagem1 = face_recognition.load_image_file(imagem1)
    imagem2 = face_recognition.load_image_file(imagem2)

    if not face_recognition.face_encodings(imagem1):
        return "Não foi possível detectar um rosto na primeira imagem."
    if not face_recognition.face_encodings(imagem2):
        return "Não foi possível detectar um rosto na segunda imagem."

    face1 = face_recognition.face_encodings(imagem1)[0]
    face2 = face_recognition.face_encodings(imagem2)[0]

    distancia = face_recognition.face_distance([face1], face2)[0]
    similaridade = (1 - distancia) * 100

    return f"Similaridade entre os rostos: {similaridade:.2f}%"

imagem1 = 'static/uploads/foto1.jpg'  
imagem2 = 'static/uploads/foto2.jpg' 
resultado = calcular_similaridade(imagem1, imagem2)
print(resultado)