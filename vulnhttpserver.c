#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <netinet/in.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

#define SERVER_IP "127.0.0.1"

#define SERVER_PORT 8080

#define DATA_SIZE 100

// compile on linux with gcc vulnhttpserver.c -pthread -o server

// error handling function
void errExit(const char szFmt[], ... ) {
    va_list args;
    va_start(args, szFmt);
    printf("ERROR: ");
    vprintf(szFmt, args);
    va_end(args);
    printf("\n");
    exit(99);
}

void *connection_handler(void * newSocketPtr) {
    int i;
    int option = 1;
    int socket = *(int *) newSocketPtr;
    // used to prevent (Socket Bind: Address already in use) because socket enters a TIME_WAIT state when program closes unexpectedly
    setsockopt(socket, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));

    // use send() and recv() to send and receive messages here
    char recvBuf[1024];
    int requestLen;

    // init request headers for parsing
    char * requestLine;
    char * parseReq; // ptr used for strcpy()
    char hostHeader[200];
    char userAgent[200];
    char acceptHeader[200];

    // response body template
    char response[] = "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n\r\n"
    "<!DOCTYPE html> <html> <head> <title>Hello, world!</title> "
    "<style> body { background-color: #111; color:white; } </style>"
    "</head> <meta charset=\"utf-8\"> <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">"
    "<body> <center> <h2 class=\"top\">$ Host = %s </h2><h3>Hello, World</h3> <br> <p class=\"about\"> This is a simple TCP server that may have some bugs <br> <br> Can you crash me? </div> </center> </body> </html>\r\n";
    char responseBody[strlen(response)]; // buffer to pass Host: header to web page
    
    // receive message from client    
    requestLen = recv(socket, recvBuf, 1024, 0);
    if (requestLen < 0) {
        errExit("Failed to receive: %s", strerror(errno));
    }

    printf(recvBuf); // print message received from client

    // parse HTTP headers from request
    for (i = 0; i < 4; i++) {
        if (i == 0) {
            // parse GET request line
            requestLine = strstr(recvBuf, "\r\n");
            //printf("requestLine = %s\n", requestLine);
        } else {
            requestLine = strstr(requestLine, "\r\n");
        }

        *(requestLine) = '\0';
        requestLine += 2;

        // parse request headers
        if (i == 1) { 
            // Host: localhost:8080
            strcpy(hostHeader, parseReq); // stack buffer overflow
            printf("host header = %s\n", hostHeader);

        } else if (i == 2) {
            // User-Agent: 
            strcpy(userAgent, parseReq);
            printf("user-agent = %s\n", userAgent);
        } else if (i == 3) {
            strcpy(acceptHeader, parseReq);
            printf("accept = %s\n", acceptHeader);
        }

        parseReq = requestLine;
        
    } // end for

    sprintf(responseBody, response, hostHeader); // format string bug 
    // send message to client
    write(socket, responseBody, strlen(responseBody) + 1);
    close(socket);

    return 0;
}

int main() {
    int welcomeSocket, newSocket;
    int returnCode;
    struct sockaddr_in serverAddr; // local host
    int option = 1;

    struct sockaddr_storage serverStorage; // remote client
    socklen_t addr_size; // client sockaddr length

    // init thread id and function
    pthread_t thread_id;

    // init welcome socket
    welcomeSocket = socket(AF_INET, SOCK_STREAM, 0);
    setsockopt(welcomeSocket, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
    if (welcomeSocket < 0) {
        errExit("Socket failed to create: %s", strerror(errno));
    }

    // init sockaddr struct with parameters
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &(serverAddr.sin_addr.s_addr));

    // bind socket with sockaddr struct
    returnCode = bind(welcomeSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));
    if (returnCode < 0) {
        errExit("Socket failed to bind: %s", strerror(errno));
    }

    // listen on welcome socket
    if (listen(welcomeSocket, 5) == 0) {
        printf("Listening... waiting for incoming TCP requests\n");
    } else {
        // errExit()
        printf("Listening error... exiting\n");
        exit(99);
    }

    addr_size = sizeof(struct sockaddr_in);

    while ((newSocket = accept(welcomeSocket, (struct sockaddr *) &serverStorage, &addr_size))) {
        printf("New connection accepted\n"); 
         
        // use pthread_create() to create new thread for new socket
        if (pthread_create(&thread_id, NULL, connection_handler, (void *) &newSocket) < 0) {
            printf("Could not create thread\n");
            exit(99);
        }
    }

    if (newSocket < 0) {
        printf("Connection accept failed\n");
        exit(99);
    }

    close(welcomeSocket);

    return 0;
}
