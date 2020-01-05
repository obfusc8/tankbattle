#!/usr/bin/python3
import pickle
import socket
import select
import sys
import threading


class PlayerError(Exception):
    pass


# create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# setup host information
# NETWORKING SETUP #
if len(sys.argv) > 1:
    host = sys.argv[1]
    print("Server host:", sys.argv[1])
else:
    #host = "192.168.86.38"
    host = "SAL-1908-KJ"
port = 9998


def gameThread(sender, receiver):

    GAMEON = True

    S = str(sender[1][0]) + ":" + str(sender[1][1])
    R = str(receiver[1][0]) + ":" + str(receiver[1][1])

    sender = sender[0]
    receiver = receiver[0]

    while GAMEON:

        try:
            # MESSAGE RECEIVED
            print("waiting for message from", S)
            message = sender.recv(1024)
            if not message:
                raise PlayerError("Connection lost from player")

            # ACKNOWLEDGE RECEIPT
            print("sending acknowledge to", S)
            sender.send("ACK".encode('ascii'))

            # MESSAGE SENT
            print("received:", message.decode('ascii'), "from", S)
            print("sending message to", R)
            receiver.send(message)

            # GET ACKNOWLEDGEMENT
            ack = receiver.recv(64).decode('ascii')
            if ack != "ACK":
                print(ack)

        except KeyboardInterrupt:
            print("[KeyboardInterrupt] Server was halted")
            ### END GAME ###
            GAMEON = False
            try:
                sender.close()
                receiver.close()
            except:
                pass
            break
        except ConnectionResetError:
            print("[ConnectionResetError] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
                sender.close()
                receiver.close()
            except:
                pass
            break
        except ConnectionAbortedError:
            print("[ConnectionAbortedError] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
                sender.close()
                receiver.close()
            except:
                pass
            break
        except OSError:
            print("[OSError] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
                sender.close()
                receiver.close()
            except:
                pass
            break
        except PlayerError:
            print("[PlayerError] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
                sender.close()
                receiver.close()
            except:
                pass
            break

    print("*** THREAD CLOSED ***")


def main():
    # bind to the port
    server.bind((host, port))

    # queue up to 5 requests
    server.listen(10)

    players = list()
    UP = True

    while UP:

        players.clear()

        print("Starting new session...")
        print("Waiting for 2 players to join")

        # Wait until 2 players have joined #
        while len(players) != 2:

            try:
                print(str(len(players)), "Players connected...")
                print("Waiting for a player connection...")
                # Accept connection and add to list
                player, addr = server.accept()
                print("Player connected...")
                greeting = "You are connected!".encode('ascii')
                print("Sending ack to player...")
                player.send(greeting)
                print("Adding player to roster...")
                players.append((player, addr))
            except KeyboardInterrupt:
                print("[Keyboard Interrupt] Server was halted")
                ### KILL SERVER ###
                UP = False
                try:
                    for p in players:
                        p[0].close()
                except:
                    pass
                break

            # Check to see if all players are still present
            print("Checking to see if all players are still connected")
            for p in players:
                try:
                    print("Unblocking socket")
                    p[0].setblocking(0)
                    print("Testing connection")
                    test = p[0].recv(1024)
                    print("Blocking socket")
                    p[0].setblocking(1)
                except BlockingIOError:
                    p[0].setblocking(1)
                except:
                    print("Player connection lost, removing from roster...")
                    p[0].close()
                    players.remove(p)
                    continue

        # Assign player positions and start game
        if (len(players) == 2):
            print("2 Players connected, sending player assignments")
            for n, p in enumerate(players):
                assignment = "PLAYER " + str(n + 1)
                print("Sending assignment to", assignment)
                assignment = assignment.encode('ascii')
                p[0].send(assignment)

            threading.Thread(target=gameThread, args=(players[0], players[1],), daemon=True).start()
            threading.Thread(target=gameThread, args=(players[1], players[0],), daemon=True).start()


    ### SHUTDOWN SERVER ###
    server.close()
    print("END")


if __name__ == '__main__':
    main()
