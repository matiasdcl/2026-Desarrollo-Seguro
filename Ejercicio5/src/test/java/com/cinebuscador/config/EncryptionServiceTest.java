package com.cinebuscador.config;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

/**
 * Ejercicio 5 - Almacenamiento inseguro de contrasenas (CWE-257 / CWE-312).
 *
 * El mismo test corre en las dos ramas. Usa reflection porque la API de
 * EncryptionService cambia entre ramas (main: encrypt/decrypt; practico-2: hash/matches).
 * En main falla; en practico-2 pasa.
 */
class EncryptionServiceTest {

    private static boolean tieneMetodo(String nombre) {
        for (Method m : EncryptionService.class.getDeclaredMethods()) {
            if (m.getName().equals(nombre)) {
                return true;
            }
        }
        return false;
    }

    @Test
    void elAlmacenamientoNoEsReversible() {
        // Poder descifrar la contrasena guardada es la vulnerabilidad: main expone
        // decrypt() y la clave embebida; practico-2 (BCrypt) no tiene nada de eso.
        assertFalse(tieneMetodo("decrypt"), "No debe poder descifrarse la contrasena guardada");
        assertFalse(tieneMetodo("getStaticKey"), "No debe exponerse la clave de cifrado");
        assertFalse(tieneMetodo("getKeyBytes"), "No debe exponerse la clave de cifrado");
        assertFalse(tieneMetodo("getKeyHex"), "No debe exponerse la clave de cifrado");
    }

    @Test
    void elHashEsSalteadoYVerificable() throws Exception {
        // La version segura guarda un hash de una via, con sal, y verificable.
        Method hash;
        Method matches;
        try {
            hash = EncryptionService.class.getMethod("hash", String.class);
            matches = EncryptionService.class.getMethod("matches", String.class, String.class);
        } catch (NoSuchMethodException e) {
            fail("No existe hash()/matches(): el almacenamiento no usa hashing");
            return;
        }

        String clave = "Secreta123";
        String h1 = (String) hash.invoke(null, clave);
        String h2 = (String) hash.invoke(null, clave);

        assertNotEquals(clave, h1, "El hash no debe ser la contrasena en texto plano");
        assertNotEquals(h1, h2, "Dos hashes de la misma clave deben diferir (por la sal)");
        assertTrue((boolean) matches.invoke(null, clave, h1), "matches debe validar la clave correcta");
        assertFalse((boolean) matches.invoke(null, "otra", h1), "matches debe rechazar una clave incorrecta");
    }
}
