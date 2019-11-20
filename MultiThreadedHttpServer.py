# Erik Safford
# Multi Threaded Http Server
# CS 455
# Fall 2019
# C:/Users/kired/AppData/Local/Programs/Python/Python37-32/python.exe "C:\Users\kired\Documents\GitHub\Multithreaded-HTTP-Server\MultiThreadedHttpServer.py"

import socket
import time
import threading
import signal
import sys
PACKET_SIZE = 1024 # Number of bytes to read from client requests
PORT = 8085 # Port server socket will be bound to, 80 is default port for http

# Function handler for SIGINT (ctrl+C), server must try to serve another connection before SIGINT stops the script 
# (F5 on localhost in browser after ctrl+C)
def shutdown_server(signal, frame):
   print("Server shutdown command recieved (ctrl+C), shutting down/closing server...")
   s.close()
   sys.exit(1)
   
# Generates http response headers based on http protocol version and response code
def generate_header(response_code, http_version, file_type):
   header = ''
   time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
   # If http version is 1.0, close connection after serving response
   if http_version == '1.0':  
      if response_code == 200:
         header += 'HTTP/1.0 200 OK\n'
      if response_code == 404:
         header += 'HTTP/1.0 404 Not Found\n'
      header += 'Date: ' + time_now + '\n'
      header += 'Server: Erik\'s Python Server\n'
      header += 'Connection: close\n'  # Signal that connection will be closed after completing the request
   # If http version is 1.1, keep connection alive after serving response
   elif http_version == '1.1':  
      if response_code == 200:
         header += 'HTTP/1.1 200 OK\n'
      elif response_code == 404:
         header += 'HTTP/1.1 404 Not Found\n'
      header += 'Date: ' + time_now + '\n'
      header += 'Server: Erik\'s Python Server\n'
      header += 'Connection: keep-alive\n'  # Signal that connection will be kept alive after completing the request

   if file_type == 'html':
      header += 'Content-Type: text/html\n\n'
   elif file_type == 'jpg' or file_type == 'jpeg':
      header += 'Content-Type: image/jpeg\n\n'
   elif file_type == 'png':
      header += 'Content-Type: image/png\n\n'
   else:
      header += 'Content-Type: ' + file_type + '\n\n'
   return header

# Read, decode, and respond to client through socket connection
def deal_with_client(client_socket, address):
   persistent_connection = False
   while True:
      try:
         # Recive request (packet) from client and decode
         message = client_socket.recv(PACKET_SIZE).decode()  

         # If no message recieved from client close connection and break
         if not message:  
            print("No message recieved, closing client connection...")
            client_socket.close()
            break

         # Get request type and version from client request
         try:
            request_method = message.split(' ')[0]     
            http_version = message.split('/')[2][:3]
            print("Method: " + request_method + '\n')
            print("Request Body: \n" + message)
            print("HTTP Version: " + http_version + '\n')
         except Exception as e:
            print("Error getting request method/http version/message")
            print("Closing client socket...")
            client_socket.close()
            break

         # Set the socket to timeout after 10 seconds if http version is 1.1 (persistent connection)
         if http_version == '1.1' and persistent_connection == False:
            persistent_connection = True
            client_socket.settimeout(10)

         # Only want the server to respond to GET or HEAD requests
         if request_method == "GET" or request_method == "HEAD":
            try:
               file_requested = message.split(' ')[1]   # I.e. GET /index.html (split on space)
               if file_requested == "/":  # / means request for the base html page 
                  file_requested = "/index.html"

               file_type = file_requested.split('.')[1]  # Get filetype of request
               print("File requested by client: " + file_requested)
               print("Filetype of file: " + file_type)
            except Exception as e:
               print("Error getting filetype/requested file")
               print("Closing client socket...")
               client_socket.close()
               break

            filepath_to_serve = "template" + file_requested  # Base page is in template folder
            print("Filepath to serve: " + filepath_to_serve + '\n')

            # Attempt to load and serve file content
            # If just serving a html file
            if file_type == 'html':
               try:
                  if request_method == "GET":  # Only want to read if was GET request
                     file = open(filepath_to_serve, 'r')
                     response_data = file.read()
                     file.close()
                  response_header = generate_header(200, http_version, file_type)  # Make 200 OK response
                  response_code = 200
               except Exception as e:  # If exception is thrown by attempting to open file that doesnt exist
                  print("File not found, serving 404 file not found response")
                  response_header = generate_header(404, http_version, file_type)  # Make 404 file not found response
                  response_code = 404

               # If request was GET and requested file was read successfully, append the file to the response header
               if request_method == "GET" and response_code == 200:
                  print("Sending: \n" + response_header + response_data)
                  # Encode the response in bytes format so can be sent to client
                  client_socket.send(response_header.encode() + response_data.encode())
               # Else simply return the response header (HEAD request - 200/404)
               else:
                  print("Sending: \n" + response_header)
                  client_socket.send(response_header.encode())
            # Else if trying to serve up an image
            elif file_type == "jpg" or file_type == "jpeg" or file_type == "png":
               try:
                  if request_method == "GET":  # Only want to read if was GET request
                     file = open(filepath_to_serve, 'rb')  # Open image in bytes format
                     response_data = file.read()
                     file.close()
                  response_header = generate_header(200, http_version, file_type)  # Make 200 OK response
                  response_code = 200
               except Exception as e:  # If exception is thrown by attempting to open file that doesnt exist
                  print("Image not found/couldn't be opened, serving 404 file not found response")
                  response_header = generate_header(404, http_version, file_type)  # Make 404 file not found response
                  response_code = 404

               # If request was GET and requested file was read successfully, send encoded header and image
               if request_method == "GET" and response_code == 200:
                  print("Sending image with: \n" + response_header)
                  client_socket.send(response_header.encode())
                  client_socket.send(response_data)  # Image already encoded since open as 'rb' (b is bytes)
               # Else simply return the response header (200/404)
               else:
                  print("Sending: \n" + response_header)
                  client_socket.send(response_header.encode())
            # Else trying to request/open an invalid file type
            else:
               print("Invalid requested filetype: " + file_type)
               response_header = generate_header(404, http_version, file_type)
               print("Sending: \n" + response_header)
               client_socket.send(response_header.encode())

            # If http version 1.0, want to close connection after completing request
            if http_version == '1.0':
               print("Closing client socket...")
               client_socket.close()
               break
            # Else if http version 1.1, want to keep persistent connection after completing request
            elif http_version == '1.1' and persistent_connection == True:
               print("http 1.1: peristent connection, continuing to recieve requests...")
         # Else if the request was not a GET or HEAD request, error and close
         else:
            print("Error: Unknown HTTP request method: " + request_method)  # 501 Not Implemented
            print("Closing client socket...")
            client_socket.close()
            break
      # Exception is thrown once the socket connection times out (http 1.1 - persistent connection)
      except socket.timeout:
         print("Socket connection timeout reached (10 seconds), closing client socket...")
         client_socket.close()
         break

# Set up ctrl+C command inturrupt
signal.signal(signal.SIGINT, shutdown_server)

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Make socket address reusable
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
print("Socket successfully created")

# Next bind localhost IP to the port
try:
   s.bind(('localhost', PORT))
   print("socket binded to", PORT)
except Exception as e:  # Exit if socket could not be bound to port
   print("Error: could not bind to port: " + PORT)
   s.close()
   sys.exit(1)

# Have the socket listen for up to 5 connections
s.listen(5)
print("socket is listening for connections, Ctrl+C and refresh localhost in browser to close server\n")

while True:
   # Accept new connection from incoming client
   client_socket, address = s.accept()  
   print('Got connection from',address,'\n')
   # Create new thread to deal with client request, and continue accepting connections
   threading.Thread(target=deal_with_client, args=(client_socket, address)).start()
