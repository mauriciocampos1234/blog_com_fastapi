import anyio
import jwt
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.config import settings

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(base_url='http://test', transport=transport) as client:
        r = await client.post('/auth/login', json={'user_id': 1})
        token = r.json()['access_token']
        try:
            decoded = jwt.decode(token, settings.jwt_secret, audience=settings.jwt_audience, algorithms=[settings.jwt_algorithm])
            print('decoded_ok', decoded)
        except Exception as e:
            print('decode_error', type(e).__name__, str(e))

anyio.run(main)
