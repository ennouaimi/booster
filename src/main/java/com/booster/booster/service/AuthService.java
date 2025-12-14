package com.booster.booster.service;

import com.booster.booster.dto.LoginUserDto;
import com.booster.booster.dto.RegisterUserDto;
import com.booster.booster.entity.User;
import com.booster.booster.errors.BooInvalidParametersException;
import com.booster.booster.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, AuthenticationManager authenticationManager) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
    }

    public User signup(RegisterUserDto input) {
        if (userRepository.existsByUsername(input.getUsername())) {
            throw new BooInvalidParametersException("Username already exists");
        }

        User user = new User();
        user.setUsername(input.getUsername());
        user.setPassword(passwordEncoder.encode(input.getPassword()));

        return userRepository.save(user);
    }


        public User authenticate(LoginUserDto input) {
        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            input.getUsername(),
                            input.getPassword()
                    )
            );
        } catch (AuthenticationException ex) {
            log.error("Authentication failed for user {}: {}", input.getUsername(), ex.getMessage());
            throw new RuntimeException("Athentification Exception : ", ex);
        }

        return userRepository.findByUsername(input.getUsername())
                .orElseThrow();
        }
}