// File: src/main/java/com/tradingplatform/userservice/controller/UserController.java
// Fixed version with proper request mapping

package com.tradingplatform.userservice.controller;

import com.tradingplatform.userservice.dto.*;
import com.tradingplatform.userservice.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/")  // Changed from "" to "/"
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Tag(name = "User Management", description = "User authentication and profile management")
public class UserController {
    
    private final UserService userService;
    
    @PostMapping("register")  // This becomes /api/users/register
    @Operation(summary = "Register a new user")
    public ResponseEntity<AuthResponseDto> register(@Valid @RequestBody UserRegistrationDto request) {
        return ResponseEntity.ok(userService.register(request));
    }
    
    @PostMapping("login")  // This becomes /api/users/login
    @Operation(summary = "Login user")
    public ResponseEntity<AuthResponseDto> login(@Valid @RequestBody LoginRequestDto request) {
        return ResponseEntity.ok(userService.login(request));
    }
    
    @PostMapping("refresh")  // This becomes /api/users/refresh
    @Operation(summary = "Refresh access token")
    public ResponseEntity<AuthResponseDto> refresh(@Valid @RequestBody RefreshTokenDto request) {
        return ResponseEntity.ok(userService.refreshToken(request.getRefreshToken()));
    }
    
    @GetMapping("profile")  // This becomes /api/users/profile
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Get user profile")
    public ResponseEntity<UserProfileDto> getProfile(@RequestHeader("Authorization") String token) {
        return ResponseEntity.ok(userService.getUserProfile(token));
    }
    
    @PutMapping("profile")  // This becomes /api/users/profile
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Update user profile")
    public ResponseEntity<UserProfileDto> updateProfile(
            @RequestHeader("Authorization") String token,
            @Valid @RequestBody UpdateProfileDto request) {
        return ResponseEntity.ok(userService.updateProfile(token, request));
    }
    
    @GetMapping("health")  // This becomes /api/users/health
    @Operation(summary = "Health check endpoint")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("User Service is healthy");
    }
}