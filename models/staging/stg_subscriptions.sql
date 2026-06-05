select
    safe_cast(subscription_id as string) as subscription_id,
    safe_cast(customer_id as string) as customer_id,
    safe_cast(start_date as date) as start_date,
    lower(coalesce(safe_cast(status as string), 'unknown')) as status,
    safe_cast(cancel_date as date) as cancel_date,
    coalesce(safe_cast(monthly_price as numeric), 0) as monthly_price

from {{ source('raw', 'subscriptions') }}
