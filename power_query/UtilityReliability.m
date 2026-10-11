let
    Source = Csv.Document(
        File.Contents(UtilityReliabilityPath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"year", Int64.Type},
        {"utility_id", Int64.Type},
        {"utility_name", type text},
        {"state", type text},
        {"ownership", type text},
        {"ieee_saidi_with_med_minutes", type number},
        {"ieee_saifi_with_med_interruptions", type number},
        {"ieee_caidi_with_med_minutes", type number},
        {"ieee_saidi_without_med_minutes", type number},
        {"ieee_saifi_without_med_interruptions", type number},
        {"ieee_caidi_without_med_minutes", type number},
        {"customer_count", Int64.Type},
        {"highest_distribution_voltage_kv", type number},
        {"outages_recorded_automatically", type text}
    })
in
    Types
