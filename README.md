🎵 Spotify to YouTube Music Playlist Cloner
Este proyecto permite clonar automáticamente tus playlists de Spotify en YouTube Music. Utiliza la API oficial de YouTube sin necesidad de automatización de navegador, y guarda el progreso y las búsquedas en archivos JSON para permitir ejecuciones diarias y evitar duplicados.

🚀 Características
🔄 Clonación automática de playlists de Spotify en YouTube Music.

💾 Progreso guardado en progress.json para continuar el trabajo en futuras ejecuciones.

⚡️ Sistema de caché yt_cache.json para evitar búsquedas duplicadas en YouTube.

✅ Detección de canciones ya añadidas, incluso si las agregaste manualmente.

🔁 Soporte para playlists largas (más de 100 canciones) gracias a la paginación.

📂 Estructura de archivos

.env: Credenciales de Spotify.

client_secret_google.json: Credenciales OAuth de Google.

yt_cache.json: Búsquedas ya realizadas en YouTube (generado por el script).

progress.json: Progreso de las playlists clonadas (generado por el script).

main.py: Script principal.

🔧 Requisitos
Python 3.10 o superior.

Librerías:

spotipy

google-auth-oauthlib

google-api-python-client

python-dotenv

Instalar dependencias:

bash
Copiar
Editar
pip install spotipy google-auth-oauthlib google-api-python-client python-dotenv
⚙️ Configuración
Crea un archivo .env con tus credenciales de Spotify:

env
SPOTIPY_CLIENT_ID=tu_client_id
SPOTIPY_CLIENT_SECRET=tu_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8080
Descarga las credenciales de Google (client_secret_google.json) desde Google Cloud Console con permisos para la API de YouTube Data v3.

▶️ Ejecución
bash
python main.py
El script te pedirá iniciar sesión en Google en la primera ejecución.
Cada vez que lo ejecutes continuará desde donde lo dejaste.

🕒 Limitaciones
La API de YouTube tiene un límite de aproximadamente 70-100 canciones por día debido a las cuotas.

Es posible ejecutar el script cada día para completar las playlists más grandes.

📌 Nota
El script detecta y evita duplicados, incluso si las canciones fueron añadidas manualmente en YouTube Music fuera del script.
