package com.example.unifiedbackend.service;

import com.example.unifiedbackend.dto.MovieDto;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class MovieService {

    @Value("${tmdb.api.key}")
    private String tmdbApiKey;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public List<MovieDto> getRecommendedMovies(String emotion, int count) {
        String genre = switch (emotion.toLowerCase()) {
            case "anger" -> "action";
            case "sadness" -> "drama";
            case "anxiety" -> "thriller";
            case "normal" -> "family";
            default -> "family";
        };

        int genreId = getGenreId(genre);

        String url = "https://api.themoviedb.org/3/discover/movie?api_key=" + tmdbApiKey +
                     "&with_genres=" + genreId +
                     "&language=ko-KR&sort_by=popularity.desc";

        String json = restTemplate.getForObject(url, String.class);
        List<MovieDto> movieList = new ArrayList<>();
        Set<String> seen = new HashSet<>();

        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode results = root.path("results");

            for (JsonNode item : results) {
                String title = item.path("title").asText();
                if (seen.contains(title)) continue;
                seen.add(title);

                String overview = item.path("overview").asText();
                String posterPath = item.path("poster_path").asText();
                double voteAverage = item.path("vote_average").asDouble(0.0);  // ← 여기 확인
                int voteCount = item.path("vote_count").asInt(0);
                double popularity = item.path("popularity").asDouble(0.0);

                if (posterPath == null || posterPath.isEmpty()) continue;
                if (voteCount < 10 || popularity < 10.0) continue;  // 너무 적은 데이터는 제외

                String posterUrl = "https://image.tmdb.org/t/p/w500" + posterPath;

                movieList.add(new MovieDto(title, posterUrl, overview, voteAverage));
            }

            // 랜덤 섞고 count개만 추출
            Collections.shuffle(movieList);
            return movieList.subList(0, Math.min(count, movieList.size()));

        } catch (Exception e) {
            e.printStackTrace();
        }

        return movieList;
    }

    private int getGenreId(String genre) {
        return switch (genre.toLowerCase()) {
            case "action" -> 28;
            case "drama" -> 18;
            case "thriller" -> 53;
            case "family" -> 10751;
            default -> 10751;
        };
    }
}
