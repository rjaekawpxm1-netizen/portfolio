package com.example.unifiedbackend.controller;

import com.example.unifiedbackend.dto.MovieDto;
import com.example.unifiedbackend.service.MovieService;
import org.springframework.web.bind.annotation.*;

import java.util.List;


@RestController
@RequestMapping("/api/recommendations")
public class MovieController {

    private final MovieService movieService;
    public MovieController(MovieService movieService) {
        this.movieService = movieService;
    }

    @GetMapping("/movies")
    public List<MovieDto> getMovies(
            @RequestParam String emotion,
            @RequestParam(defaultValue = "2") int count) {
        System.out.println("🎬 getMovies() called with emotion = " + emotion);
        return movieService.getRecommendedMovies(emotion, count);
    }
}
