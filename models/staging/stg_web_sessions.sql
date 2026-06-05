select
    safe_cast(session_id as string) as session_id,
    safe_cast(date as date) as session_date,
    coalesce(safe_cast(channel as string), 'Unknown') as channel,
    safe_cast(customer_id as string) as customer_id,
    coalesce(safe_cast(converted as int64), 0) as converted

from {{ source('raw', 'web_sessions') }}
