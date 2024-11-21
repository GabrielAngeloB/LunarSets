from gtts import gTTS
import os
texto = 'Testando o Texto para voz'
lingua = 'pt'
arquivo = gTTS(text = texto, lang=lingua, slow=False)
arquivo.save("pasta_upload/teste123.mp3")
os.system("start audios/teste123.mp3")