"""Ejercicio 2 - XSS almacenado (CWE-79). Tests unitarios sobre el template edit.html.

En main fallan (la descripcion se muestra sin escapar). En practico-2 pasan (Jinja la escapa).
"""
import os
import sys

import pytest
from flask import render_template

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402


def renderizar_edit(descripcion):
    """Renderiza edit.html con una pelicula de prueba que tiene la descripcion dada."""
    pelicula = {
        "id": 1,
        "nombre": "Pelicula de prueba",
        "genero": "Drama",
        "director": "Alguien",
        "descripcion": descripcion,
    }
    with app.test_request_context():
        return render_template("edit.html", pelicula=pelicula)


def test_descripcion_normal_se_muestra():
    """Control: una descripcion comun aparece en la pagina en las dos ramas."""
    html = renderizar_edit("Una pelicula sobre el desierto.")
    assert "Una pelicula sobre el desierto." in html


@pytest.mark.parametrize(
    "payload, escapado",
    [
        ("<script>alert(1)</script>", "&lt;script&gt;alert(1)&lt;/script&gt;"),
        ("<img src=x onerror=alert(1)>", "&lt;img src=x onerror=alert(1)&gt;"),
    ],
    ids=["script", "img_onerror"],
)
def test_descripcion_maliciosa_se_escapa(payload, escapado):
    """Guarda HTML en la descripcion; en main sale tal cual, en practico-2 sale escapado."""
    html = renderizar_edit(payload)
    assert payload not in html
    assert escapado in html
