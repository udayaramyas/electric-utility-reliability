let
    Source = Csv.Document(
        File.Contents(StateTotalsPath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"year", Int64.Type},
        {"state", type text},
        {"customer_count_any_standard", Int64.Type},
        {"saidi_with_med_minutes", type number},
        {"saifi_with_med_interruptions", type number},
        {"caidi_with_med_minutes", type number},
        {"saidi_without_med_minutes", type number},
        {"saifi_without_med_interruptions", type number},
        {"caidi_without_med_minutes", type number}
    })
in
    Types
