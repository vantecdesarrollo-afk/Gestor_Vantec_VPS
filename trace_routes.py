from src.main import app
import inspect

with open("route_trace.txt", "w") as f:
    for route in app.routes:
        methods = getattr(route, "methods", [])
        if methods:
             f.write(f"Route: {route.path} {list(methods)}\n")
             if hasattr(route, "endpoint"):
                  endpoint = route.endpoint
                  module = inspect.getmodule(endpoint)
                  f.write(f"  Endpoint: {endpoint.__name__}\n")
                  if module:
                       f.write(f"  Module: {module.__file__}\n")
                       try:
                            lines, start = inspect.getsourcelines(endpoint)
                            f.write(f"  Line: {start}\n")
                       except Exception:
                            f.write("  Line: Unknown\n")
                  else:
                       f.write("  Module: Unknown\n")
             f.write("\n")

print("Route trace saved to route_trace.txt")
