This program implements a simple HTTP server using only Socket API. At a high level, a web server listens for connections on a socket (bound to a specific port on a host machine - localhost:8085), then clients connect to this socket and use HTTP protocol to retrieve files from the server (i.e. index.html).

When the server gets a request for /index.html, it will prepend the location “template/” to the specified file and determine if the file exists. That is, “template/index.html” is the file requested. If the file does not exist, a file not found error is returned. If a file is present, an HTTP OK message is returned along with the contents of a file.

The web server translates "GET /" to "GET /index.html". That is, “template/index.html” is assumed to be the filename if no explicit filename is present. Therefore, the two URL's " http://localhost " and " http://localhost/index.html " return equivalent results.

The web server only accepts GET and HEAD type requests, if it’s a HEAD request and the file requested is present, an HTTP OK message is returned without the contents of a file. If it’s a POST, PUT, or DELETE request, a method not allowed error is returned.

If HTTP/1.1 is requested (instead of HTTP/1.0), the web server will make a "persistent" connection for pipelining requests. After the results of a single request are returned (e.g., index.html), the server leaves the connection open for 10 seconds, allowing the client to reuse that connection to make subsequent requests. 

The web server is multi-threaded, spawning a new thread for each incoming connection to parse the request, transmit the file, etc.

High Level Pseudocode:

- Forever loop (listen for connections)
  - Accept new connection from incoming client
    - Parse the HTTP request
    - Ensure well-formed request (return error and skip the rest steps otherwise)
    - Ensure method is allowed (return error and skip the rest steps otherwise)
    - Determine if target file exists (return error and skip the rest steps otherwise)
    - If method is GET, transmit OK message and contents of file to socket (by performing reads on the file and writes on the socket); if method is HEAD, transmit OK message to socket
  - Close the connection

# Example console output of HTTP requests from browser:
![Alt text](consoleoutput.png?raw=true)

# Example HTTP response to browser:
![Alt text](example.png?raw=true)
