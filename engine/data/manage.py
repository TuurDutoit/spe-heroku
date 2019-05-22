from .routes.manage import refresh_routes_for

def handle_change(change):
    if not change:
        return
    if change['type'] == 'object':
        refresh_routes_for(change['object'], change['records'])
