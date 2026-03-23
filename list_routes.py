import asyncio
from src.main import app

def list_routes():
    print("Listing all API Routes:")
    for route in app.routes:
        methods = getattr(route, "methods", [])
        if methods:
             print(f"{list(methods)} {route.path}")

if __name__ == "__main__":
    list_routes()
