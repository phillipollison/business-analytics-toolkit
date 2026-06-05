select
    safe_cast(product_id as string) as product_id,
    safe_cast(product_name as string) as product_name,
    coalesce(safe_cast(category as string), 'Unknown') as category

from {{ source('raw', 'products') }}
