package com.booster.booster.dto;

import lombok.Getter;
import lombok.Setter;

public class LoginResponseDto {
    private String token;
    private long expiresIn;

    public void setExpiresIn(long expiresIn) {
        this.expiresIn = expiresIn;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public long getExpiresIn() {
        return expiresIn;
    }

    public String getToken() {
        return token;
    }
}
