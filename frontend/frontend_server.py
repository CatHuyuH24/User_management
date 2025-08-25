#!/usr/bin/env python3
"""
Simple HTTP server for the User Management frontend
Serves static files and handles CORS for local development
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def start_server(port=3000):
    """Start the HTTP server"""
    
    # Change to frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    print(f"""
🚀 User Management Frontend Server Starting...

📁 Serving from: {frontend_dir}
🌐 Server URL: http://localhost:{port}
📋 Available Pages:
   • Landing Page: http://localhost:{port}/index.html
   • Sign Up: http://localhost:{port}/signup.html  
   • Login: http://localhost:{port}/login.html
   • Profile: http://localhost:{port}/profile.html
   • Server Info: http://localhost:{port}/server.html

🔧 Backend API: http://localhost:8000
📖 API Docs: http://localhost:8000/docs

Press Ctrl+C to stop the server
""")
    
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully on port {port}")
            print("=" * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python frontend_server.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 3000.")
    
    start_server(port)
