"""Ejercicio 4 - SSTI / inyeccion SpEL (CWE-94). Tests de integracion.

Necesitan la app levantada con Docker (docker compose up -d --build) en http://localhost:8080.
En main fallan (lo que se busca se evalua como expresion SpEL). En practico-2 pasan (no se evalua).
"""
import os

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="module", autouse=True)
def app_levantada():
    """Corta con un mensaje claro si la app no esta corriendo."""
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.ConnectionError:
        pytest.exit(f"La app no responde en {BASE_URL}. Levantala con docker compose up -d --build")


def buscar(expresion):
    """Manda la expresion por el buscador (GET /?buscar=...) y devuelve el HTML de la respuesta."""
    return requests.get(BASE_URL, params={"buscar": expresion}, timeout=10).text


def test_home_lista_funciones():
    """Control: la home sin busqueda lista las funciones en las dos ramas."""
    html = requests.get(BASE_URL, timeout=10).text
    assert "Inception" in html


@pytest.mark.parametrize(
    "expresion, resultado",
    [
        ("7*7", "49"),
        ("6*8", "48"),
    ],
    ids=["por_49", "por_48"],
)
def test_expresion_spel_no_se_evalua(expresion, resultado):
    """Manda una operacion aritmetica; en main la app devuelve el resultado calculado, en practico-2 no."""
    html = buscar(expresion)
    assert resultado not in html
