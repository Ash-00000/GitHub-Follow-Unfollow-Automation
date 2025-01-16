import aiohttp
import asyncio
import time

TOKEN = "your-api-token-key"
FOLLOWERS_URL = "https://api.github.com/users/{username}/followers"
FOLLOW_URL = "https://api.github.com/user/following"
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

async def follow_user(session, username):
    """Follow a user by username asynchronously."""
    await check_rate_limit(session)
    follow_url = f"{FOLLOW_URL}/{username}"
    async with session.put(follow_url, headers=headers) as response:
        if response.status == 204:
            print(f"Successfully followed {username}")
        else:
            print(f"Error following {username}: {response.status}, {await response.json()}")

async def get_followers(session, username, page=1):
    """Fetch the list of followers of a user asynchronously."""
    params = {'page': page, 'per_page': 100}
    url = FOLLOWERS_URL.format(username=username)
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error fetching followers list: {response.status}, {await response.json()}")
            return []

async def follow_all(username):
    """Follow all followers of the given user asynchronously."""
    async with aiohttp.ClientSession() as session:
        page = 1
        followers = []

        # Fetch all followers with pagination
        while True:
            users = await get_followers(session, username, page)
            if not users:
                break
            followers.extend(users)
            page += 1

        if not followers:
            print(f"{username} has no followers.")
            return

        # Follow users concurrently
        tasks = [follow_user(session, user["login"]) for user in followers]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    target_username = input("Enter the username whose followers you want to follow: ").strip()
    try:
        asyncio.run(follow_all(target_username))
    except KeyboardInterrupt:
        print("Operation canceled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
