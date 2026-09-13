package com.cinebuscador.config;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class EncryptionService {

    private static final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    public static String hash(String plaintext) {
        return encoder.encode(plaintext);
    }

    public static boolean matches(String plaintext, String hash) {
        return encoder.matches(plaintext, hash);
    }
}