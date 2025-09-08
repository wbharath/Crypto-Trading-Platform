package com.tradingplatform.userservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDto {
    
    private Long id;
    private String email;
    private String firstName;
    private String lastName;
    private String role;
    private String status;
    private Boolean kycVerified;
    private Boolean twoFactorEnabled;
    private LocalDateTime createdAt;
}
