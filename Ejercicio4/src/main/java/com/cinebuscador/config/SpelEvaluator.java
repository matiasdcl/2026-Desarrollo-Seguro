package com.cinebuscador.config;

import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.SimpleEvaluationContext;
import org.springframework.stereotype.Component;

@Component
public class SpelEvaluator {

    public String evaluate(String expression) {
        if (expression == null || expression.isBlank()) {
            return "";
        }

        // Solo se permiten literales de texto: cualquier otro caracter de SpEL
        // (paréntesis, puntos, T(), etc.) se rechaza directamente.
        if (!expression.matches("^[\\p{L}0-9 ]*$")) {
            return "";
        }

        ExpressionParser parser = new SpelExpressionParser();

        // SimpleEvaluationContext no permite invocar clases arbitrarias (T(...)),
        // constructores, ni acceder a beans o variables del sistema.
        org.springframework.expression.EvaluationContext context =
            SimpleEvaluationContext.forReadOnlyDataBinding().build();

        var expr = parser.parseExpression(expression);
        Object result = expr.getValue(context);

        return result != null ? result.toString() : "";
    }
}