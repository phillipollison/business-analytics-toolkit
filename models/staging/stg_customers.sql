select
    safe_cast(customer_id as string) as customer_id,
    safe_cast(customer_email as string) as customer_email,
    safe_cast(first_order_date as date) as first_order_date,
    coalesce(safe_cast(customer_segment as string), 'Unknown') as customer_segment

from {{ source('raw', 'customers') }}
