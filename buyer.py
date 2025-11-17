"""
Docstring for C22363431-DS-CMPU4021-ASSIGNMENT.buyer

Student ID: C22363431
Name: Jana Sy
Date: 17/11/25
Module: Distributed Systems, CMPU4021

"""

import socket
import sys
import argparse

host = 'localhost'
port = 5000
data_payload = 2048

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = (host,port)
    client.connect(server_address)
    print("Buyer connected to server %s port %s" % server_address)

    msg = "Buyer says: Hello World!"
    client.sendall(msg.encode("utf-8"))

    reply_data = client.recv(data_payload)
    reply_decoded = reply_data.decode("utf-8")
    print(f"Buyer received a message: {reply_decoded}")

    client.close()
    print("Buyer has closed the connection.")

if __name__ == "__main__":
    main()