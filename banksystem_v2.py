from http import HTTPStatus


class Bank:
    def __init__(self):
        self._users = []
        self._accounts = []
        self._users_num = 0
        self._accounts_num = 0
        self._users_active = set()
        self._accounts_active = set()

    def create_user(self, name, birthday, address):
        self._users_num =+ 1
        user_id = self._users_num
        self._users_active.add(user_id)
        new_user = BankUser(user_id, name, birthday, address)
        self._users.append(new_user)
        return user_id

    def create_account(self, user_id):
        if user_id not in self._users_active:
            return HTTPStatus.BAD_REQUEST
        self._accounts_num += 1
        account_num = self._accounts_num
        self._accounts_active.add(account_num)
        new_account = BankAccount("0001", account_num, user_id, 500)
        self._accounts.append(new_account)
        return account_num
    
    def list_accounts(self, user_id):
        if user_id not in self._users_active:
            return HTTPStatus.BAD_REQUEST
        return [str((acc.agency, acc.number)) for acc in self._accounts if acc.user == user_id]

    def deposit(self, /, user, account, amount) -> None:
        # Deposit new values to the account
        if (
            user not in self._users_active
            or account not in self._accounts_active
            or self._accounts[account-1].user != user
        ):
            return HTTPStatus.BAD_REQUEST

        if amount > 0:
            self._accounts[account-1].balance += amount
            self._accounts[account-1].statement.append(("d", amount))
            return HTTPStatus.OK
        else:
            return HTTPStatus.BAD_REQUEST

    def withdrawal(self, *, user, account, amount) -> None:
        # Withdrawal operation of the account limited for WITHDRAWAL_LIMIT per day
        if (
            user not in self._users_active
            or account not in self._accounts_active
            or self._accounts[account-1].user != user
        ):
            return HTTPStatus.BAD_REQUEST

        if amount > self._accounts[account-1].balance:
            return HTTPStatus.UNAUTHORIZED
        elif amount > self._accounts[account-1].limit:
            return HTTPStatus.FORBIDDEN
        elif self._accounts[account-1].withdrawal_num >= self._accounts[account-1].WITHDRAWAL_LIMIT:
            return HTTPStatus.NOT_ACCEPTABLE
        elif amount > 0:
            self._accounts[account-1].balance -= amount
            self._accounts[account-1].statement.append(("w", amount))
            self._accounts[account-1].withdrawal_num += 1
        else:
            return HTTPStatus.BAD_REQUEST

    def get_balance(self, user, account) -> float:
        # Return the current balance of the account
        if (
            user not in self._users_active
            or account not in self._accounts_active
            or self._accounts[account-1].user != user
        ):
            return HTTPStatus.BAD_REQUEST
        return self._accounts[account-1].balance

    def get_statement(self, user, account) -> str:
        # Create a statement output from the entries in cronological order
        if (
            user not in self._users_active
            or account not in self._accounts_active
            or self._accounts[account-1].user != user
        ):
            return HTTPStatus.BAD_REQUEST
        return self._accounts[account-1].statement


class BankUser:
    def __init__(self, id, name, birthday, address):
        self.id = id
        self.name = name
        self.birthday = birthday
        self.address = address


class BankAccount:
    def __init__(self, agency, number, user, limit) -> None:
        self.agency = agency
        self.number = number
        self.user = user
        self.balance = 0
        self.limit = limit
        self.statement = []
        self.withdrawal_num = 0
        self.WITHDRAWAL_LIMIT = 3


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

    def _console_menu(self, user, account) -> str:
        if not user:
            menu = """
            [nu] Novo Usuario
            [q] Sair
            => """
        elif not account:
            menu = """
            [lc] Listar Contas
            [nc] Nova Conta
            [nu] Novo Usuario
            [q] Sair
            => """
        else:
            menu = """
            [d] Depositar
            [s] Sacar
            [e] Extrato
            [lc] Listar Contas
            [nc] Nova Conta
            [nu] Novo Usuario
            [q] Sair
            => """
        return menu

    def _console_statement(self, statement, /, *, balance) -> None:
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

    def run(self) -> None:
        bank = Bank()
        current_user = None
        current_account = None
        while True:
            option = input(self._console_menu(current_user, current_account))
            if option.lower() == 'd' and current_account:
                amount = float(input(self.deposit_message))
                result = bank.deposit(current_user, current_account, amount)
                if result == HTTPStatus.BAD_REQUEST:
                    print(self.deposit_error)
            elif option.lower() == 's' and current_account:
                amount = float(input(self.withdrawal_message))
                result = bank.withdrawal(user=current_user, account=current_account, amount=amount)
                if result == HTTPStatus.BAD_REQUEST:
                    print(self.withdrawal_error)
                elif result == HTTPStatus.UNAUTHORIZED:
                    print(self.withdrawal_error_no_balance)
                elif result == HTTPStatus.FORBIDDEN:
                    print(self.withdrawal_error_no_limit)
                elif result == HTTPStatus.NOT_ACCEPTABLE:
                    print(self.withdrawal_error_max_exceeded)
            elif option.lower() == 'e' and current_account:
                self._console_statement(bank.get_statement(current_user, current_account), balance=bank.get_balance(current_user, current_account))
            elif option.lower() == 'lc' and current_user:
                print("\n".join(bank.list_accounts(current_user)))
            elif option.lower() == 'nc' and current_user:
                current_account = bank.create_account(current_user)
            elif option.lower() == 'nu':
                name = input("Nome: ")
                birthday = input("Aniversario: ")
                address = input("Endereco: ")
                current_user = bank.create_user(name, birthday, address)
            elif option.lower() == 'q':
                break
            else:
                print(self.invalid_operation)

console = Interface()
console.run()
