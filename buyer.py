"""
Docstring for C22363431-DS-CMPU4021-ASSIGNMENT.buyer

Student ID: C22363431
Name: Jana Sy
Date: 17/11/25
Module: Distributed Systems, CMPU4021

"""

import socket
import sys
import threading # for the background receiver of my broadcast

host = 'localhost'
port = 5000
data_payload = 2048

# a background thread that listen for messages from the seller and prints them
def receiver(client, b):
    try:
        while True:
            seller_reply = client.recv(data_payload)

            if not seller_reply:
                print(f"\n> Server closed connection.")
                break
            
            msg = seller_reply.decode("utf-8")

            for line in msg.splitlines():
                if line.strip() == "":
                    continue
                print(f"\n{line}")

            print(f"> ", end="", flush=True)
   
    except Exception as e:
        pass

def main():
    buyer = input("Enter your name: ")
    b = f"{buyer}"

    port_num = input("Enter port for this shop (e.g 5000): ").strip()
    if not port_num:
        port_num = "5000"

    port = int(port_num)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = (host,port)
    client.connect(server_address)

    client.sendall(b.encode("utf-8"))
    print(f"{b}, you have connected to shop!")

    # start the background receiver thread
    recv_thread = threading.Thread(target=receiver, args=(client, b), daemon=True)
    recv_thread.start()

    try:
        while True:
            print(f"> ", end="", flush=True)
            msg = input().strip()   

            if not msg:
                continue

            if msg.lower() in ("quit", "exit"):
                print(f"> Closing Connection...")
                break

            client.sendall(msg.encode("utf-8"))

            # moved the replies and broadcast to def receiver()

    except:
        print(f"\n> [INTERRUPTED BY CLIENT]")
    finally:
        client.close()
        print(f"[SELLER]: Bye!")

if __name__ == "__main__":
    main()