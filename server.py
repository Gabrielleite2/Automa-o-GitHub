import http.server
import socketserver
import json
import subprocess
import os
import threading
import webbrowser

PORT = 8000
DIRECTORY = "."

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching so the dashboard refreshes properly
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/api/refresh':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                print("\n[Server] Handling refresh request...")
                
                # 1. Run Scraper
                print("[Server] Running scrape_reddit.py...")
                subprocess.run(["python", os.path.join("execution", "scrape_reddit.py")], check=True)
                
                # 2. Re-generate Dashboard html
                print("[Server] Running generate_dashboard.py...")
                subprocess.run(["python", os.path.join("execution", "generate_dashboard.py")], check=True)
                
                # 3. Inform client success
                response = {"status": "success", "message": "Data refreshed successfully."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print("[Server] Refresh complete.\n")
                
            except Exception as e:
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[Server] Error during refresh: {e}\n")
        elif self.path == '/api/send_email':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                print("\n[Server] Handling send_email request...")
                result = subprocess.run(
                    ["python", os.path.join("execution", "send_email.py"), post_data], 
                    capture_output=True, text=True, check=True
                )
                
                # Check if output is clean JSON by attempting to parse, to avoid breaking frontend
                try:
                    # just testing if valid JSON
                    output_json = json.loads(result.stdout.strip())
                    output = result.stdout.strip()
                except json.JSONDecodeError:
                    output = json.dumps({"status": "error", "message": f"Non-JSON response from script: {result.stdout.strip()}"})

                self.wfile.write(output.encode('utf-8'))
                print(f"[Server] Send email process complete.\n")
            except subprocess.CalledProcessError as e:
                response = {"status": "error", "message": f"Process failed: {e.stderr}"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[Server] Send error: {e.stderr}\n")
            except Exception as e:
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[Server] Server execution error: {str(e)}\n")
        else:
            self.send_response(404)
            self.end_headers()

def open_browser():
    webbrowser.open(f'http://localhost:{PORT}/reddit_dashboard.html')

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    # Start the server
    handler = RequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"==================================================")
        print(f"Server started at http://localhost:{PORT}")
        print(f"Serving files from {os.path.abspath(DIRECTORY)}")
        print(f"Press Ctrl+C to stop.")
        print(f"==================================================")
        
        # Open browser automatically after a tiny delay
        threading.Timer(0.5, open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
