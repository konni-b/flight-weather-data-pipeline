-- Staging model for raw weather data.
-- Selects relevant columns, renames to snake_case, and fixes data types.
-- Source: raw.weather (Dec 2022 + Jan 2023)

WITH source AS (

    SELECT * FROM {{ source('raw', 'weather') }}

),

renamed AS (

    SELECT
        iata_code,
        CAST(date AS DATE)    AS date,
        tavg                  AS temp_avg,
        tmin                  AS temp_min,
        tmax                  AS temp_max,
        prcp                  AS precipitation,
        CAST(snow AS INTEGER) AS snow_depth,
        CAST(wdir AS INTEGER) AS wind_direction,
        wspd                  AS wind_speed,
        wpgt                  AS peak_wind_gust,
        pres                  AS air_pressure,
        CAST(tsun AS INTEGER) AS total_sunshine

    FROM source

)

SELECT * FROM renamed
