

FROM eclipse-temurin:17-jdk-alpine as build


RUN apk update && apk add --no-cache maven


WORKDIR /app


COPY pom.xml .


RUN mvn dependency:go-offline -B


COPY src ./src


RUN mvn clean package -DskipTests


FROM eclipse-temurin:17-jre-alpine

RUN apk update && apk add --no-cache curl

RUN addgroup --system spring && adduser --system spring --ingroup spring


WORKDIR /app


COPY --from=build /app/target/user-service-*.jar app.jar

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