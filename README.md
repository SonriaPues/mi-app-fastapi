# 📚 Book Hub

Catálogo colaborativo de libros donde los usuarios pueden explorar, guardar favoritos y reseñar libros.

## Stack

- **Backend:** Python 3.11+ / FastAPI
- **Base de datos:** MongoDB Atlas (motor async)
- **Frontend:** Jinja2 + CSS + JS
- **Auth:** JWT en cookies HttpOnly + bcrypt

## Instalación local

### 1. Clonar y crear entorno virtual

```bash
git clone <tu-repo>
cd book-hub
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar MongoDB Atlas

1. Crear cuenta gratuita en [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Crear un cluster gratuito (M0)
3. Crear un usuario de base de datos
4. Agregar tu IP a la whitelist (o `0.0.0.0/0` para desarrollo)
5. Copiar el connection string

### 3. Configurar variables de entorno

```bash
copy .env.example .env
```

Editar `.env` con tu connection string y contraseña del admin:

```
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/bookhub
ADMIN_USERNAME=admin
ADMIN_PASSWORD=TuPasswordSegura123
JWT_SECRET_KEY=una-clave-secreta-larga-aleatoria
```

### 4. Ejecutar seed

```bash
python scripts/seed_database.py
```

Esto crea el usuario admin y carga 20 libros clásicos.

### 5. Levantar la aplicación

```bash
uvicorn app.main:app --reload
```

Abre http://localhost:8000

- **Admin:** el usuario configurado en `.env`
- **Docs API:** http://localhost:8000/docs

## Despliegue en Render

1. Crear un nuevo Web Service en Render
2. Conectar tu repositorio
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Agregar variables de entorno (las del `.env`)
6. Ejecutar seed: `python scripts/seed_database.py`

## Estructura del proyecto

```
book-hub/
├── app/
│   ├── main.py          # Punto de entrada FastAPI
│   ├── config.py         # Settings desde .env
│   ├── database.py       # Conexión MongoDB
│   ├── auth/jwt.py       # JWT + bcrypt
│   ├── models/           # Modelos Pydantic
│   ├── routes/           # Auth, Books, Admin, API
│   ├── templates/        # Jinja2 HTML
│   └── static/           # CSS, JS, imágenes
├── scripts/
│   ├── seed_books.json
│   ├── seed_database.py
│   └── fetch_open_library.py
├── requirements.txt
├── .env.example
└── Procfile
```
