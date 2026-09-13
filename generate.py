#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from textwrap import dedent

DEFAULTS = {
    "name": "demo-service",
    "group": "com.example",
    "package": "com.example.demo",
    "description": "Generated with Booster",
    "java": 21,
    "port": 8080,
    "database": "postgres",
    "flyway": True,
    "security": "jwt",
    "cors_origins": ["http://localhost:3000"],
    "public_paths": ["/api/auth/**", "/actuator/health", "/swagger-ui/**", "/v3/api-docs/**"],
    "swagger": True,
    "actuator": True,
    "rate_limit": True,
    "rate_limit_requests_per_minute": 120,
    "docker": True,
    "testcontainers": True,
}


def java_class(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    value = "".join(p[:1].upper() + p[1:] for p in parts if p)
    if not value or value[0].isdigit():
        value = "Generated" + value
    return value


def artifact(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-") or "app"


def package_path(package: str) -> str:
    return package.replace(".", "/")


def write(root: Path, rel: str, content: str):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def pom(cfg):
    deps = [
        """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>""",
        """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>""",
        """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>""",
    ]
    if cfg["database"] == "postgres":
        deps.append("""<dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>""")
    else:
        deps.append("""<dependency><groupId>com.h2database</groupId><artifactId>h2</artifactId><scope>runtime</scope></dependency>""")
    if cfg["flyway"]:
        deps.append("""<dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>""")
        if cfg["database"] == "postgres":
            deps.append("""<dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>""")
    if cfg["security"] == "jwt":
        deps += [
            """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-security</artifactId></dependency>""",
            """<dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-api</artifactId><version>0.12.6</version></dependency>""",
            """<dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-impl</artifactId><version>0.12.6</version><scope>runtime</scope></dependency>""",
            """<dependency><groupId>io.jsonwebtoken</groupId><artifactId>jjwt-jackson</artifactId><version>0.12.6</version><scope>runtime</scope></dependency>""",
        ]
    if cfg["swagger"]:
        deps.append("""<dependency><groupId>org.springdoc</groupId><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId><version>2.8.14</version></dependency>""")
    if cfg["actuator"]:
        deps += [
            """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>""",
            """<dependency><groupId>io.micrometer</groupId><artifactId>micrometer-core</artifactId></dependency>""",
        ]
    if cfg["rate_limit"]:
        deps.append("""<dependency><groupId>com.bucket4j</groupId><artifactId>bucket4j-core</artifactId><version>8.10.1</version></dependency>""")
    deps += [
        """<dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><optional>true</optional></dependency>""",
        """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-test</artifactId><scope>test</scope></dependency>""",
    ]
    if cfg["testcontainers"] and cfg["database"] == "postgres":
        deps += [
            """<dependency><groupId>org.testcontainers</groupId><artifactId>postgresql</artifactId><scope>test</scope></dependency>""",
            """<dependency><groupId>org.testcontainers</groupId><artifactId>junit-jupiter</artifactId><scope>test</scope></dependency>""",
            """<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-testcontainers</artifactId><scope>test</scope></dependency>""",
        ]
    dep_xml = "\n        ".join(deps)
    return f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>
      <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.8</version>
        <relativePath/>
      </parent>
      <groupId>{cfg['group']}</groupId>
      <artifactId>{artifact(cfg['name'])}</artifactId>
      <version>0.0.1-SNAPSHOT</version>
      <name>{artifact(cfg['name'])}</name>
      <description>{cfg['description']}</description>
      <properties><java.version>{cfg['java']}</java.version></properties>
      <dependencies>
        {dep_xml}
      </dependencies>
      <build><plugins>
        <plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin>
      </plugins></build>
    </project>
    """


def application_yml(cfg):
    lines = [f"server:\n  port: ${{PORT:{cfg['port']}}}\n  forward-headers-strategy: framework", "spring:"]
    if cfg["database"] == "postgres":
        lines.append("""  datasource:
    url: jdbc:postgresql://${PGHOST:localhost}:${PGPORT:5432}/${PGDATABASE:app}
    username: ${PGUSER:app}
    password: ${PGPASSWORD:app}
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false""")
    else:
        lines.append("""  datasource:
    url: jdbc:h2:mem:app;MODE=PostgreSQL
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: update
    open-in-view: false""")
    if cfg["flyway"]:
        lines.append("  flyway:\n    enabled: true")
    if cfg["security"] == "jwt":
        lines.append("""security:
  jwt:
    secret-key: ${JWT_SECRET:change-me-change-me-change-me-change-me}
    expiration-time: ${JWT_EXPIRATION_MS:86400000}""")
    if cfg["swagger"]:
        lines.append("""springdoc:
  api-docs:
    enabled: ${SWAGGER_ENABLED:true}
  swagger-ui:
    enabled: ${SWAGGER_ENABLED:true}""")
    if cfg["actuator"]:
        lines.append("""management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      probes:
        enabled: true
      show-details: never""")
    if cfg["rate_limit"]:
        lines.append(f"""app:
  rate-limit:
    requests-per-minute: ${{RATE_LIMIT_RPM:{cfg['rate_limit_requests_per_minute']}}}""")
    return "\n\n".join(lines) + "\n"


def generate(cfg, out: Path):
    pkg = cfg["package"]
    pp = package_path(pkg)
    cls = java_class(cfg["name"])
    write(out, "pom.xml", pom(cfg))
    write(out, "src/main/resources/application.yml", application_yml(cfg))
    write(out, ".gitignore", """
    target/
    .idea/
    *.iml
    .env
    .DS_Store
    """)
    write(out, ".env.example", """
    PORT=8080
    PGHOST=localhost
    PGPORT=5432
    PGDATABASE=app
    PGUSER=app
    PGPASSWORD=app
    JWT_SECRET=replace-with-a-long-random-secret-at-least-32-bytes
    SWAGGER_ENABLED=true
    RATE_LIMIT_RPM=120
    """)
    write(out, f"src/main/java/{pp}/{cls}Application.java", f"""
    package {pkg};

    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;

    @SpringBootApplication
    public class {cls}Application {{
        public static void main(String[] args) {{ SpringApplication.run({cls}Application.class, args); }}
    }}
    """)
    write(out, f"src/main/java/{pp}/api/PingController.java", f"""
    package {pkg}.api;

    import java.util.Map;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RestController;

    @RestController
    public class PingController {{
        @GetMapping("/api/ping")
        public Map<String, String> ping() {{ return Map.of("status", "ok"); }}
    }}
    """)
    write(out, f"src/main/java/{pp}/error/ApiError.java", f"""
    package {pkg}.error;

    import java.time.Instant;

    public record ApiError(Instant timestamp, int status, String error, String message, String path) {{}}
    """)
    write(out, f"src/main/java/{pp}/error/GlobalExceptionHandler.java", f"""
    package {pkg}.error;

    import jakarta.servlet.http.HttpServletRequest;
    import java.time.Instant;
    import java.util.stream.Collectors;
    import org.springframework.http.HttpStatus;
    import org.springframework.http.ResponseEntity;
    import org.springframework.web.bind.MethodArgumentNotValidException;
    import org.springframework.web.bind.annotation.ExceptionHandler;
    import org.springframework.web.bind.annotation.RestControllerAdvice;

    @RestControllerAdvice
    public class GlobalExceptionHandler {{
        @ExceptionHandler(MethodArgumentNotValidException.class)
        ResponseEntity<ApiError> validation(MethodArgumentNotValidException ex, HttpServletRequest req) {{
            String message = ex.getBindingResult().getFieldErrors().stream()
                    .map(e -> e.getField() + ": " + e.getDefaultMessage()).collect(Collectors.joining(", "));
            return build(HttpStatus.BAD_REQUEST, message, req.getRequestURI());
        }}

        @ExceptionHandler(Exception.class)
        ResponseEntity<ApiError> unexpected(Exception ex, HttpServletRequest req) {{
            return build(HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected server error", req.getRequestURI());
        }}

        private ResponseEntity<ApiError> build(HttpStatus status, String message, String path) {{
            return ResponseEntity.status(status).body(new ApiError(Instant.now(), status.value(), status.getReasonPhrase(), message, path));
        }}
    }}
    """)

    if cfg["security"] == "jwt":
        write(out, f"src/main/java/{pp}/security/SecurityConfig.java", security_config(cfg, pkg))
        write(out, f"src/main/java/{pp}/security/JwtService.java", jwt_service(pkg))
        write(out, f"src/main/java/{pp}/security/JwtAuthenticationFilter.java", jwt_filter(pkg))
        write(out, f"src/main/java/{pp}/auth/User.java", user_entity(pkg))
        write(out, f"src/main/java/{pp}/auth/UserRepository.java", user_repo(pkg))
        write(out, f"src/main/java/{pp}/auth/AuthService.java", auth_service(pkg))
        write(out, f"src/main/java/{pp}/auth/AuthController.java", auth_controller(pkg))
        write(out, f"src/main/java/{pp}/auth/LoginRequest.java", login_request(pkg))
        write(out, f"src/main/java/{pp}/auth/RegisterRequest.java", register_request(pkg))
        write(out, f"src/main/java/{pp}/auth/AuthResponse.java", auth_response(pkg))
    if cfg["rate_limit"]:
        write(out, f"src/main/java/{pp}/security/RateLimitFilter.java", rate_limit_filter(pkg))
    if cfg["flyway"]:
        write(out, "src/main/resources/db/migration/V1__init.sql", init_sql(cfg))
    if cfg["docker"]:
        write(out, "Dockerfile", dockerfile())
        if cfg["database"] == "postgres":
            write(out, "docker-compose.yml", compose(cfg))
    write(out, f"src/test/java/{pp}/{cls}ApplicationTests.java", test_class(cfg, pkg, cls))
    write(out, "README.md", generated_readme(cfg))


def security_config(cfg, pkg):
    origins = ", ".join(f'"{x}"' for x in cfg["cors_origins"])
    public = ",\n                        ".join(f'"{x}"' for x in cfg["public_paths"])
    rate_dep = "private final RateLimitFilter rateLimitFilter;" if cfg["rate_limit"] else ""
    rate_chain = ".addFilterBefore(rateLimitFilter, UsernamePasswordAuthenticationFilter.class)" if cfg["rate_limit"] else ""
    return f"""
    package {pkg}.security;

    import java.util.List;
    import lombok.RequiredArgsConstructor;
    import org.springframework.context.annotation.Bean;
    import org.springframework.context.annotation.Configuration;
    import org.springframework.security.config.Customizer;
    import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
    import org.springframework.security.config.annotation.web.builders.HttpSecurity;
    import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
    import org.springframework.security.config.http.SessionCreationPolicy;
    import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
    import org.springframework.security.crypto.password.PasswordEncoder;
    import org.springframework.security.web.SecurityFilterChain;
    import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
    import org.springframework.web.cors.CorsConfiguration;
    import org.springframework.web.cors.CorsConfigurationSource;
    import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

    @Configuration
    @EnableMethodSecurity
    @RequiredArgsConstructor
    public class SecurityConfig {{
        private final JwtAuthenticationFilter jwtAuthenticationFilter;
        {rate_dep}

        @Bean
        SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {{
            http.csrf(AbstractHttpConfigurer::disable)
                .cors(Customizer.withDefaults())
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                    .requestMatchers(
                        {public}
                    ).permitAll()
                    .anyRequest().authenticated())
                {rate_chain}
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
            return http.build();
        }}

        @Bean PasswordEncoder passwordEncoder() {{ return new BCryptPasswordEncoder(); }}

        @Bean
        CorsConfigurationSource corsConfigurationSource() {{
            CorsConfiguration c = new CorsConfiguration();
            c.setAllowedOrigins(List.of({origins}));
            c.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
            c.setAllowedHeaders(List.of("*"));
            c.setAllowCredentials(true);
            UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
            source.registerCorsConfiguration("/**", c);
            return source;
        }}
    }}
    """


def jwt_service(pkg):
    return f"""
    package {pkg}.security;

    import io.jsonwebtoken.Claims;
    import io.jsonwebtoken.Jwts;
    import io.jsonwebtoken.security.Keys;
    import java.nio.charset.StandardCharsets;
    import java.util.Date;
    import javax.crypto.SecretKey;
    import org.springframework.beans.factory.annotation.Value;
    import org.springframework.stereotype.Service;

    @Service
    public class JwtService {{
        @Value("${{security.jwt.secret-key}}") private String secret;
        @Value("${{security.jwt.expiration-time}}") private long expiration;

        public String issue(String subject) {{
            Date now = new Date();
            return Jwts.builder().subject(subject).issuedAt(now).expiration(new Date(now.getTime() + expiration))
                    .signWith(key()).compact();
        }}
        public String subject(String token) {{ return claims(token).getSubject(); }}
        public boolean valid(String token) {{ return claims(token).getExpiration().after(new Date()); }}
        private Claims claims(String token) {{ return Jwts.parser().verifyWith(key()).build().parseSignedClaims(token).getPayload(); }}
        private SecretKey key() {{ return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)); }}
    }}
    """


def jwt_filter(pkg):
    return f"""
    package {pkg}.security;

    import {pkg}.auth.UserRepository;
    import jakarta.servlet.FilterChain;
    import jakarta.servlet.ServletException;
    import jakarta.servlet.http.HttpServletRequest;
    import jakarta.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import lombok.RequiredArgsConstructor;
    import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
    import org.springframework.security.core.context.SecurityContextHolder;
    import org.springframework.stereotype.Component;
    import org.springframework.web.filter.OncePerRequestFilter;

    @Component
    @RequiredArgsConstructor
    public class JwtAuthenticationFilter extends OncePerRequestFilter {{
        private final JwtService jwtService;
        private final UserRepository userRepository;

        @Override protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
                throws ServletException, IOException {{
            String header = request.getHeader("Authorization");
            if (header != null && header.startsWith("Bearer ") && SecurityContextHolder.getContext().getAuthentication() == null) {{
                try {{
                    String token = header.substring(7);
                    if (jwtService.valid(token)) {{
                        userRepository.findByEmailIgnoreCase(jwtService.subject(token)).ifPresent(user -> {{
                            var auth = new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
                            SecurityContextHolder.getContext().setAuthentication(auth);
                        }});
                    }}
                }} catch (RuntimeException ignored) {{ }}
            }}
            chain.doFilter(request, response);
        }}
    }}
    """


def user_entity(pkg):
    return f"""
    package {pkg}.auth;

    import jakarta.persistence.*;
    import java.util.Collection;
    import java.util.List;
    import lombok.*;
    import org.springframework.security.core.GrantedAuthority;
    import org.springframework.security.core.authority.SimpleGrantedAuthority;
    import org.springframework.security.core.userdetails.UserDetails;

    @Entity @Table(name = "app_user") @Getter @Setter @NoArgsConstructor
    public class User implements UserDetails {{
        @Id @GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
        @Column(nullable = false, unique = true) private String email;
        @Column(nullable = false) private String password;
        @Column(nullable = false) private String role = "USER";
        @Override public Collection<? extends GrantedAuthority> getAuthorities() {{ return List.of(new SimpleGrantedAuthority("ROLE_" + role)); }}
        @Override public String getUsername() {{ return email; }}
    }}
    """


def user_repo(pkg):
    return f"""
    package {pkg}.auth;
    import java.util.Optional;
    import org.springframework.data.jpa.repository.JpaRepository;
    public interface UserRepository extends JpaRepository<User, Long> {{ Optional<User> findByEmailIgnoreCase(String email); }}
    """


def auth_service(pkg):
    return f"""
    package {pkg}.auth;

    import {pkg}.security.JwtService;
    import lombok.RequiredArgsConstructor;
    import org.springframework.security.crypto.password.PasswordEncoder;
    import org.springframework.stereotype.Service;
    import org.springframework.transaction.annotation.Transactional;

    @Service @RequiredArgsConstructor
    public class AuthService {{
        private final UserRepository users;
        private final PasswordEncoder encoder;
        private final JwtService jwt;

        @Transactional
        public AuthResponse register(RegisterRequest request) {{
            if (users.findByEmailIgnoreCase(request.email()).isPresent()) throw new IllegalArgumentException("Email already used");
            User user = new User();
            user.setEmail(request.email().trim().toLowerCase());
            user.setPassword(encoder.encode(request.password()));
            users.save(user);
            return new AuthResponse(jwt.issue(user.getEmail()));
        }}

        public AuthResponse login(LoginRequest request) {{
            User user = users.findByEmailIgnoreCase(request.email()).orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));
            if (!encoder.matches(request.password(), user.getPassword())) throw new IllegalArgumentException("Invalid credentials");
            return new AuthResponse(jwt.issue(user.getEmail()));
        }}
    }}
    """


def auth_controller(pkg):
    return f"""
    package {pkg}.auth;

    import jakarta.validation.Valid;
    import lombok.RequiredArgsConstructor;
    import org.springframework.web.bind.annotation.*;

    @RestController @RequestMapping("/api/auth") @RequiredArgsConstructor
    public class AuthController {{
        private final AuthService authService;
        @PostMapping("/register") public AuthResponse register(@Valid @RequestBody RegisterRequest r) {{ return authService.register(r); }}
        @PostMapping("/login") public AuthResponse login(@Valid @RequestBody LoginRequest r) {{ return authService.login(r); }}
    }}
    """


def login_request(pkg):
    return f"""package {pkg}.auth;\nimport jakarta.validation.constraints.*;\npublic record LoginRequest(@Email @NotBlank String email, @NotBlank String password) {{}}\n"""


def register_request(pkg):
    return f"""package {pkg}.auth;\nimport jakarta.validation.constraints.*;\npublic record RegisterRequest(@Email @NotBlank String email, @Size(min=8,max=100) String password) {{}}\n"""


def auth_response(pkg):
    return f"""package {pkg}.auth;\npublic record AuthResponse(String token) {{}}\n"""


def rate_limit_filter(pkg):
    return f"""
    package {pkg}.security;

    import io.github.bucket4j.Bandwidth;
    import io.github.bucket4j.Bucket;
    import io.github.bucket4j.Refill;
    import jakarta.servlet.*;
    import jakarta.servlet.http.*;
    import java.io.IOException;
    import java.time.Duration;
    import java.util.concurrent.ConcurrentHashMap;
    import org.springframework.beans.factory.annotation.Value;
    import org.springframework.stereotype.Component;
    import org.springframework.web.filter.OncePerRequestFilter;

    @Component
    public class RateLimitFilter extends OncePerRequestFilter {{
        private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();
        @Value("${{app.rate-limit.requests-per-minute:120}}") private int rpm;

        @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
                throws ServletException, IOException {{
            String key = req.getRemoteAddr();
            Bucket bucket = buckets.computeIfAbsent(key, k -> Bucket.builder().addLimit(Bandwidth.classic(rpm, Refill.intervally(rpm, Duration.ofMinutes(1)))).build());
            if (bucket.tryConsume(1)) chain.doFilter(req, res);
            else {{ res.setStatus(429); res.setContentType("application/json"); res.getWriter().write("{\\"error\\":\\"Too many requests\\"}"); }}
        }}
    }}
    """


def init_sql(cfg):
    if cfg["security"] == "jwt":
        return """
        CREATE TABLE app_user (
          id BIGSERIAL PRIMARY KEY,
          email VARCHAR(320) NOT NULL UNIQUE,
          password VARCHAR(255) NOT NULL,
          role VARCHAR(30) NOT NULL DEFAULT 'USER'
        );
        """
    return "-- Add your first schema migration here.\n"


def dockerfile():
    return """
    FROM eclipse-temurin:21-jdk AS build
    WORKDIR /app
    COPY . .
    RUN ./mvnw -q -DskipTests package || mvn -q -DskipTests package

    FROM eclipse-temurin:21-jre
    WORKDIR /app
    COPY --from=build /app/target/*.jar app.jar
    USER 10001
    EXPOSE 8080
    ENTRYPOINT ["java","-jar","app.jar"]
    """


def compose(cfg):
    return f"""
    services:
      postgres:
        image: postgres:16
        environment:
          POSTGRES_DB: app
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
        ports:
          - "5432:5432"
        volumes:
          - postgres_data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U app -d app"]
          interval: 5s
          timeout: 3s
          retries: 10
    volumes:
      postgres_data:
    """


def test_class(cfg, pkg, cls):
    annotation = '@org.springframework.test.context.ActiveProfiles("test")' if cfg["database"] == "postgres" else ""
    return f"""
    package {pkg};
    import org.junit.jupiter.api.Test;
    import org.springframework.boot.test.context.SpringBootTest;
    @SpringBootTest
    {annotation}
    class {cls}ApplicationTests {{ @Test void contextLoads() {{}} }}
    """


def generated_readme(cfg):
    return f"""
    # {cfg['name']}

    Spring Boot {cfg['java']} project generated with Booster.

    ## Included
    - REST + validation + JPA
    - Database: {cfg['database']}
    - Flyway: {cfg['flyway']}
    - Security: {cfg['security']}
    - Swagger/OpenAPI: {cfg['swagger']}
    - Actuator: {cfg['actuator']}
    - Rate limiting: {cfg['rate_limit']}
    - Docker: {cfg['docker']}
    - Testcontainers: {cfg['testcontainers']}

    ## Run
    ```bash
    docker compose up -d
    ./mvnw spring-boot:run
    ```

    Health: `GET /actuator/health`  
    Ping: `GET /api/ping`  
    Swagger: `/swagger-ui/index.html`
    """


def load_config(path):
    cfg = dict(DEFAULTS)
    if path:
        cfg.update(json.loads(Path(path).read_text(encoding="utf-8")))
    return cfg


def main():
    p = argparse.ArgumentParser(description="Generate a production-ready Spring Boot starter")
    p.add_argument("name", nargs="?", help="Project name (overrides config)")
    p.add_argument("--config", help="JSON config file")
    p.add_argument("--output", help="Output directory")
    p.add_argument("--package", dest="package_name")
    p.add_argument("--security", choices=["jwt", "none"])
    p.add_argument("--database", choices=["postgres", "h2"])
    p.add_argument("--no-swagger", action="store_true")
    p.add_argument("--no-docker", action="store_true")
    p.add_argument("--no-rate-limit", action="store_true")
    args = p.parse_args()

    cfg = load_config(args.config)
    if args.name: cfg["name"] = args.name
    if args.package_name: cfg["package"] = args.package_name
    if args.security: cfg["security"] = args.security
    if args.database: cfg["database"] = args.database
    if args.no_swagger: cfg["swagger"] = False
    if args.no_docker: cfg["docker"] = False
    if args.no_rate_limit: cfg["rate_limit"] = False

    out = Path(args.output or artifact(cfg["name"])).resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    generate(cfg, out)
    print(f"Generated {cfg['name']} in {out}")
    print(f"Package: {cfg['package']} | Security: {cfg['security']} | DB: {cfg['database']}")


if __name__ == "__main__":
    main()
