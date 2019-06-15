from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)

        print(f"Client connected: {self.ip}")

        self.transport.write("Welcome to the chat v0.1\n".encode())
        #How I can use map() there? 
        if len(self.factory.chat_history) > 0:
            for element in self.factory.chat_history:
                self.transport.write(f"{element}\n".encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')

        if self.login is not None:
            server_message = f"{self.login}: {message}"
            self.factory.notify_all_users(server_message)
            self.factory.chat_history.append(server_message)

            print(server_message)
        else:
            if message.startswith("login:") and message.replace("login:", "") not in self.factory.clients_logins:
                self.login = message.replace("login:", "")

                notification = f"New user connected: {self.login}"
                self.factory.chat_history.append(notification)
                self.factory.notify_all_users(notification)
                print(notification)
            else:
                print("Error: Invalid client login")
                self.transport.write("This login already in chat. Press ctrl + C and try whith anyother login\n".encode())
                self.connectionLost()

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        if self in self.factory.clients:
            self.factory.clients.remove(self)
            print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list
    clients_logins: list
    chat_history: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        self.clients_logins = []
        self.chat_history = []
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        for user in self.clients:
            if user.login not in self.clients_logins: self.clients_logins.append(user.login)
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()
