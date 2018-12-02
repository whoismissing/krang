#!/usr/bin/python3
# Tested on python3.6.5

import socket
import subprocess
import time
# Used to send exit to program
import sys
import signal 
# Used to check if directory exists - otherwise create
import os 
# Used to generate seed and trigger mutations
import random
# Get functions for genetic algorithm from local bebop.py
from bebop import init_population, fitness, crossover, mutate

# Code to shutdown program gracefully from keyboard interrupt
def signal_handler(signal, frame):
    print("\n[EXIT] Got CTRL-C, exiting session...")
    sys.exit(0)

def print_cool_banner():
    banner = """
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMmdyyyyyyyyhhdmNNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd+............-:+ymMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNdyyyyo:-//////:::::-.../+ymmMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNmds:......:+-........--:://///+ooydmMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMNdo//:::........-.-/::::::::-...-/o+/////+ydmMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMm+-...............//-......--:://+///////////+ymNMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMms///..-............----..........:++////////////osmNMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMNdo:....-:-..........//::::///////:///////////////////+smMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMMNds+/+/..----.:..-::///:..-.............-/+oo///-////////////sNMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMMmo-.....--.....-.:+-.........-:::::---....:///:::.-///////////omMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMMMd+.......:........-.........-//------:://////:-.....-://+//////+dMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMMMNdy-......--.........---.......-...........-+o:......--.:/+s//////+hmNMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMms/-+....................----.......---......://-.......--://soo+//////yNMMMMMMMMMMMMMMMM
    MMMMMMMMMMNs-...........................:...-:/::://////+/:........../////////////odMMMMMMMMMMMMMMMM
    MMMMMMMMMMy--:..........................--..--.........:+/-.........://:://////////dMMMMMMMMMMMMMMMM
    MMMMMMMMMh::yy+-.......:..........-.........-:////////::-..........:/--.-//////s//+dMMMMMMMMMMMMMMMM
    MMMMMMMMMNhhs::o......---...:/-...://-......---.......-:/-.........-....-///////yoyMMMMMMMMMMMMMMMMM
    MMMMMMMMMMMd/.+:..../o/....//.......:s.......-::::::::..................://////+s/shMMMMMMMMMMMMMMMM
    MMMMNdyymNMy..o.....-o.....+........-:+......--------:/-..............-:///////+///sNMMMMMMMMMMMMMMM
    MMMdo/++odMy-.:....../-----...........+-............................-://///////////smMMMMMMMMMMMMMMM
    MMNo:/ysymMNy//......:::--//..........+...........-:...........--:::////s//////////+oymMMMMMMMMMMMMM
    MMy--/+smNMMh:...........//-........:////-.......-//.......---::////+oo++/////////////sNMMMMMMMMMMMM
    MMs..///+shmo...--......//.-........-...-+:.....--o.......---://++++////+/////////////odMMMMMMMMMMMM
    MMm+.:////+ss-.--.../:-//..+:::++++/:---..//----/+s.......-//+////++o+//+s+////////////hMMMMMMMMMMMM
    MMMh:..:///ydo-:.....::o/---++:so+++osys+:-:/+::/+o:----:///:////////////s+s///////////smMMMMMMMMMMM
    MMMNh/..://+oo.---......-:::-..-+ooo+osyyso////+o+///++++///+ooosso+/////+/+o///////////ymMMMMMMMMMM
    MMMMMm+.:////s-..-..............-:/+ooosyy+oo+++//+o++ssoooyhs+os+ooo//////s+////////ss+/omMMMMMMMMM
    MMMMMMs..--/:/o:--..-.......-..-///////+/---s+/////+s++yysssssoo//////////++/////////ymdyhNMMMMMMMMM
    MMMMMm+.....---+/-..:-...../+:++++/--.......---::---:/+oo++++++//////////////////////+yMMMMMMMMMMMMM
    MMMMMmo........///+//:/-..-hyhyyyyhhyso++/::::/o:---/:--:////::/+os//////////////+++ohNMMMMMMMMMMMMM
    MMMMMMd/-........./....-...yyyyyysoooooosyyhhhhhhyyyyo+/:---/oyhhhos/////////////+osshmMMMMMMMMMMMMM
    MMMMMMMmh/.................:os/-y//o++ooo+++/////+osyyyyyyyyhyyyyh+s////////////////+osyhmMMMMMMMMMM
    MMMMMMMMMy-..............-....--::::::-.....------../osy+/hy/h/oy+//////////////////+/////yNMMMMMMMM
    MMMMMMMMMNs:-..-.........:-.......:-...-:/+++++++++/////++o++++////////++/////////////////+hmNMMMMMM
    MMMMMMMMMMNmdhs/-........:/:--....-:::::-.-------:/ooooo+//////////////o+/////+////////////::odNMMMM
    MMMMMMMMMMMMMMNh+-.....-/////os+::::::::+:........://////////////s+/////ss////s+//////+o+//////+hMMM
    MMMMMMMMMMMMMMMMNds+///+oyhhmmNMNmNNNNNNmo.-:/so///:+oossyyyyyyhmdyssssydNmhsosdso//s+soo++o////smMM
    MMMMMMMMMMMMMMMMMMMMMmNNMMMMMMMMMMMMMMMNd+:yNNMMdo-+mNMMMMMMMMMMMMMMMMMMMMMMMmNMMNmmhso++/////:-omMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNs--yMMMMMd+smMMMMMMMMMMMMMMMMMMMMMMNhssyhhyhho////////:--yMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMdyhNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNhoo+//////////////+odMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNmhoo+++++ooyhmNMMMMMM
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNmmmNNNMMMMMMMMMMM"""
    # Most important line of code here - Added the most essential feature 
    # Print the cool banner
    print("\x1b[0;31;40m" + banner + "\x1b[0m")
    print()

def main():
    # Prepare initial configuration of target IP and port to connect to and process name
    TCP_IP = "localhost"
    TCP_PORT = 8080
    target = './server'

    # Prepare seed for replayability - deterministic
    seed = random.random()
    random.seed(seed)

    print_cool_banner()
    
    # Check if dir exists to store crashes in - otherwise make it exist
    print("Does the directory crashem/ exist?")
    if not os.path.exists("crashem/"):
        # Ask user to create directory, otherwise exit
        print("crashem/ does not exist so would you like to make the directory?")
        user_choice = input("[Y] or [N] ")
        if user_choice == str("Y"):
            os.makedirs("crashem/")
            print("Created directory")
        else:
            print("Cannot continue unless the directory is made so exiting...")
            sys.exit(0)
    else:
        print("Directory already exists! Continuing...")

    # Close program gracefully from keyboard interrupt
    signal.signal(signal.SIGINT, signal_handler)

    # Prepare initial payloads to apply genetic algorithm
    population = init_population()

    # Spawn initial target process to be fuzzed
    proc = subprocess.Popen(target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        try:
            # This sleep should match the timeout of proc.communicate(timeout= ) below
            time.sleep(0.01)
            print("[Payload] Sending input")
            ### GENETIC ALGORITHM BEGINS HERE ###
            # 1. SELECT parents (best, worst)
            (best, worst) = fitness(population)
            # 2. CROSSOVER parents and generate new population of 10
            population = crossover(population[best], population[worst])

            # Get a payload from the population
            payload = population.pop()
            mutant = mutate(payload)
            population.append(mutant)

            # Output payload to terminal (pretty print)
            print("\x1b[1;35;m" + payload + "\x1b[0m")

            # Send input to program and check if any output received
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((TCP_IP, TCP_PORT))
            s.send(payload.encode())
            #print("Received: ", s.recv(1024).decode())
            # Check for timeout here (process is hanging)

            s.close()
        except Exception as e:
            print("Some error happened when sending input")
            print(e)
        # if subprocess object is not NULL
        if proc != 0:
            print(proc)
            try:
                proc.communicate(timeout=0.01)
                print("Return code =", proc.returncode)
                # Check for signal 11 (segfault so crash)
                if int(proc.returncode) == -11:
                    print("\x1b[0;37;41m" + "[EXIT] SEGFAULT" + "\x1b[0m")
                # If returncode is not None, process has crashed
                if proc.returncode != None:
                    print("Process has terminated so need to restart")
                    # Write payload and seed to file then restart process to continue fuzzing
                    tm = time.strftime('%a, %d %b %Y %H:%M:%S %Z(%z)')
                    crashFile = open("crashem/crash" + str(tm), "w")
                    crashFile.write(str(seed))
                    crashFile.write("\nPayload:\n")
                    crashFile.write(payload)
                    crashFile.close()
                    print("\tRestarting process...")
                    proc.terminate()
                    proc = subprocess.Popen(target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Process did not crash so continue
            except subprocess.TimeoutExpired:
                print("\x1b[6;30;42m" + "[STATUS] Process is still alive" + "\x1b[0m")
                continue

if __name__ == "__main__":
    main()
