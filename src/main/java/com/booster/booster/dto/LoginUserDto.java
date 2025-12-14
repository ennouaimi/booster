package com.booster.booster.dto;

import lombok.Getter;

public class LoginUserDto {
    private String username;
    private String password;

    public String getPassword() {
        return password;
    }

    public String getUsername() {
        return username;
    }
}
