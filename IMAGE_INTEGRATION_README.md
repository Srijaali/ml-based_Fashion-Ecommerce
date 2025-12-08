# Product Image Integration Guide

This guide explains how product images are integrated into the FastAPI backend and how to use them in the frontend.

## How It Works

1. **Static File Serving**: The backend serves images from the `filtered_images` directory at the `/images` endpoint.
2. **Database Storage**: Each product (article) has an `image_path` column that stores the filename of its image.
3. **URL Generation**: The backend automatically converts `image_path` to `image_url` when returning product data.

## API Endpoints

### New Endpoints for Products with Images

1. **Get All Products with Images**
   ```
   GET /articles/products/
   ```
   Returns a list of products with `product_id`, `name`, `price`, and `image_url`.

2. **Get Single Product with Image**
   ```
   GET /articles/products/{product_id}
   ```
   Returns a single product with `product_id`, `name`, `price`, and `image_url`.

### Existing Endpoints (Now Include image_path)

All existing article endpoints now include the `image_path` field in their responses:
- `GET /articles/` - Get all articles
- `GET /articles/{article_id}` - Get single article
- `GET /articles/by-name/{prod_name}` - Get articles by name
- `GET /articles/search/{query}` - Search articles

## Image URL Format

Images are accessible at:
```
http://localhost:8000/images/{image_filename}
```

For example, if a product has `image_path` = "010123456.jpg", its image URL will be:
```
http://localhost:8000/images/010123456.jpg
```

## Database Schema Changes

A new column `image_path` has been added to the `articles` table:
```sql
ALTER TABLE niche_data.articles ADD COLUMN image_path text;
```

## Updating Image Paths

To populate the database with existing image filenames, run:
```bash
cd backend
python update_image_paths.py
```

This script will scan the `filtered_images` directory and update the `image_path` column for all matching articles.

## Frontend Usage

In your frontend code, you can now access product images using the `image_url` field:

```javascript
// For the new endpoints
fetch('http://localhost:8000/articles/products/')
  .then(response => response.json())
  .then(products => {
    products.forEach(product => {
      console.log(product.image_url); // Full URL to the product image
    });
  });

// For existing endpoints (with image_path)
fetch('http://localhost:8000/articles/')
  .then(response => response.json())
  .then(articles => {
    articles.forEach(article => {
      const imageUrl = `http://localhost:8000/images/${article.image_path}`;
      console.log(imageUrl);
    });
  });
```

## Troubleshooting

1. **Images not loading**: Make sure the `update_image_paths.py` script has been run to populate the database.

2. **404 errors**: Verify that image files exist in the `backend/filtered_images` directory and that their filenames match the `article_id` values in the database.

3. **CORS issues**: The backend is configured to allow all origins, but you can adjust the CORS settings in `main.py` if needed.