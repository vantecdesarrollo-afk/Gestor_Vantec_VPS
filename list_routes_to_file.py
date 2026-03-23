from src.main import app

with open("routes.txt", "w") as f:
    for route in app.routes:
        methods = getattr(route, "methods", [])
        if methods:
            f.write(f"{list(methods)} {route.path}\n")

print("Routes saved to routes.txt")
