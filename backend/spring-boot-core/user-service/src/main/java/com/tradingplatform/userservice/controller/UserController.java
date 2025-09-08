// File: src/main/java/com/tradingplatform/userservice/controller/UserController.java
// Make sure you have ALL these imports at the top:

package com.tradingplatform.userservice.controller;

import com.tradingplatform.userservice.dto.AuthResponseDto;
import com.tradingplatform.userservice.dto.LoginRequestDto;
import com.tradingplatform.userservice.dto.RefreshTokenDto;
import com.tradingplatform.userservice.dto.TwoFactorSetupDto;
import com.tradingplatform.userservice.dto.TwoFactorVerificationDto;
import com.tradingplatform.userservice.dto.UpdateProfileDto;
import com.tradingplatform.userservice.dto.UserProfileDto;  // ← Make sure this import is here
import com.tradingplatform.userservice.dto.UserRegistrationDto;
import com.tradingplatform.userservice.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Tag(name = "User Management", description = "User authentication and profile management")
public class UserController {
    
    private final UserService userService;
    
    @PostMapping("/register")
    @Operation(summary = "Register a new user")
    public ResponseEntity<AuthResponseDto> register(@Valid @RequestBody UserRegistrationDto request) {
        return ResponseEntity.ok(userService.register(request));
    }
    
    @PostMapping("/login")
    @Operation(summary = "Login user")
    public ResponseEntity<AuthResponseDto> login(@Valid @RequestBody LoginRequestDto request) {
        return ResponseEntity.ok(userService.login(request));
    }
    
    @PostMapping("/refresh")
    @Operation(summary = "Refresh access token")
    public ResponseEntity<AuthResponseDto> refresh(@Valid @RequestBody RefreshTokenDto request) {
        return ResponseEntity.ok(userService.refreshToken(request.getRefreshToken()));
    }
    
    @GetMapping("/profile")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Get user profile")
    public ResponseEntity<UserProfileDto> getProfile(@RequestHeader("Authorization") String token) {
        return ResponseEntity.ok(userService.getUserProfile(token));
    }
    
    @PutMapping("/profile")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Update user profile")
    public ResponseEntity<UserProfileDto> updateProfile(
            @RequestHeader("Authorization") String token,
            @Valid @RequestBody UpdateProfileDto request) {
        return ResponseEntity.ok(userService.updateProfile(token, request));
    }
    
    @PostMapping("/enable-2fa")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Enable two-factor authentication")
    public ResponseEntity<TwoFactorSetupDto> enableTwoFactor(@RequestHeader("Authorization") String token) {
        return ResponseEntity.ok(userService.enableTwoFactor(token));
    }
    
    @PostMapping("/verify-2fa")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Verify and activate two-factor authentication")
    public ResponseEntity<String> verifyTwoFactor(
            @RequestHeader("Authorization") String token,
            @Valid @RequestBody TwoFactorVerificationDto request) {
        userService.verifyTwoFactor(token, request.getCode());
        return ResponseEntity.ok("Two-factor authentication enabled successfully");
    }
    
    @GetMapping("/health")
    @Operation(summary = "Health check endpoint")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("User Service is healthy");
    }
}