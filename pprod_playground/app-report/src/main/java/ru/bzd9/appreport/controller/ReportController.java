package ru.bzd9.appreport.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequiredArgsConstructor
public class ReportController {
    private final JdbcTemplate jdbcTemplate;

    @GetMapping("/reports")
    public List<ReportRow> reports(@AuthenticationPrincipal Jwt jwt) {
        int user_id = Integer.parseInt(jwt.getClaimAsString("crm_user_id"));

        List<ReportRow> resultList = jdbcTemplate.query(
                "SELECT user_id, prosthesis_type, muscle_group, signal_time FROM default.emg_sensor_data WHERE user_id = ?",
                (rs, rowNum) -> new ReportRow(
                        rs.getInt("user_id"),
                        rs.getString("prosthesis_type"),
                        rs.getString("muscle_group"),
                        rs.getTimestamp("signal_time").toLocalDateTime()),
                user_id
        );

        return resultList;
    }

    public record ReportRow(
            int user_id,
            String prosthesisType,
            String muscleGroup,
            LocalDateTime signalTime
    ) {

    }

}
