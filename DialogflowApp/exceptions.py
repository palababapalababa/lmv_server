class NoTeamProvidedException(Exception):
    def __init__(self):
        self.message = "Ви не вибрали команду"

    def __str__(self):
        return self.message


class AllGamesPresentException(Exception):
    def __init__(self):
        self.message = "Всі матчі вже на екрані"

    def __str__(self):
        return self.message
