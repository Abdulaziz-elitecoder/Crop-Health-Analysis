# API Documentation

## Authentication (/auth)

### POST /auth/signup
**Description:** Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user_id": "uuid",
  "access_token": "jwt-token",
  "refresh_token": "refresh-token"
}
```

**Errors:**
- 400: Invalid email or signup failed.

---

### POST /auth/signin
**Description:** Log in an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user_id": "uuid",
  "access_token": "jwt-token",
  "refresh_token": "refresh-token"
}
```

**Errors:**
- 401: Invalid credentials.

---

### POST /auth/logout
**Description:** Log out a user.

**Request Body:**
```json
{
  "access_token": "jwt-token"
}
```

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Errors:**
- 400: Logout failed.

---

## Users (/users)

### GET /users/{user_id}
**Description:** Retrieve user details.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com"
}
```

**Errors:**
- 401: Unauthorized.
- 404: User not found.

---

## Images (/images)

### POST /images/
**Description:** Upload an image.

**Headers:**
- Authorization: Bearer <jwt-token>

**Form Data:**
- file: The image file (JPEG, PNG, or TIFF).
- user_id: The UUID of the user uploading the image.
- metadata (optional): JSON string (e.g., {"location": "Field A", "crop_type": "Wheat"}).

**Response (200):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "image_url": "https://supabase-url/storage/v1/object/public/images/...",
  "file_type": "rgb",
  "metadata": {"location": "Field A", "crop_type": "Wheat"},
  "created_at": "2025-04-15T12:00:00Z"
}
```

**Errors:**
- 401: Unauthorized.
- 400: Invalid file or upload failed.

---

### GET /images/
**Description:** Retrieve all images for a user.

**Query Parameters:**
- user_id: The UUID of the user.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "image_url": "https://supabase-url/storage/v1/object/public/images/...",
    "file_type": "ndvi",
    "metadata": {"location": "Field A", "crop_type": "Wheat"},
    "created_at": "2025-04-15T12:00:00Z"
  }
]
```

**Errors:**
- 401: Unauthorized.

---

### GET /images/{image_id}
**Description:** Retrieve a specific image by ID.

**Query Parameters:**
- user_id: The UUID of the user.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "image_url": "https://supabase-url/storage/v1/object/public/images/...",
  "file_type": "rgb",
  "metadata": {"location": "Field A", "crop_type": "Wheat"},
  "created_at": "2025-04-15T12:00:00Z"
}
```

**Errors:**
- 401: Unauthorized.
- 404: Image not found.

---

### DELETE /images/{image_id}
**Description:** Delete an image by ID.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "message": "Image deleted successfully"
}
```

**Errors:**
- 401: Unauthorized.
- 404: Image not found.

---

## Classifications (/classifications)

### POST /classifications/{image_id}
**Description:** Classify an image as healthy or unhealthy.

**Query Parameters:**
- user_id: The UUID of the user.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "id": "uuid",
  "image_id": "uuid",
  "classification": "healthy",
  "confidence": 0.95,
  "created_at": "2025-04-15T12:00:00Z"
}
```

**Errors:**
- 401: Unauthorized.
- 404: Image not found.
- 400: Classification failed (e.g., invalid image format).

---

### GET /classifications/{image_id}/result
**Description:** Retrieve the classification result for an image.

**Query Parameters:**
- user_id: The UUID of the user.

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
{
  "id": "uuid",
  "image_id": "uuid",
  "classification": "healthy",
  "confidence": 0.95,
  "created_at": "2025-04-15T12:00:00Z"
}
```

**Errors:**
- 401: Unauthorized.
- 404: Classification not found.

---

## Logs (/logs)

### GET /logs/
**Description:** Retrieve API request logs (admin access may be required).

**Headers:**
- Authorization: Bearer <jwt-token>

**Response (200):**
```json
[
  {
    "id": "uuid",
    "endpoint": "/images/",
    "method": "POST",
    "status_code": 200,
    "user_id": "uuid",
    "created_at": "2025-04-15T12:00:00Z"
  }
]
```

**Errors:**
- 401: Unauthorized.

---

## Testing the API

### Sign Up:
```bash
curl -X POST http://localhost:8000/auth/signup \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "password": "password123"}'
```

### Upload an Image:
```bash
curl -X POST http://localhost:8000/images/?user_id=<user-id> \
-H "Authorization: Bearer <access-token>" \
-F "file=@/path/to/image.jpg" \
-F "metadata={\"location\": \"Field A\", \"crop_type\": \"Wheat\"}"
```

### Classify the Image:
```bash
curl -X POST http://localhost:8000/classifications/<image-id>?user_id=<user-id> \
-H "Authorization: Bearer <access-token>"
```

### Get Classification Result:
```bash
curl -X GET http://localhost:8000/classifications/<image-id>/result?user_id=<user-id> \
-H "Authorization: Bearer <access-token>"
```

---

## Troubleshooting

### Supabase Connection Issues:
- Ensure the SUPABASE_URL and SUPABASE_KEY are correct in your .env file.
- Check that your Supabase project is running and accessible.

### Model Loading Errors:
- Verify that model/inception.keras exists and is a valid Keras model file.
- Ensure TensorFlow is installed (`pip install tensorflow`).

### Image Upload Failures:
- Check that the Supabase images bucket exists and is configured correctly.
- Ensure the file type is supported (JPEG, PNG, TIFF).

### Logs:
- Check the terminal output for error messages.
- Review the logs in the Supabase database (logs table) or API responses from /logs/.

