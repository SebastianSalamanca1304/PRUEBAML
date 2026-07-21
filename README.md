# PRUEBAML

PRUEBAML es una solución basada en arquitectura **RAG** (*Retrieval-Augmented Generation*) para consultar información documental relacionada con Bancolombia. El proyecto permite extraer, limpiar, indexar y consultar contenido no estructurado para generar respuestas contextualizadas a partir de una base de conocimiento vectorial.

Su propósito es facilitar la búsqueda y análisis de información documental mediante una tubería que integra ingesta de datos, procesamiento, almacenamiento semántico e interacción conversacional. Este enfoque es coherente con casos de automatización documental y análisis de información no estructurada en contextos como Bancolombia [web:587][web:606].

## Tabla de contenido

- [Descripción](#descripción)
- [Objetivo](#objetivo)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Flujo de trabajo](#flujo-de-trabajo)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución local](#ejecución-local)
- [Ejecución con Docker](#ejecución-con-docker)
- [Persistencia de datos](#persistencia-de-datos)
- [Seguridad](#seguridad)
- [Mejoras futuras](#mejoras-futuras)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Descripción

El proyecto implementa un pipeline RAG para responder preguntas sobre documentos asociados al dominio bancario. La solución toma documentos fuente, los transforma en fragmentos consultables, los indexa en una base vectorial y utiliza ese contexto para producir respuestas más precisas.

Además, el sistema separa claramente la lógica de scraping, indexación y chat, lo que mejora la mantenibilidad y facilita futuras extensiones del proyecto.

## Objetivo

El objetivo principal de PRUEBAML es construir una base de conocimiento consultable que permita:

- Extraer información desde fuentes documentales.
- Limpiar y estructurar los datos obtenidos.
- Indexar el contenido en una base vectorial.
- Recuperar contexto relevante según la consulta del usuario.
- Generar respuestas fundamentadas en documentos previamente procesados.

## Arquitectura

La solución está dividida en tres componentes principales:

- **Scraper:** obtiene o extrae documentos y datos desde fuentes definidas.
- **RAG:** procesa, fragmenta, indexa y recupera información relevante.
- **Chat:** gestiona la interacción del usuario con el sistema y el historial de conversación.

Esta organización modular es consistente con buenas prácticas de documentación de proyectos, donde conviene explicar claramente las responsabilidades de cada parte del sistema y el modo de ejecución [web:621][web:627].

## Estructura del proyecto

```bash
PRUEBAML/
│   .dockerignore.txt
│   .gitignore
│   docker-compose.yml
│   Dockerfile
│   extraction.py
│   main.py
│   README.md
│   requirements.txt
│
├── app/
│   │   __init__.py
│   │
│   ├── chat/
│   │   │   chat_history.py
│   │   │   __init__.py
│   │
│   ├── rag/
│   │   │   indexer.py
│   │   │   rag_service.py
│   │   │   __init__.py
│   │
│   ├── scraper/
│   │   │   extractor.py
│   │
├── chromadb/
├── data/
│   ├── chat_history/
│   │   └── chat_history.db
│   ├── chroma/
│   │   ├── chroma.sqlite3
│   │   └── 66a7c6dd-9854-438e-a022-b5f24121753b/
│   ├── clean/
│   ├── processed/
│   └── raw/
├── logs/
└── storage/
```

## Descripción de archivos y carpetas

### Archivos raíz

- `main.py`: punto de entrada principal de la aplicación.
- `extraction.py`: script auxiliar para procesos de extracción.
- `requirements.txt`: dependencias del proyecto.
- `Dockerfile`: definición de imagen para contenerización.
- `docker-compose.yml`: orquestación de servicios del proyecto.
- `.gitignore`: exclusión de archivos que no deben versionarse.
- `.dockerignore.txt`: exclusión de archivos innecesarios en el build de Docker.
- `README.md`: documentación principal del repositorio.

### Módulo `app/`

#### `app/chat/`
Contiene la lógica relacionada con la conversación y el historial de interacciones.

- `chat_history.py`: manejo de historial del chat.
- `__init__.py`: inicialización del paquete.

#### `app/rag/`
Contiene el núcleo del pipeline RAG.

- `indexer.py`: indexación, fragmentación o carga de datos a la base vectorial.
- `rag_service.py`: servicio principal de recuperación y generación.
- `__init__.py`: inicialización del paquete.

#### `app/scraper/`
Contiene la lógica de extracción de datos desde fuentes externas.

- `extractor.py`: módulo principal de scraping o extracción documental.

### Carpeta `data/`

Organiza la información según su etapa dentro del pipeline:

- `data/raw/`: datos originales o documentos sin procesar.
- `data/clean/`: datos limpios y normalizados.
- `data/processed/`: datos listos para indexación o consumo por el sistema.
- `data/chroma/`: persistencia de la base vectorial.
- `data/chat_history/`: historial persistente de conversaciones, incluyendo `chat_history.db`.

### Otras carpetas

- `chromadb/`: directorio relacionado con la infraestructura o configuración local de ChromaDB.
- `logs/`: registros del sistema para monitoreo y depuración.
- `storage/`: almacenamiento auxiliar para artefactos del proyecto.

## Flujo de trabajo

El funcionamiento general del sistema puede resumirse así:

1. **Extracción**
   - Se obtienen documentos o datos desde una fuente definida.
   - La información inicial se almacena en `data/raw/`.

2. **Limpieza**
   - Los datos se normalizan y se preparan para el procesamiento.
   - El resultado se guarda en `data/clean/`.

3. **Procesamiento**
   - Los documentos se convierten en una estructura útil para indexación.
   - Los datos transformados se almacenan en `data/processed/`.

4. **Indexación**
   - Se generan embeddings sobre fragmentos del contenido.
   - Estos embeddings se almacenan en ChromaDB dentro de `data/chroma/`.

5. **Consulta**
   - El usuario realiza una pregunta.
   - El sistema recupera los fragmentos más relevantes desde la base vectorial.

6. **Respuesta**
   - El módulo RAG usa el contexto recuperado para generar una respuesta.

7. **Historial**
   - La conversación puede registrarse en `data/chat_history/chat_history.db`.

## Requisitos previos

Para ejecutar el proyecto localmente, se recomienda contar con:

- Python 3.10 o superior.
- `pip`.
- Git.
- Docker y Docker Compose, si se va a ejecutar en contenedores.
- Archivo `.env` configurado con las variables necesarias.

Los READMEs más útiles suelen incluir requisitos, instalación, configuración y ejemplos listos para copiar y pegar, porque eso reduce la fricción para poner en marcha el proyecto [web:591][web:627].

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/SebastianSalamanca1304/PRUEBAML.git
cd PRUEBAML
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` local con las variables de entorno necesarias. Si tienes un `.env.example`, úsalo como base.

Ejemplo:

```env
OPENAI_API_KEY=tu_api_key
CHROMA_PATH=./data/chroma
RAW_DATA_PATH=./data/raw
CLEAN_DATA_PATH=./data/clean
PROCESSED_DATA_PATH=./data/processed
CHAT_HISTORY_PATH=./data/chat_history/chat_history.db
LOGS_PATH=./logs
```

> Nunca subas el archivo `.env` real al repositorio.

## Ejecución local

Como el proyecto incluye `main.py`, ese archivo debe documentarse como el punto de entrada principal salvo que exista otra convención interna más específica [web:587][web:621].

Ejecuta la aplicación con:

```bash
python main.py
```

Si necesitas correr primero la extracción, puedes documentar también un flujo como este:

```bash
python extraction.py
python main.py
```

## Ejecución con Docker

Dado que el repositorio incluye `Dockerfile` y `docker-compose.yml`, conviene documentar también la ejecución en contenedor, porque es una práctica esperada en proyectos que ya están preparados para ese flujo [web:618].

Construcción y arranque:

```bash
docker compose up --build
```

Si deseas ejecutar en segundo plano:

```bash
docker compose up -d --build
```

Para detener los contenedores:

```bash
docker compose down
```

## Persistencia de datos

El proyecto ya contempla persistencia en varios niveles:

- Base vectorial en `data/chroma/`.
- Historial de chat en `data/chat_history/chat_history.db`.
- Archivos de entrada en `data/raw/`.
- Archivos limpios en `data/clean/`.
- Logs de ejecución en `logs/`.

Esto ayuda a mantener trazabilidad, reproducibilidad y continuidad del sistema entre ejecuciones.

## Seguridad

Durante el desarrollo se presentó un bloqueo de GitHub Push Protection por detección de un secreto en el historial. GitHub bloquea pushes que contienen secretos detectados y recomienda eliminar el secreto del historial o resolver la excepción de forma explícita [web:564][web:566].

Por eso, en este proyecto se deben seguir estas prácticas:

- Mantener `.env` fuera del control de versiones.
- Incluir `.env` en `.gitignore`.
- Subir solo `.env.example` sin valores reales.
- Revocar y regenerar cualquier clave que haya quedado expuesta.
- Verificar el historial antes de hacer push si hubo archivos sensibles.

## Mejoras futuras

- Agregar evaluación automática de respuestas del RAG.
- Implementar trazabilidad de fuentes por respuesta.
- Mejorar el pipeline de limpieza y normalización.
- Incorporar más fuentes documentales.
- Añadir interfaz web para consulta.
- Implementar autenticación y control de acceso.
- Añadir pruebas automatizadas.

## Contribución

Para contribuir al proyecto:

1. Haz un fork del repositorio.
2. Crea una rama para tu cambio.
3. Realiza tus modificaciones.
4. Ejecuta pruebas o validaciones necesarias.
5. Envía un pull request con una descripción clara del cambio.

## Licencia

Definir la licencia del proyecto según el uso esperado del repositorio, por ejemplo MIT o Apache 2.0.
