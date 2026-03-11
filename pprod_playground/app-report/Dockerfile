# Build stage with Gradle and Java 21
FROM gradle:8.6-jdk21-alpine AS build
WORKDIR /app

# Copy Gradle files first (for better layer caching)
COPY build.gradle .
COPY settings.gradle .
#COPY gradle.properties .
COPY gradle ./gradle
COPY gradlew .

# Download dependencies (cached unless build files change)
RUN ./gradlew dependencies --no-daemon

# Copy source code
COPY src ./src

# Build the application
RUN ./gradlew clean build -x test --no-daemon

# Runtime stage
FROM eclipse-temurin:21
WORKDIR /app

# Create non-root user for security
RUN groupadd -r spring && useradd -r -g spring spring
USER spring

# Copy the built artifact
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8000

ENTRYPOINT ["java", "-jar", "app.jar"]

