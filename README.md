🦜 Habla Correcto

Un juego con interfaz gráfica para que niños practiquen su pronunciación en inglés. El juego muestra una palabra en español, el jugador dice la traducción en inglés, y la aplicación graba su voz, la reconoce y la compara con la respuesta correcta.

Hecho para una escuela de idiomas en línea que enseña inglés.

🎮 ¿Cómo funciona?
👀 Aparece un dibujo y una palabra en español 🇪🇸
🎤 El jugador pulsa ¡HABLA! y dice la palabra en inglés 🇬🇧
🧠 La app graba la voz, la convierte en texto y la compara con la traducción
⭐ Si acierta, gana estrellas. Si falla, pierde una vida ❤️

Lora, el loro 🦜, acompaña al jugador con mensajes y cambia de cara según lo que pase.

✨ Características
Reconocimiento de voz en inglés con Google Speech Recognition
Traducción de inglés a español con googletrans, con un diccionario de respaldo si no hay conexión
3 niveles de dificultad: 🐣 Fácil, 🐥 Medio y 🦅 Difícil
Sistema de estrellas con bonus por racha, por intentos y por no usar pistas
Vidas, pistas y botón de saltar
Fin del juego al quedarse sin vidas o al terminar todas las rondas
Interfaz para niños: botones grandes, colores alegres, un dibujo por palabra, confeti y sonidos
Récord que se guarda entre partidas
Detecta cuando una palabra sonó "casi" bien (80 % de parecido o más)
📋 Requisitos
Python 3.8 o superior (con tkinter, que ya viene incluido en Windows y Mac)
Micrófono
Conexión a internet (para reconocer la voz)
🚀 Instalación y ejecución
Descarga habla_correcto_ninos.py y guárdalo en una carpeta.
Abre una terminal dentro de esa carpeta.
Ejecuta:
python habla_correcto_ninos.py

La primera vez, el programa instala solo las librerías que falten:

Librería	Para qué sirve
sounddevice	Grabar el audio del micrófono
scipy	Guardar la grabación como archivo .wav
SpeechRecognition	Convertir la voz en texto
googletrans	Traducir las palabras (opcional)

Si prefieres instalarlas tú mismo:

pip install sounddevice scipy SpeechRecognition
pip install googletrans==4.0.0rc1

Si googletrans no se puede instalar con tu versión de Python, el juego sigue funcionando con su diccionario de respaldo de 30 palabras.

🕹️ Cómo se juega
Escribe tu nombre y elige un nivel.
(Opcional) Pulsa Probar mi micrófono y di “hello”.
Pulsa ¡A JUGAR!
En cada ronda pulsa ¡HABLA! cuando estés listo y di la palabra en inglés.
Usa 💡 Pista si te atascas, o ⏭️ Saltar para pasar a la siguiente.
🎚️ Niveles
Nivel	Rondas	Vidas	Intentos por palabra	Segundos para hablar	Multiplicador
🐣 Fácil	6	5	3	3	x1
🐥 Medio	8	4	2	4	x2
🦅 Difícil	10	3	1	4	x3
⭐ Puntuación

Cada palabra correcta suma:

10 × multiplicador del nivel
+3 por cada intento que no hizo falta usar
+2 por cada acierto seguido (racha)
+5 si no usó la pista

Además:

La pista cuesta −5 estrellas.
Al terminar todas las rondas, cada vida que queda da +10 estrellas.
🏁 Fin del juego
💀 Se pierde si el jugador se queda sin vidas.
🏆 Se gana al completar todas las rondas.
Al final se muestran de 1 a 3 estrellas ⭐ y un título según el porcentaje de aciertos:
Aciertos	Título
Menos de 30 %	🌱 Semillita
30 % a 59 %	📚 Buen estudiante
60 % a 89 %	🎤 Súper hablador
90 % o más	🏅 ¡Campeón del inglés!
🛠️ Solución de problemas
Problema	Qué hacer
can't open file ...	Revisa el nombre exacto del archivo con dir (Windows) o ls (Mac y Linux) y ejecuta ese nombre.
pip no se reconoce	Usa python -m pip install ...
No te entiende nunca	Revisa tu internet, habla cerca del micrófono y en un lugar sin ruido.
Error de micrófono	Comprueba que esté conectado y que Windows permita su uso. En Linux instala libportaudio2.
Error con googletrans	Ignóralo: el juego usa el diccionario de respaldo.
📁 Archivos
habla_correcto_ninos.py     El juego completo (un solo archivo)
record_habla_ninos.json     Se crea solo; guarda el récord
🧰 Tecnologías
Python
tkinter para la interfaz gráfica
sounddevice y scipy para grabar audio
SpeechRecognition para reconocer la voz
googletrans para traducir
👥 Equipo
[Tu nombre]: lógica del juego (puntos, rachas, niveles, fin del juego y récord)
Xabi: grabación de voz, reconocimiento y traducción
Belén: interfaz gráfica para niños
📝 Notas
Los sonidos de acierto y error solo suenan en Windows.
El reconocimiento de voz usa un servicio de Google, por eso necesita internet.
