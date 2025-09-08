package com.tradingplatform.userservice.service;

import com.tradingplatform.userservice.dto.*;
import com.tradingplatform.userservice.entity.User;
import com.tradingplatform.userservice.exception.UserNotFoundException;
import com.tradingplatform.userservice.exception.InvalidCredentialsException;
import com.tradingplatform.userservice.repository.UserRepository;
import com.tradingplatform.userservice.security.JwtService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
@Slf4j
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final TwoFactorService twoFactorService;
    
    public AuthResponseDto register(UserRegistrationDto request) {
        log.info("Attempting to register user with email: {}", request.getEmail());
        
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already exists");
        }
        
        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhoneNumber(request.getPhoneNumber());
        
        user = userRepository.save(user);
        
        String accessToken = jwtService.generateToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);
        
        log.info("User registered successfully with ID: {}", user.getId());
        
        return AuthResponseDto.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(jwtService.getExpirationTime())
                .user(mapToUserDto(user))
                .build();
    }
    
    public AuthResponseDto login(LoginRequestDto request) {
        log.info("Attempting login for email: {}", request.getEmail());
        
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new InvalidCredentialsException("Invalid credentials"));
        
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new InvalidCredentialsException("Invalid credentials");
        }
        
        // Check 2FA if enabled
        if (user.getTwoFactorEnabled() && request.getTwoFactorCode() != null) {
            if (!twoFactorService.verifyCode(user, request.getTwoFactorCode())) {
                throw new InvalidCredentialsException("Invalid 2FA code");
            }
        } else if (user.getTwoFactorEnabled()) {
            throw new IllegalArgumentException("2FA code required");
        }
        
        String accessToken = jwtService.generateToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);
        
        log.info("User logged in successfully: {}", user.getId());
        
        return AuthResponseDto.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(jwtService.getExpirationTime())
                .user(mapToUserDto(user))
                .build();
    }
    
    public AuthResponseDto refreshToken(String refreshToken) {
        String email = jwtService.extractUsername(refreshToken);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
        
        if (!jwtService.isTokenValid(refreshToken, user)) {
            throw new IllegalArgumentException("Invalid refresh token");
        }
        
        String newAccessToken = jwtService.generateToken(user);
        
        return AuthResponseDto.builder()
                .accessToken(newAccessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(jwtService.getExpirationTime())
                .user(mapToUserDto(user))
                .build();
    }
    
    public UserProfileDto getUserProfile(String token) {
        User user = getUserFromToken(token);
        return mapToUserProfileDto(user);
    }
    
    public UserProfileDto updateProfile(String token, UpdateProfileDto request) {
        User user = getUserFromToken(token);
        
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhoneNumber(request.getPhoneNumber());
        
        user = userRepository.save(user);
        log.info("Profile updated for user: {}", user.getId());
        
        return mapToUserProfileDto(user);
    }
    
    public TwoFactorSetupDto enableTwoFactor(String token) {
        User user = getUserFromToken(token);
        return twoFactorService.generateSetup(user);
    }
    
    public void verifyTwoFactor(String token, String code) {
        User user = getUserFromToken(token);
        twoFactorService.verifyAndEnable(user, code);
        log.info("2FA enabled for user: {}", user.getId());
    }
    
    private User getUserFromToken(String token) {
        String jwt = token.substring(7); // Remove "Bearer " prefix
        String email = jwtService.extractUsername(jwt);
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User not found"));
    }
    
    private UserDto mapToUserDto(User user) {
        return UserDto.builder()
                .id(user.getId())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .role(user.getRole().name())
                .status(user.getStatus().name())
                .kycVerified(user.getKycVerified())
                .twoFactorEnabled(user.getTwoFactorEnabled())
                .createdAt(user.getCreatedAt())
                .build();
    }
    
    private UserProfileDto mapToUserProfileDto(User user) {
        return UserProfileDto.builder()
                .id(user.getId())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .phoneNumber(user.getPhoneNumber())
                .role(user.getRole().name())
                .status(user.getStatus().name())
                .kycVerified(user.getKycVerified())
                .twoFactorEnabled(user.getTwoFactorEnabled())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}