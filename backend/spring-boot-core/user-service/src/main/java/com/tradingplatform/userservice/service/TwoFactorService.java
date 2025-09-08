package com.tradingplatform.userservice.service;

import com.tradingplatform.userservice.dto.TwoFactorSetupDto;
import com.tradingplatform.userservice.entity.User;
import com.tradingplatform.userservice.repository.UserRepository;
import com.warrenstrange.googleauth.GoogleAuthenticator;
import com.warrenstrange.googleauth.GoogleAuthenticatorKey;
import com.warrenstrange.googleauth.GoogleAuthenticatorQRGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class TwoFactorService {
    
    private final UserRepository userRepository;
    private final GoogleAuthenticator googleAuthenticator = new GoogleAuthenticator();
    
    @Value("${totp.issuer}")
    private String issuer;
    
    public TwoFactorSetupDto generateSetup(User user) {
        GoogleAuthenticatorKey key = googleAuthenticator.createCredentials();
        String secret = key.getKey();
        
        // Save secret to user (but don't enable 2FA yet)
        user.setTwoFactorSecret(secret);
        userRepository.save(user);
        
        String qrCodeUrl = GoogleAuthenticatorQRGenerator.getOtpAuthTotpURL(
                issuer,
                user.getEmail(),
                key
        );
        
        log.info("Generated 2FA setup for user: {}", user.getId());
        
        return TwoFactorSetupDto.builder()
                .secret(secret)
                .qrCodeUrl(qrCodeUrl)
                .manualEntryKey(secret)
                .build();
    }
    
    public boolean verifyCode(User user, String code) {
        if (user.getTwoFactorSecret() == null) {
            return false;
        }
        
        try {
            int verificationCode = Integer.parseInt(code);
            return googleAuthenticator.authorize(user.getTwoFactorSecret(), verificationCode);
        } catch (NumberFormatException e) {
            log.warn("Invalid 2FA code format for user: {}", user.getId());
            return false;
        }
    }
    
    public void verifyAndEnable(User user, String code) {
        if (!verifyCode(user, code)) {
            throw new IllegalArgumentException("Invalid verification code");
        }
        
        user.setTwoFactorEnabled(true);
        userRepository.save(user);
        
        log.info("2FA successfully enabled for user: {}", user.getId());
    }
}