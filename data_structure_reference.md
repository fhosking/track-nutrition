# Food Log Data Structure Reference

## brands
| Column     | Type      | Description                    |
|------------|-----------|--------------------------------|
| id         | integer   | Primary key                    |
| name       | text      | Brand name (unique)            |
| created_at | timestamp | When brand was created         |

## food_library
| Column       | Type             | Description                         |
|--------------|------------------|-------------------------------------|
| id           | integer          | Primary key                         |
| name         | text             | Food item name                      |
| protein_g    | double precision | Protein per serving (g)             |
| fat_g        | double precision | Fat per serving (g)                 |
| alcohol_g    | double precision | Alcohol per serving (g)             |
| carbs_g      | double precision | Carbs per serving (g)               |
| fibre_g      | double precision | Fibre per serving (g)               |
| unit_type    | text             | Unit type (e.g., g, ml, slice)      |
| serving_size | text             | Description of serving size         |
| brand_id     | integer          | Foreign key to brands(id)           |
| brand        | text             | Legacy brand field (deprecated)     |

## food_log
| Column    | Type             | Description                         |
|-----------|------------------|-------------------------------------|
| id        | integer          | Primary key                         |
| food_id   | integer          | Foreign key to food_library(id)     |
| date      | date             | Date of entry                       |
| quantity  | double precision | Quantity consumed                   |

## Notes
- The `brands` table is the primary source for brand information
- `food_library.brand_id` references `brands.id` for proper normalization
- `food_library.brand` is kept for backward compatibility but should be migrated to `brand_id`
- Brand filtering is done via the `brand_id` relationship
