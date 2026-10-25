# Pruebas de seguridad (Practico 4)

Este repositorio tiene pruebas de seguridad para las 5 vulnerabilidades que se mitigaron en el Practico 2. Las mismas pruebas corren en dos ramas:

- `main`: codigo vulnerable. Las pruebas fallan.
- `practico-2`: codigo mitigado. Las pruebas pasan.

Cada prueba intenta explotar la vulnerabilidad. Por eso funcionan como pruebas de regresion: si alguien vuelve a introducir el fallo, la prueba se pone en rojo.

Para cambiar entre las dos versiones del codigo:

```
git checkout main          # codigo vulnerable
git checkout practico-2    # codigo mitigado
```

## Requisitos

- Python 3 (ejercicios 1 a 4)
- Docker (ejercicios 3, 4 y 5)

Entorno de Python, desde la raiz del repositorio:

```
python3 -m venv .venv
source .venv/bin/activate
pip install flask==3.0.0 pytest requests
```

## Resumen

| # | Vulnerabilidad | Tipo | Herramienta |
|---|---|---|---|
| 1 | SQL Injection | Unitaria | pytest |
| 2 | XSS almacenado | Unitaria | pytest |
| 3 | File Upload (Path Traversal) | Integracion | Docker + pytest |
| 4 | SSTI (SpEL) | Integracion | Docker + pytest |
| 5 | Almacenamiento inseguro de contrasenas | Unitaria | JUnit (Maven) |

## Ejercicio 1 - SQL Injection

Prueba unitaria sobre la funcion de busqueda.

```
cd Ejercicio1
python -m pytest tests/ -v
```

Resultado esperado: en `practico-2` pasan las 4; en `main` fallan 3 (pasa solo la de control).

## Ejercicio 2 - XSS almacenado

Prueba unitaria sobre el template que muestra la descripcion de la pelicula.

```
cd Ejercicio2
python -m pytest tests/ -v
```

Resultado esperado: en `practico-2` pasan las 3; en `main` fallan 2 (pasa solo la de control).

## Ejercicio 3 - File Upload (Path Traversal)

Prueba de integracion: levanta la app con Docker y le pega por HTTP.

```
cd Ejercicio3
docker compose up -d --build
docker logs -f cinebuscador3     # esperar "Started CineBuscadorApplication" y salir con Ctrl+C
python -m pytest tests/ -v
docker compose down
```

Resultado esperado: en `practico-2` pasan las 3; en `main` fallan 2 (pasa solo la de control).

Nota: al cambiar de rama hay que levantar con `--build`, porque la imagen tiene compilado el codigo de la rama anterior.

## Ejercicio 4 - SSTI (SpEL)

Prueba de integracion, igual que el 3. Usa el mismo puerto 8080, asi que si quedo levantado el del Ejercicio 3 hay que bajarlo antes (`docker compose down`).

```
cd Ejercicio4
docker compose up -d --build
docker logs -f cinebuscador4     # esperar "Started CineBuscadorApplication" y salir con Ctrl+C
python -m pytest tests/ -v
docker compose down
```

Resultado esperado: en `practico-2` pasan las 3; en `main` fallan 2 (pasa solo la de control).

## Ejercicio 5 - Almacenamiento inseguro de contrasenas

Prueba unitaria con JUnit. No necesita levantar la app; se corre con una imagen de Maven en Docker. Desde la raiz del repositorio:

```
docker run --rm -v "$PWD/Ejercicio5":/app -v "$HOME/.m2":/root/.m2 -w /app maven:3.9.11-eclipse-temurin-21 mvn test
```

Resultado esperado: en `practico-2` termina en `BUILD SUCCESS` (2 pruebas pasan); en `main` termina en `BUILD FAILURE` (2 pruebas fallan).
