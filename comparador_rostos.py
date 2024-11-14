import face_recognition
import dlib

def calcular_similaridade(imagem1_path, imagem2_path):
    imagem1 = face_recognition.load_image_file(imagem1_path)
    imagem2 = face_recognition.load_image_file(imagem2_path)

    if not face_recognition.face_encodings(imagem1):
        return "Não foi possível detectar um rosto na primeira imagem."
    if not face_recognition.face_encodings(imagem2):
        return "Não foi possível detectar um rosto na segunda imagem."

    face1 = face_recognition.face_encodings(imagem1)[0]
    face2 = face_recognition.face_encodings(imagem2)[0]

    distancia = face_recognition.face_distance([face1], face2)[0]
    similaridade = (1 - distancia) * 100

    return f"Similaridade: {similaridade:.2f}%, Distancia: {distancia}%"

imagem1_path = 'foto1.jpg'  
imagem2_path = 'foto2.jpg' 
resultado = calcular_similaridade(imagem1_path, imagem2_path)
print(resultado)