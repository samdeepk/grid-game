# Testing Guide

This document describes the testing setup for frontend-to-backend integration tests.

## Backend Integration Tests

### Setup

1. **Install dependencies:**
   ```bash
   cd server/py3
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   pytest test_integration.py -v
   ```

3. **Run with coverage:**
   ```bash
   pytest test_integration.py --cov=. --cov-report=html
   ```

### Test Structure

The backend integration tests (`test_integration.py`) use:
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client for testing FastAPI
- **aiosqlite** - In-memory SQLite for test database

### Test Coverage

The integration tests cover:

1. **User Endpoints**
   - Creating users with/without icons
   - Error handling

2. **Session Endpoints**
   - Creating sessions
   - Getting sessions
   - Listing sessions with filters
   - Joining sessions
   - Error cases (not found, already full, etc.)

3. **Move Endpoints**
   - Making valid moves
   - Turn validation
   - Coordinate validation
   - Cell occupancy validation
   - Win condition detection
   - Draw condition detection

4. **End-to-End Flow**
   - Complete game flow from creation to completion

### Running Specific Tests

```bash
# Run only user tests
pytest test_integration.py::TestUserEndpoints -v

# Run only session tests
pytest test_integration.py::TestSessionEndpoints -v

# Run only move tests
pytest test_integration.py::TestMoveEndpoints -v

# Run only E2E tests
pytest test_integration.py::TestEndToEndFlow -v
```

## Frontend API Integration Tests

### Setup

1. **Install dependencies:**
   ```bash
   cd webapp/grid-react
   npm install
   ```

2. **Run tests:**
   ```bash
   npm test
   ```

3. **Run in watch mode:**
   ```bash
   npm run test:watch
   ```

4. **Run with coverage:**
   ```bash
   npm run test:coverage
   ```

### Test Structure

The frontend API tests (`src/utils/__tests__/api.test.ts`) use:
- **Jest** - Testing framework
- **@testing-library/jest-dom** - DOM matchers
- **Mocked fetch** - API mocking

### Test Coverage

The frontend tests cover:

1. **API Client Functions**
   - `createUser()` - User creation with/without icon
   - `createSession()` - Session creation
   - `getSession()` - Getting session by ID
   - `joinSession()` - Joining a session
   - `makeMove()` - Making moves
   - `listSessions()` - Listing sessions with filters
   - `pollSession()` - Polling functionality

2. **Error Handling**
   - 404 errors
   - 409 conflicts
   - 400 validation errors

## End-to-End Testing

For true end-to-end testing (frontend + backend), you can:

1. **Start backend server:**
   ```bash
   cd server/py3
   uvicorn main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd webapp/grid-react
   npm run dev
   ```

3. **Use Playwright or Cypress** for browser-based E2E tests (not included in this setup)

## Test Database

The backend tests use an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) which:
- Is created fresh for each test
- Is automatically cleaned up after each test
- Doesn't require a real database connection
- Runs faster than PostgreSQL tests

## Continuous Integration

To run tests in CI:

```bash
# Backend
cd server/py3
pip install -r requirements.txt
pytest test_integration.py -v

# Frontend
cd webapp/grid-react
npm install
npm test
```

## Writing New Tests

### Backend Test Example

```python
@pytest.mark.asyncio
async def test_my_new_endpoint(client: AsyncClient, test_user):
    """Test description."""
    response = await client.post(
        "/my-endpoint",
        json={"key": "value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["expected"] == "value"
```

### Frontend Test Example

```typescript
it('should do something', async () => {
  const mockResponse = { id: '123', name: 'Test' };
  
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: async () => mockResponse,
    headers: new Headers({ 'content-type': 'application/json' }),
  } as Response);

  const result = await myApiFunction();
  expect(result).toEqual(mockResponse);
});
```

## Troubleshooting

### Backend Tests

- **Import errors**: Make sure all dependencies are installed
- **Database errors**: Tests use in-memory DB, no setup needed
- **Async errors**: Make sure `@pytest.mark.asyncio` is used

### Frontend Tests

- **Module not found**: Run `npm install`
- **Jest config errors**: Check `jest.config.js` and `jest.setup.js`
- **Mock errors**: Ensure `global.fetch` is properly mocked

