select
    safe_cast(order_id as string) as order_id,
    safe_cast(customer_id as string) as customer_id,
    safe_cast(order_date as date) as order_date,
    coalesce(safe_cast(channel as string), 'Unknown') as channel,
    safe_cast(revenue as numeric) as revenue,
    coalesce(safe_cast(refund_amount as numeric), 0) as refund_amount

from {{ source('raw', 'orders') }}
