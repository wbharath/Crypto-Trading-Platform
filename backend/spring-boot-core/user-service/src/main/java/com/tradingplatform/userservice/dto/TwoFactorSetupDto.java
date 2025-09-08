package com.tradingplatform.userservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TwoFactorSetupDto {
    
    private String secret;
    private String qrCodeUrl;
    private String manualEntryKey;
}