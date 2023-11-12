import datetime


class UserMessageConstructorComponent:
    """
    This component is responsible for constructing a message to be sent to the user.
    """

    def __init__(self, user_input: str = None):
        self.user_input = user_input
        self.curr_time = datetime.datetime.now()

    def __get_curr_time(self) -> datetime.datetime:
        return self.curr_time

    def message_constructor(self) -> str:
        user_message = f"Current Time: {self.curr_time}\n {self.user_input}"

        return user_message
