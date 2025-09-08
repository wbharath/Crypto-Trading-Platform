# Dockerfile for User Service
# Multi-stage build for Spring Boot application

# Stage 1: Build stage with Maven
FROM eclipse-temurin:17-jdk-alpine as build

# Install Maven
RUN apk update && apk add --no-cache maven

# Set working directory
WORKDIR /app

# Copy pom.xml first (for better Docker layer caching)
COPY pom.xml .

# Download dependencies (this layer will be cached unless pom.xml changes)
RUN mvn dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Stage 2: Runtime stage
FROM eclipse-temurin:17-jre-alpine

# Install curl for health check
RUN apk update && apk add --no-cache curl

# Create app user
RUN addgroup --system spring && adduser --system spring --ingroup spring

# Set working directory
WORKDIR /app

# Copy the built jar from build stage
COPY --from=build /app/target/user-service-*.jar app.jar

# Change ownership
RUN chown spring:spring app.jar

# Switch to non-root user
USER spring:spring

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/users/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]