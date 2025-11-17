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

host = 'localhost'
port = 5000 # hard-coded default port
data_payload = 2048

def main():

    # For a UDP socket, AF_INET = internet address family for IPV4, SOCK_STREAM = socket type for TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    #binds the socket to the address above ^

    print("Starting TCP Connection for server %s port %s" % server_address)
    server.bind(server_address)

    # enables a server to accept connections 
    server.listen()
    print("Seller listening for connections...")
    conn, addr = server.accept()
    print(f"Seller accepted connection by {addr}")

    msg_data = conn.recv(data_payload)
    msg_decoded = msg_data.decode("utf-8")

    print(f"Seller received a message: {msg_decoded}")

    seller_reply = "Seller says: Hello Buyer!"
    conn.sendall(seller_reply.encode("utf-8"))

    conn.close()
    server.close()
    print("Seller has closed the connection.")


if __name__ == "__main__":
    main()