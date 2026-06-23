-- Intermediate model for joined flights - weather data.
-- INNER JOIN on iata_code and date
-- Ref: stg_flights, stg_weather

WITH flights AS (
    SELECT * FROM {{ ref('stg_flights') }}
),

weather AS (
    SELECT * FROM {{ ref('stg_weather') }}
),

joined AS (
    SELECT 
        f.*,
        w.temp_avg,
        w.temp_min,
        w.temp_max,
        w.precipitation,
        w.snow_depth,
        w.wind_direction,
        w.wind_speed,
        w.peak_wind_gust,
        w.air_pressure,
        w.total_sunshine

    FROM flights f 
    INNER JOIN weather w
    ON f.origin_airport_code = w.iata_code
    AND f.flight_date = w.date
)

SELECT * FROM joined