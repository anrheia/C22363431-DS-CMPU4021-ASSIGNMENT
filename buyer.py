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
    
    buyer = str(input("Enter your name: "))
    b = f"[{buyer}]"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = (host,port)
    client.connect(server_address)

    client.sendall(b.encode("utf-8"))
    print(f"{b}: connected to server {host} port {port}")

    try:
        while True:
            msg = str(input(f"{b}: "))

            if not msg:
                continue

            if msg.lower() in ("quit", "exit"):
                print(f"{b}: Closing Connection...")
                break

            client.sendall(msg.encode("utf-8"))

            reply = client.recv(data_payload)
            reply_decoded = reply.decode("utf-8")

            if not reply:
                print(f"{b}: Server closed connection.")
                break

            print(f"{reply_decoded}")

    except:
        print(f"\n{b}: [INTERRUPTED BY CLIENT]")
    finally:
        client.close()
        print(f"{b}: Bye!")

if __name__ == "__main__":
    main()