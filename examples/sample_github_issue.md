# Sample GitHub Issue for Test Generation

## Example 1: User Authentication Feature

**Title**: Implement User Authentication

**Body**:
```markdown
We need to implement user authentication for the application to allow users to securely log in and access their accounts.

## Acceptance Criteria

- AC1: User can navigate to the login page at `/login`
- AC2: User can enter username and password in the login form
- AC3: User receives clear error message when entering invalid credentials
- AC4: User is redirected to dashboard at `/dashboard` after successful login
- AC5: User session persists after page reload
- AC6: User can log out and session is cleared

## Additional Context

This feature should integrate with the existing User model in `src/models/user.py`.
Follow the authentication patterns used in `src/auth/session.py`.

## Related Files
- `src/models/user.py` - User data model
- `src/auth/session.py` - Session management
- `src/routes/auth.py` - Authentication endpoints
```

---

## Example 2: Shopping Cart Functionality

**Title**: Add Shopping Cart Feature

**Body**:
```markdown
Implement shopping cart functionality to allow users to add, remove, and manage products before checkout.

## Acceptance Criteria

- AC1: User can add products to cart from product listing page
- AC2: User can view cart with all added products and quantities
- AC3: User can update product quantities in the cart
- AC4: User can remove products from the cart
- AC5: Cart displays correct subtotal and total prices
- AC6: Cart persists across browser sessions
- AC7: User sees empty cart message when cart has no items

## Technical Notes

- Use localStorage for cart persistence
- Integrate with existing Product API at `/api/products`
- Calculate taxes based on user location
- Maximum 99 items per product in cart

## Related Components
- `src/components/ProductCard.tsx` - Product display component
- `src/api/cart.ts` - Cart API client
- `src/store/cartStore.ts` - Cart state management
```

---

## Example 3: API Endpoint for User Search

**Title**: Create User Search API Endpoint

**Body**:
```markdown
Create a REST API endpoint to search users by various criteria.

## Acceptance Criteria

- AC1: Endpoint accepts GET request at `/api/users/search`
- AC2: Supports query parameters: `q` (search term), `role` (filter by role), `limit` (max results)
- AC3: Searches across username, email, and full name fields
- AC4: Returns users in JSON format with id, username, email, role
- AC5: Returns 400 error for invalid parameters
- AC6: Returns 200 with empty array when no users match
- AC7: Implements pagination with `page` and `limit` parameters
- AC8: Search is case-insensitive
- AC9: Requires authentication token in Authorization header

## API Specification

```
GET /api/users/search?q=john&role=admin&page=1&limit=20
Authorization: Bearer <token>

Response:
{
  "users": [...],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

## Related Files
- `src/routes/users.py` - User routes
- `src/models/user.py` - User model
- `src/services/search.py` - Search service
```

---

## Example 4: Data Validation Function

**Title**: Add Email Validation Utility

**Body**:
```markdown
Create a robust email validation function for use across the application.

## Acceptance Criteria

- AC1: Function validates email format according to RFC 5322
- AC2: Returns true for valid emails, false for invalid
- AC3: Handles common edge cases (multiple @, missing domain, etc.)
- AC4: Rejects emails with spaces or special characters
- AC5: Accepts international domain names (IDN)
- AC6: Function is pure (no side effects)
- AC7: Includes TypeScript/Python type hints
- AC8: Performance: validates email in under 1ms

## Test Cases to Cover

Valid emails:
- user@example.com
- user.name+tag@example.co.uk
- user@sub.example.com

Invalid emails:
- @example.com
- user@
- user space@example.com
- user@@example.com

## Related Files
- `src/utils/validation.py` - Validation utilities
- `src/forms/userForm.py` - Uses email validation
```

---

## Tips for Writing Good Issues

### ✅ Good Practices

1. **Clear Acceptance Criteria**: Each AC should be specific and testable
2. **Context**: Mention related files, components, or patterns
3. **Technical Details**: Include API specs, edge cases, requirements
4. **Examples**: Show expected inputs/outputs
5. **Constraints**: Mention performance, security, or business rules

### ❌ Avoid

1. Vague descriptions: "Make it better"
2. Missing acceptance criteria
3. No technical context
4. Ambiguous requirements

### Format Template

```markdown
[Brief description of the feature or fix]

## Acceptance Criteria

- AC1: [Specific testable requirement]
- AC2: [Another specific requirement]
- AC3: [Edge case or error handling]
- AC4: [Additional requirement]

## Additional Context (Optional)

- Related files: `path/to/file.py`
- Similar to: [Related feature]
- Technical constraints: [Performance, security, etc.]
- Edge cases to consider: [List edge cases]

## Related Files (Optional)

- `src/component/File.tsx` - Description
- `src/api/endpoint.py` - Description
```

---

## Using These Examples

1. Copy one of the examples above
2. Create a new issue in your GitHub repository
3. Paste the content (adjust as needed for your project)
4. Note the issue number
5. Run the test generation:
   ```bash
   curl -X POST http://localhost:8000/github/generate-tests \
     -H "Content-Type: application/json" \
     -d '{"issue_number": YOUR_ISSUE_NUMBER}'
   ```
6. Check the generated PR and tests!


