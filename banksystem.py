from http import HTTPStatus


class BankAccount:
    def __init__(self, balance, limit) -> None:
        self.balance = balance
        self.limit = limit
        self.statement = []
        self.withdrawal_num = 0
        self.WITHDRAWAL_LIMIT = 3

    def deposit(self, amount) -> None:
        # Deposit new values to the account
        if amount > 0:
            self.balance += amount
            self.statement.append(("d", amount))
            return HTTPStatus.OK
        else:
            return HTTPStatus.BAD_REQUEST

    def withdrawal(self, amount) -> None:
        # Withdrawal operation of the account limited for WITHDRAWAL_LIMIT per day
        if amount > self.balance:
            return HTTPStatus.UNAUTHORIZED
        elif amount > self.limit:
            return HTTPStatus.FORBIDDEN
        elif self.withdrawal_num >= self.WITHDRAWAL_LIMIT:
            return HTTPStatus.NOT_ACCEPTABLE
        elif amount > 0:
            self.balance -= amount
            self.statement.append(("w", amount))
            self.withdrawal_num += 1
        else:
            return HTTPStatus.BAD_REQUEST

    def get_balance(self) -> float:
        # Return the current balance of the account
        return self.balance

    def get_statement(self) -> str:
        # Create a statement output from the entries in cronological order
        return self.statement


class Interface:
    def __init__(self) -> None:
        self.deposit_message = "Informe o valor do depósito: "
        self.deposit_error = "Operação falhou! O valor informado é inválido."
        self.withdrawal_message = "Informe o valor do saque: "
        self.withdrawal_error = "Operação falhou! O valor informado é inválido."
        self.withdrawal_error_no_balance = (
            "Operação falhou! Você não tem saldo suficiente."
        )
        self.withdrawal_error_no_limit = (
            "Operação falhou! O valor do saque excede o limite."
        )
        self.withdrawal_error_max_exceeded = (
            "Operação falhou! Número máximo de saques excedido."
        )
        self.invalid_operation = (
            "Operação inválida, por favor selecione novamente a operação desejada."
        )

    def _console_menu(self) -> str:
        menu = """
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [q] Sair
        => """
        return menu

    def _console_statement(self, statement, balance) -> None:
        print("================ EXTRATO ================")
        if not statement:
            print("Não foram realizadas movimentações.")
        else:
            for s in statement:
                if s[0] == "d":
                    print(f"Depósito: R$ {s[1]:.2f}")
                elif s[0] == "w":
                    print(f"Saque: R$ {s[1]:.2f}")
            print(f"\nSaldo: R$ {balance:.2f}")

    def run(self, account: BankAccount) -> None:
        while True:
            option = input(self._console_menu())
            match option.lower():
                case "d":
                    amount = float(input(self.deposit_message))
                    result = account.deposit(amount)
                    if result == HTTPStatus.BAD_REQUEST:
                        print(self.deposit_error)
                case "s":
                    amount = float(input(self.withdrawal_message))
                    result = account.withdrawal(amount)
                    if result == HTTPStatus.BAD_REQUEST:
                        print(self.withdrawal_error)
                    elif result == HTTPStatus.UNAUTHORIZED:
                        print(self.withdrawal_error_no_balance)
                    elif result == HTTPStatus.FORBIDDEN:
                        print(self.withdrawal_error_no_limit)
                    elif result == HTTPStatus.NOT_ACCEPTABLE:
                        print(self.withdrawal_error_max_exceeded)
                case "e":
                    self._console_statement(account.statement, account.balance)
                case "q":
                    break
                case _:
                    print(self.invalid_operation)


account = BankAccount(0, 500)
console = Interface()
console.run(account)
