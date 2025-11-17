"""
Docstring for C22363431-DS-CMPU4021-ASSIGNMENT.seller

Student ID: C22363431
Name: Jana Sy
Date: 17/11/25
Module: Distributed Systems, CMPU4021

"""

import socket
import sys
import argparse
import threading

host = 'localhost'
port = 5000 # hard-coded default port
data_payload = 2048

s = "[SELLER]"

def handle_client(conn,addr):
    print(f"{s}: New client connected - {addr}")

    try:
        while True:
            msg = conn.recv(data_payload)

            if not msg:
                print(f"{s}: Client {addr} disconnected.")
                break

            msg_decoded = msg.decode("utf-8")
            print(f"{s}: From {addr} - {msg_decoded}")

            reply = f"{s}: welcomes you."
            conn.sendall(reply.encode("utf-8"))

    except Exception as e:
        print(f"{s}: Error with client {addr}")
    finally:
        conn.close()
        print(f"{s}: Connection with client {addr} closed.")
    return

def main():

    # For a TCP* socket, AF_INET = internet address family for IPV4, SOCK_STREAM = socket type for TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)

    # setsockopt: makes it so that it avoids the bind() exception error where it says address is already in use

    #binds the socket to the address above 
    print(f"Starting TCP Connection for {s} %s port %s" % server_address)
    server.bind(server_address)

    # enables a server to accept connections 
    server.listen()
    print(f"{s} listening for connections...")

    try:
        while True:
            conn, addr = server.accept()
            print(f"{s} accepted connection by {addr}")

            # creates a new thread, 
            # target=handle_client -> what function the thread runs
            # args=(conn, addr) -> passes the arguments to the target fns
            # daemon=True -> background thread that doesnt stop the program from exiting
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            #starts the actual thread, if .start() isn't called, the thread exists but isn't run.
            client_thread.start()

    except KeyboardInterrupt:
        print(f"{s} Shutting Down...")

    finally:
        server.close()
        print(f"{s} closed.")


if __name__ == "__main__":
    main()