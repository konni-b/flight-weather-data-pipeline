-- Staging model for raw BTS On-Time Performance data.
-- Selects relevant columns, renames to snake_case, and fixes data types.
-- Source: raw.flights (Dec 2022 + Jan 2023)

WITH source AS (

    SELECT * FROM {{ source('raw', 'flights') }}

),

renamed AS (

    SELECT
        -- Flight identifiers
        FlightDate                                          AS flight_date,
        Reporting_Airline                                   AS airline_code,
        Flight_Number_Reporting_Airline                     AS flight_number,

        -- Origin
        Origin                                              AS origin_airport_code,
        OriginCityName                                      AS origin_city_name,
        OriginState                                         AS origin_state,

        -- Destination
        Dest                                                AS dest_airport_code,
        DestCityName                                        AS dest_city_name,
        DestState                                           AS dest_state,

        -- Scheduled times
        CRSDepTime                                          AS scheduled_dep_time,
        CRSArrTime                                          AS scheduled_arr_time,

        -- Actual times
        DepTime                                             AS actual_dep_time,
        ArrTime                                             AS actual_arr_time,

        -- Delays (minutes) — cast from FLOAT to INTEGER
        CAST(DepDelay AS INT64)                             AS dep_delay_minutes,
        CAST(ArrDelay AS INT64)                             AS arr_delay_minutes,

        -- Delay breakdown by cause (minutes)
        CAST(CarrierDelay AS INT64)                         AS carrier_delay_minutes,
        CAST(WeatherDelay AS INT64)                         AS weather_delay_minutes,
        CAST(NASDelay AS INT64)                             AS nas_delay_minutes,
        CAST(LateAircraftDelay AS INT64)                    AS late_aircraft_delay_minutes,

        -- Cancellation
        CAST(Cancelled AS INT64)                             AS is_cancelled,
        CancellationCode                                    AS cancellation_code,

        -- Diverted
        CAST(Diverted AS INT64)                              AS is_diverted,

        -- Flight stats
        CAST(AirTime AS INT64)                              AS air_time_minutes,
        CAST(Distance AS INT64)                             AS distance_miles

    FROM source

)

SELECT * FROM renamed
