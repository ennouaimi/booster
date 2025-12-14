package com.booster.booster.errors;

public class BooInvalidParametersException extends RuntimeException {
    public BooInvalidParametersException(String username) {
        super("Invalid parameters : " + username);
    }
}
