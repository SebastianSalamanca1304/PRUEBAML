# PRUEBAML

Breve descripción del proyecto. Explica qué problema resuelve, para quién está pensado y cuál es su objetivo principal.

## Características
- Funcionalidad 1.
- Funcionalidad 2.
- Funcionalidad 3.

## Tecnologías utilizadas
- Python
- [Framework principal]
- [Base de datos]
- Docker
- Otras librerías relevantes

## Requisitos previos
- Python 3.x
- pip
- Git
- Docker y Docker Compose (si aplica)

## Instalación
```bash
git clone https://github.com/SebastianSalamanca1304/PRUEBAML.git
cd PRUEBAML
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuración
Crea un archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Agrega las variables de entorno necesarias en `.env`.

## Ejecución
Ejemplo:

```bash
python app.py
```

O si usas Docker:

```bash
docker compose up --build
```

## Uso
Explica cómo usar el sistema paso a paso:
1. Inicia la aplicación.
2. Accede a la ruta principal o interfaz.
3. Carga los datos o ejecuta la acción principal.
4. Revisa los resultados.

## Estructura del proyecto
```bash
PRUEBAML/
├───app
│   ├───chat
│   │   └───__pycache__
│   ├───rag
│   │   └───__pycache__
│   ├───scraper
│   └───__pycache__
├───chromadb
├───data
│   ├───chat_history
│   ├───chroma
│   │   └───66a7c6dd-9854-438e-a022-b5f24121753b
│   ├───clean
│   ├───processed
│   └───raw
├───logs
└───storage
```

## Variables de entorno
Ejemplo:

```env
OPENAI_API_KEY=tu_api_key_aqui
ENV=development
PORT=8000
```

Nunca subas el archivo `.env` real al repositorio.

## Seguridad
- El archivo `.env` está excluido del repositorio mediante `.gitignore`.
- Las credenciales sensibles deben mantenerse fuera del control de versiones.
- Usa `.env.example` para documentar las variables necesarias.

## Problemas encontrados y solución aplicada
Durante el proceso de subida al repositorio, GitHub bloqueó el push por detección de secretos en el historial de commits. Se corrigió eliminando el archivo sensible del control de versiones y evitando subir credenciales reales al repositorio, en línea con la protección de secretos de GitHub [web:564][web:566].

## Próximas mejoras
- Mejora 1.
- Mejora 2.
- Mejora 3.

## Contribución
1. Haz un fork del repositorio.
2. Crea una rama nueva.
3. Realiza tus cambios.
4. Envía un pull request.

## Licencia
Indica aquí la licencia del proyecto, por ejemplo MIT.
