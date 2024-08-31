from Client import Client
from MainServer import MainServer

NUM_CLIENTS = 3
NUM_CHECKS = 5


def test_adding_file(file_path):
    main_server = MainServer()
    client = Client(main_server)
    assert (client.add_file(file_path))  # addition of file into system


def test_fetch_file(file_path, output_file):
    main_server = MainServer()
    client = Client(main_server)
    client.add_file(file_path)  # addition of file into system
    assert (client.request_file(file_path, output_file)[0])  # client requests file it added to system


def test_fetching_invalid_file(file_path, output_file):
    main_server = MainServer()
    client = Client(main_server)
    assert (not client.request_file(file_path, output_file)[0])  # client request file it did not add to system


def test_remove_file(file_path):
    main_server = MainServer()
    client = Client(main_server)
    client.add_file(file_path)  # addition of file into system
    assert (client.remove_file(file_path))  # client request file it added to system


def test_unauthorized_remove(file_path):
    main_server = MainServer()
    client1 = Client(main_server)
    client2 = Client(main_server)
    client1.add_file(file_path)  # addition of file into system
    assert (not client2.remove_file(file_path))  # client request file it did not add to system


def test_connection_loss(file_path1, file_path2, output_file):
    main_server = MainServer()
    client = Client(main_server)
    client.add_file(file_path1)  # addition of file into system
    client.add_file(file_path2)  # addition of file into system
    main_server.connection_loss(0)  # Simulate connection loss to a single server
    assert (client.request_file(file_path1, output_file)[0])  # client request file it did not add to system
    assert (main_server.servers[0].check_data(file_path2))


def test_malicious_server(file_path1, file_path2, output_file):
    main_server = MainServer()
    client = Client(main_server)
    client.add_file(file_path1)  # addition of file into system
    client.add_file(file_path2)  # addition of file into system
    main_server.corrupt_data(file_path1, 3)  # Simulate corrupted data (malicious server)
    assert (client.request_file(file_path1, output_file)[0])  # client request file it did not add to system
    assert (main_server.servers[3].check_data(file_path2))


def test_erasure_failing(file_path, output_file):
    main_server = MainServer()
    client = Client(main_server)
    client.add_file(file_path)  # addition of file into system

    main_server.connection_loss(0)  # Simulate connection loss to a single server
    main_server.connection_loss(1)  # Simulate connection loss to a single server
    main_server.connection_loss(2)  # Simulate connection loss to a single server
    main_server.connection_loss(3)  # Simulate connection loss to a single server
    assert (not client.request_file(file_path, output_file)[0])  # client request file it did not add to system


def main():
    main_server = MainServer()
    clients = []
    output_files = []
    for i in range(NUM_CLIENTS):
        clients.append(Client(main_server))
    file_path = "example.txt"
    file_path2 = "example2.txt"
    for i in range(NUM_CHECKS):
        out_name = "checking" + str(i) + ".txt"
        output_files.append(out_name)

    test_adding_file(file_path)
    test_fetch_file(file_path, output_files[0])
    test_fetching_invalid_file(file_path, output_files[1])
    test_remove_file(file_path)
    test_unauthorized_remove(file_path)
    test_connection_loss(file_path, file_path2, output_files[2])
    test_malicious_server(file_path, file_path2, output_files[3])
    test_erasure_failing(file_path, output_files[4])


if __name__ == "__main__":
    main()
