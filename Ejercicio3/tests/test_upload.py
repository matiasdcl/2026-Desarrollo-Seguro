"""Ejercicio 3 - Path Traversal en la subida de archivos (CWE-22). Tests de integracion.

Necesitan la app levantada con Docker (docker compose up -d --build) en http://localhost:8080.
En main fallan (el archivo se escribe fuera de /uploads). En practico-2 pasan (queda adentro).
"""
import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
PELICULA_ID = 1


@pytest.fixture(scope="module", autouse=True)
def app_levantada():
    """Corta con un mensaje claro si la app no esta corriendo."""
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.ConnectionError:
        pytest.exit(f"La app no responde en {BASE_URL}. Levantala con docker compose up -d --build")


def subir(nombre, contenido):
    """Sube un archivo como afiche de la pelicula 1, igual que el formulario de /upload/1."""
    archivos = {"afiche": (nombre, contenido, "application/octet-stream")}
    return requests.post(f"{BASE_URL}/upload/{PELICULA_ID}", files=archivos, allow_redirects=False, timeout=10)


def test_upload_normal_funciona():
    """Control: un archivo con nombre comun se sube y se puede descargar en las dos ramas."""
    nombre = f"afiche-{uuid.uuid4().hex}.png"
    contenido = b"imagen de prueba"
    assert subir(nombre, contenido).status_code == 302
    respuesta = requests.get(f"{BASE_URL}/uploads/{nombre}", timeout=10)
    assert respuesta.status_code == 200
    assert respuesta.content == contenido


@pytest.mark.parametrize("prefijo", ["../", "../../../../tmp/"], ids=["un_nivel", "hasta_tmp"])
def test_nombre_con_traversal_queda_dentro_de_uploads(prefijo):
    """Sube un archivo con ../ en el nombre; en main se escribe fuera de /uploads, en practico-2 queda adentro."""
    nombre = f"traversal-{uuid.uuid4().hex}.txt"
    contenido = b"archivo del atacante"
    subir(prefijo + nombre, contenido)
    respuesta = requests.get(f"{BASE_URL}/uploads/{nombre}", timeout=10)
    assert respuesta.status_code == 200
    assert respuesta.content == contenido
