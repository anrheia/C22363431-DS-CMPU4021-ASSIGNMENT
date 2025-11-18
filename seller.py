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
import time
import random 

host = 'localhost'
port = 5000 # hard-coded default port
data_payload = 2048

s = "[SELLER]"

#item inventory
inventory = {
    "FLOUR": 5,
    "SUGAR": 5,
    "POTATO": 5,
    "OIL": 5
}

#current item on sale
current_item = None
sale_end_time = 0
lock = threading.Lock() #protects shared state when multiple buyers connect

def sale_timer_loop():
    while True:
        time.sleep(1)

        with lock:
            if current_item is None:
                continue

            expired = time.time() >= sale_end_time
            item = current_item

        if expired:
            print(f"{s}: Sale for {item} ended.")
            new_sale()

def new_sale():
    global current_item, sale_end_time # refers to global variable, not local

    with lock:
        available_items = [item for item, stock in inventory.items() if stock > 0]

        if not available_items:
            current_item = None 
            sale_end_time = 0
            print(f"{s}: No items left to sell.")
            return
        current_item = random.choice(available_items)

        duration = random.randint(10, 60)
        sale_end_time = time.time() + duration

    print(f"{s}: NEW SALE -> {current_item} for {duration}s. ")

def handle_client(conn,addr):

    buyer_name = conn.recv(data_payload).decode("utf-8").strip()
    print(f"{s}: New buyer connected - {buyer_name}")

    try:
        while True:
            msg = conn.recv(data_payload)

            if not msg:
                print(f"{s}: Client {buyer_name} disconnected.")
                break

            msg_decoded = msg.decode("utf-8")
            print(f"{buyer_name}: {msg_decoded}") 

            if msg_decoded.lower() == "inventory":
                item_line = [f"- {item} ({stock})" for item, stock in inventory.items()]
                items_display = "\n".join(item_line)
                reply = f"{s}: Item Inventory \n{items_display}"

            elif msg_decoded.lower() == "sale":
                with lock:
                    if current_item is None:
                        reply = f"{s}: No active sale at the moment."
                    else:
                        remaining = max(0, int(sale_end_time - time.time()))
                        stock_left = inventory.get(current_item, 0)
                        reply = (f"{s}: CURRENT SALE -> {current_item} "
                                 f"Stock: {stock_left}, time left: {remaining}s")
            else:
                reply = f"{s}: Unknown Command. Try: inventory, sale, buy, quit/exit."
            
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

    new_sale()
    timer_thread = threading.Thread(target=sale_timer_loop, daemon=True)
    timer_thread.start()

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