from app import create_app, db
import os
import socket

app = create_app()

def find_free_port():
    """Find a free port to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Find a free port automatically
    port = find_free_port()
    print(f"Starting Flask app on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)