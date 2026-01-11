import anyio
import asyncio
from httpx import ASGITransport, AsyncClient
from src.main import app
import src.security as s


async def main():
    print('jwt_audience', s.settings.jwt_audience)
    print('jwt_issuer', s.settings.jwt_issuer)
    print('jwt_alg', s.settings.jwt_algorithm)

    transport = ASGITransport(app=app)
    async with AsyncClient(base_url='http://test', transport=transport) as client:
        r = await client.post('/auth/login', json={'user_id': 1})
        token = r.json()['access_token']
        decoded = await s.decode_jwt(token)
        print('decode_direct', decoded)

        r2 = await client.get('/posts/', params={'published': 'on', 'limit': 10}, headers={'Authorization': f'Bearer {token}'})
        print('posts', r2.status_code, r2.text)

anyio.run(main)
