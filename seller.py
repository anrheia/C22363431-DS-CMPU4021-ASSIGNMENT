"""
Docstring for C22363431-DS-CMPU4021-ASSIGNMENT.seller

Student ID: C22363431
Name: Jana Sy
Date: 17/11/25
Module: Distributed Systems, CMPU4021

"""
import socket
import sys  
import threading
import time
import random 

host = 'localhost'
port = 5000 # hard-coded default port
data_payload = 2048

s = None
buyers = [] # list of all active buyers

min_stock = 1
max_stock = 20

#item inventory dict
inventory = {
    "FLOUR": random.randint(min_stock, max_stock),+
    "SUGAR": random.randint(min_stock, max_stock),
    "POTATO": random.randint(min_stock, max_stock),
    "OIL": random.randint(min_stock, max_stock)
}

#current item on sale
current_item = None
sale_end_time = 0
lock = threading.Lock() #protects shared state when multiple buyers connect

# sends an automatic message to all connected buyers
def broadcast(msg):
    dead = [] # gonna be a list of all broken connections

    with lock:
        for b in buyers:
            try:
                b.sendall((msg + "\n").encode("utf-8"))
            except OSError:
                dead.append(b) #if the buyer (b) is disconnected move them to dead list also

        for b in dead:
            if b in buyers:
                buyers.remove(b) # remove the disconnected buyer from active clients lsit
                try:
                    b.close()
                except OSError:
                    pass

"""

SHOP PORTION: SETS UP NEW SALE ITEM + TIMER

"""

def sale_timer_loop():
    while True:
        time.sleep(1)

        with lock:
            if current_item is None:
                continue

            expired = time.time() >= sale_end_time
            item = current_item

        if expired:
            end_msg = f"{s}: Sale for {item} ended."
            print(end_msg)
            broadcast(end_msg)
            new_sale()

def new_sale():
    global current_item, sale_end_time # refers to global variable, not local

    with lock:
        # if the item in inventory's stock is greater than 0, add them to available items
        available_items = [item for item, stock in inventory.items() if stock > 0]

        # if all the stock from the seller is gone
        if not available_items:
            current_item = None 
            sale_end_time = 0
            print(f"{s}: No items left to sell.")
            return
        # current item will be a random item in available_items which has stock
        current_item = random.choice(available_items)

        duration = random.randint(10, 60)
        sale_end_time = time.time() + duration

    msg = f"{s}: NEW SALE -> {current_item} for {duration}s. "
    print(msg)
    broadcast(msg)

"""

HANDLES ALL CLIENT/BUYER INPUTS

"""

def handle_client(conn,addr):
    buyer_name = conn.recv(data_payload).decode("utf-8").strip()
    print(f"{s}: New buyer connected - {buyer_name}")

    with lock:
        buyers.append(conn) # if a new buyer has connected, add them to the buyers list

    try:
        while True:
            msg = conn.recv(data_payload)

            if not msg:
                print(f"{s}: Client {buyer_name} disconnected.")
                break

            msg_decoded = msg.decode("utf-8")
            print(f"{buyer_name}: {msg_decoded}") 

            # if the messsage is inventory, show all items in stock
            if msg_decoded.lower() == "inventory":
                item_line = [f"- {item} ({stock})" for item, stock in inventory.items()]
                items_display = "\n".join(item_line)
                reply = f"{s}: Item Inventory \n{items_display}"

            # if the message is sale, show active item on sale and time remaining on sale
            elif msg_decoded.lower() == "sale":
                with lock:
                    if current_item is None:
                        reply = f"{s}: No active sale at the moment."
                    else:
                        remaining = max(0, int(sale_end_time - time.time()))
                        stock_left = inventory.get(current_item, 0)
                        reply = (f"{s}: CURRENT SALE -> {current_item} "
                                 f"Stock: {stock_left}, time left: {remaining}s")
                        
            # if the message starts with buy, split the message in parts
            elif msg_decoded.lower().startswith("buy"):
                parts = msg_decoded.strip().split()

                #if the message is not in 3 parts send the reply
                if len(parts) != 3:
                    reply = f"{s}: USAGE - buy <ITEM> <AMOUNT>. EXAMPLE - buy potato 3"
                    conn.sendall((reply + "\n").encode("utf-8"))
                    continue

                item = parts[1].upper()
                        
                try:
                    amount = int(parts[2])
                # if the amount isnt a number, state reply
                except ValueError:
                    reply = f"{s}: Amount must be a number. EXAMPLE - buy flour 2"
                    conn.sendall((reply + "\n").encode("utf-8"))
                    continue
                
                #if the amount is less than zero state reply
                if amount <= 0:
                    reply = f"{s}: Amount must be greater than 0"
                    conn.sendall((reply + "\n").encode("utf-8"))
                    continue
            
                purchase_success = False
                remaining_after = None 

                with lock:
                    # if item not in inventory, tell user to check inventory
                    if item not in inventory:
                        reply = f"{s}: Unknown item '{item}'. Try: inventory."

                    # if the item is not for sale tell user to check sale
                    elif current_item is not None and item != current_item:
                        reply = f"{s}: {item} is currently not on sale. Try: sale."

                    # if the amount stated to buy is greater than the amount on stock tell them the available item on stock
                    elif inventory[item] < amount:
                        reply = f"{s}: Not enough {item} in stock, Available {inventory[item]}."

                    # else proceed w purchase
                    else:
                        inventory[item] -= amount
                        remaining_after = inventory[item]
                        purchase_success = True
                        reply = f"{s}: Purchase successful! You bought {amount} stocks of {item}."
                
                conn.sendall((reply + "\n").encode("utf-8"))

                #if purchase was succesful send a broadcast to other buyers
                if purchase_success:
                    purchase_msg = f"{s}: {buyer_name} bought {amount} stocks of {item}. Remaining {item} stocks: {remaining_after} "
                    broadcast(purchase_msg)

                    if remaining_after == 0 and item == current_item:
                        new_sale()
                    
                continue

            elif msg_decoded.lower() == "commands":
                reply = f"{s}: Try: inventory, sale, buy, buy <ITEM> <AMOUNT>, quit/exit,."            
            else:
                reply = f"{s}: Unknown Command. Try: commands, inventory, sale, buy, quit/exit."
            
            conn.sendall((reply + "\n").encode("utf-8"))
            
    except Exception as e:
        pass

    finally:
        conn.close()
        print(f"{s}: Connection with client {addr} closed.")

    return

"""

MAIN CONSOLE, HANDLES THE CONNECTION AND THREADS

"""

def main():

    global s, port

    seller = input("Enter your name, seller: ")
    if not seller:
        name = "SELLER"
    s = f"[{seller}]"

    port_num = input("Enter port for this shop (e.g 5000): ").strip()
    if not port_num:
        port_num = "5000"

    port = int(port_num)

    # For a TCP* socket, AF_INET = internet address family for IPV4, SOCK_STREAM = socket type for TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)

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