from Client import Client
from MainServer import MainServer


def main():
    main_server = MainServer()

    client = Client(main_server)

    file_path = "example.txt"
    client.add_file(file_path)
    output_path = "checking.txt"
    client.request_file(file_path, output_path)


if __name__ == "__main__":
    main()
