import aiohttp
import asyncio
import time

TOKEN = "YOUR-GITHUB-API-TOKEN-KEY"
FOLLOWING_URL = "https://api.github.com/user/following"
RATE_LIMIT_URL = "https://api.github.com/rate_limit"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

async def check_rate_limit(session):
    """Check rate limit asynchronously."""
    async with session.get(RATE_LIMIT_URL, headers=headers) as response:
        data = await response.json()
        remaining = data['rate']['remaining']
        reset_time = data['rate']['reset']
        
        if remaining == 0:
            wait_time = reset_time - time.time()
            print(f"Rate limit exceeded. Waiting for {int(wait_time // 60)} minutes.")
            await asyncio.sleep(wait_time + 5)

async def unfollow_user(session, username):
    """Unfollow a user by username asynchronously."""
    await check_rate_limit(session)
    unfollow_url = f"{FOLLOWING_URL}/{username}"
    async with session.delete(unfollow_url, headers=headers) as response:
        if response.status == 204:
            print(f"Successfully unfollowed {username}")
        else:
            print(f"Error unfollowing {username}: {response.status}, {await response.json()}")

async def get_following(session, page=1):
    """Fetch the list of users currently being followed asynchronously."""
    params = {'page': page, 'per_page': 100}
    async with session.get(FOLLOWING_URL, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error fetching following list: {response.status}, {await response.json()}")
            return []

async def unfollow_all():
    """Unfollow all users asynchronously."""
    async with aiohttp.ClientSession() as session:
        page = 1
        following = []
        
        # Fetch all followed users with pagination
        while True:
            users = await get_following(session, page)
            if not users:
                break
            following.extend(users)
            page += 1

        if not following:
            print("You are not following anyone.")
            return
        
        # Unfollow users concurrently
        tasks = [unfollow_user(session, user["login"]) for user in following]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(unfollow_all())
    except KeyboardInterrupt:
        print("Operation canceled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
