import yt_dlp


def pegar_mp4(url):
    ydl_opts = {
        'format': 'best', 
        'outtmpl': 'downloads/%(title)s.%(ext)s', 
        'max_filesize': 50 * 1024 * 1024,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def pegar_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',  
        'outtmpl': 'downloads/%(title)s.%(ext)s',  
        'postprocessors': [{  
            'key': 'FFmpegAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    

pegar_mp4("https://www.youtube.com/watch?v=YhvLXwmCO4E")

    





    