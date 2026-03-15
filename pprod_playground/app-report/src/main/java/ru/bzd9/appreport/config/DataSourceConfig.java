package ru.bzd9.appreport.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.datasource.SimpleDriverDataSource;

import javax.sql.DataSource;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

@Configuration
@ConfigurationProperties("spring.datasource")
public class DataSourceConfig {

    @Value("${spring.datasource.url}")
    private String uri;

    @Value("${spring.datasource.username}")
    private String username;

    @Value("${spring.datasource.password}")
    private String password;

    @Bean
    public DataSource dataSource() throws SQLException {
        SimpleDriverDataSource dataSource = new SimpleDriverDataSource();

        dataSource.setDriver(DriverManager.getDriver(uri));
        dataSource.setUrl(uri);
        dataSource.setUsername(username);
        dataSource.setPassword(password);

        Properties connectionProperties = new Properties();
//        connectionProperties.setProperty("useUnicode","true");
//        connectionProperties.setProperty("characterEncoding","UTF-8");
//        connectionProperties.setProperty("prepareThreshold","0");
        dataSource.setConnectionProperties(connectionProperties);

        return dataSource;
    }

}
