-- Staging model for raw airports data.
-- Selects relevant columns, and filter rows by country and iata code completeness.
-- Source: raw.airports

WITH source AS (

    SELECT * FROM {{ source('raw', 'airports') }}

),

filtered AS (

    SELECT iata_code,
           name,
           city,
           country,
           latitude,
           longitude

    FROM source

    WHERE country = 'United States'
      AND iata_code IS NOT NULL
      AND iata_code != ''
      AND iata_code != '\\N'

)

SELECT * FROM filtered