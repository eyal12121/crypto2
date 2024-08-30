from Client import Client
from MainServer import MainServer


def main():
    main_server = MainServer()

    client = Client(main_server)
    client2 = Client(main_server)
    file_path = "example.txt"
    file_path2 = "example2.txt"
    client.add_file(file_path)
    client2.add_file(file_path2)
    output_path = "checking.txt"
    output_path2 = "checking2.txt"
    output_path3 = "checking3.txt"
    output_path4 = "checking4.txt"
    client.request_file(file_path, output_path)
    client2.request_file(file_path, output_path2)
    client.request_file(file_path2, output_path3)
    client2.request_file(file_path2, output_path4)
    assert (client.remove_file(file_path))
    assert (not client.remove_file(file_path2))
    # server changed info
    # erasure encoding
    # dynamic server amount (serverManager)?

if __name__ == "__main__":
    main()
