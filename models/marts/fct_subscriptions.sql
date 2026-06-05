with subscriptions as (

    select
        subscription_id,
        customer_id,
        start_date,
        date_trunc(start_date, month) as start_month,
        status,
        cancel_date,
        date_trunc(cancel_date, month) as cancel_month,
        monthly_price,
        case
            when status in ('active', 'trialing') then true
            else false
        end as is_active,
        case
            when status in ('canceled', 'cancelled', 'churned') then true
            else false
        end as is_canceled

    from {{ ref('stg_subscriptions') }}

)

select *
from subscriptions
