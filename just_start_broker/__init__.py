class JustStartBrokerException(Exception):
    pass


class EntityNotFoundError(JustStartBrokerException):
    pass


class ClientError(JustStartBrokerException):
    pass
