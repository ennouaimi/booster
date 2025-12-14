package com.booster.booster.auth;

import com.booster.booster.repository.UserRepository;
import jakarta.validation.constraints.NotNull;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class BooUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    @Autowired
    public BooUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(@NotNull String email) throws UsernameNotFoundException {
        return userRepository.findByUsername(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));
    }
}

