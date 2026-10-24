"""Ejercicio 1 - SQL Injection (CWE-89). Tests unitarios sobre buscar_funciones().

En main fallan (la inyeccion funciona). En practico-2 pasan (la inyeccion se bloquea).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import init_db  # noqa: E402
from app import app, buscar_funciones  # noqa: E402

TOTAL_FUNCIONES = 21


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    """Base temporal con los datos de init_db.py, para no pisar cine.db."""
    monkeypatch.setattr(init_db, "__file__", str(tmp_path / "init_db.py"))
    init_db.init_db()
    app.config["DATABASE"] = str(tmp_path / "cine.db")
    with app.app_context():
        yield


def test_busqueda_normal_funciona(ctx):
    """Control: buscar "Dune" devuelve sus 3 funciones en las dos ramas."""
    resultados = buscar_funciones("Dune")
    assert len(resultados) == 3
    assert all(r["pelicula"] == "Dune: Parte Dos" for r in resultados)


def test_or_1_igual_1_no_devuelve_todo(ctx):
    """Manda ' OR '1'='1; en main devuelve todas las funciones, en practico-2 ninguna."""
    resultados = buscar_funciones("' OR '1'='1")
    assert len(resultados) == 0


def test_union_no_filtra_esquema_de_la_base(ctx):
    """Manda un UNION contra sqlite_master; en main muestra los CREATE TABLE, en practico-2 nada."""
    payload = "' UNION SELECT name, sql, 1 FROM sqlite_master --"
    resultados = buscar_funciones(payload)
    textos = " ".join(str(v) for r in resultados for v in tuple(r))
    assert "CREATE TABLE" not in textos
    assert len(resultados) == 0


def test_order_by_no_acepta_sql_en_sentido(ctx):
    """Manda sentido="ASC LIMIT 1"; en main corta a 1 fila, en practico-2 vuelven todas."""
    resultados = buscar_funciones("", sort_by="nombre", sort_dir="ASC LIMIT 1")
    assert len(resultados) == TOTAL_FUNCIONES
