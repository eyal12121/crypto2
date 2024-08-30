from Client import Client
from MainServer import MainServer

NUM_CLIENTS = 3
NUM_CHECKS = 9


def main():
    main_server = MainServer()
    clients = []
    output_files = []
    for i in range(NUM_CLIENTS):
        clients.append(Client(main_server))
    file_path = "example.txt"
    file_path2 = "example2.txt"
    for i in range(NUM_CHECKS):
        out_name = "checkings" + str(i) + ".txt"
        output_files.append(out_name)

    clients[0].add_file(file_path)  # addition of file into system
    clients[1].add_file(file_path2)  # addition of file into system
    clients[0].request_file(file_path, output_files[0])  # client requests file it added to system
    clients[1].request_file(file_path, output_files[1])  # client requests file it added to system
    clients[0].request_file(file_path2, output_files[2])  # client request file it did not add to system
    clients[1].request_file(file_path2, output_files[3])  # client request file it did not add to system
    assert (clients[0].remove_file(file_path))  # client asks to remove file it added to system
    assert (not clients[0].remove_file(file_path2))  # client asks to remove file it did not add to system
    clients[2].add_file(file_path)  # addition of removed file into system by different client
    clients[0].request_file(file_path, output_files[4])  # client request file it did not add to system
    assert (not clients[0].remove_file(file_path))  # client asks to remove file that it did not add to system
    main_server.connection_loss(0)  # Simulate connection loss to a single server
    assert (clients[0].request_file(file_path, output_files[5])[0])  # client request file it did not add to system
    main_server.corrupt_data(file_path, 3)  # Simulate corrupted data (malicious server)
    assert (clients[0].request_file(file_path, output_files[6])[0])  # client request file it did not add to system
    main_server.connection_loss(1)  # Simulate connection loss to a single server
    assert (clients[0].request_file(file_path, output_files[7])[0])  # client request file it did not add to system
    assert (not clients[0].request_file(file_path2, output_files[8])[0])  # client request file it did not add to system

    # dynamic server amount (serverManager)?
    # add test funcs for different case scenarios


if __name__ == "__main__":
    main()
