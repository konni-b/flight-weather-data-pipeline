-- Mart model
-- All columns from intermediate model
-- Plus, derived columns for easier analysis
-- Ref: int_flights_weather

WITH flights_weather AS (
    SELECT * FROM {{ ref('int_flights_weather') }}
),
fct_flights AS (
    SELECT  *,
            CASE
                WHEN is_cancelled = 1 AND cancellation_code = 'B' THEN TRUE
                ELSE FALSE
            END AS is_weather_cancelled,
            CASE
                WHEN is_cancelled = 1 AND cancellation_code = 'A' THEN TRUE
                ELSE FALSE
            END AS is_carrier_cancelled,
            CASE
                WHEN airline_code = 'WN' THEN TRUE
                ELSE FALSE
            END AS is_southwest,
            CASE
                WHEN flight_date BETWEEN '2022-12-21' AND '2022-12-26' THEN TRUE
                ELSE FALSE
            END AS is_storm_period
    FROM flights_weather
)

SELECT * FROM fct_flights
