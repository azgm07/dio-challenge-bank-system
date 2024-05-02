from abc import ABC, abstractmethod, abstractproperty


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self): ...
    @abstractmethod
    def registrar(self, conta) -> None: ...


class Deposito(Transacao):
    def __init__(self, valor) -> None:
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta) -> None:
        print(f"Registrar deposito de {conta} em Historico")
        if conta.depositar(self._valor):
            conta.registrar_transacao(self)
            print(f"Sucesso")
        else:
            print(f"Falha")

    def __str__(self) -> str:
        return f"Deposito de {self._valor}"


class Saque(Transacao):
    def __init__(self, valor) -> None:
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta) -> None:
        print(f"Registrar saque de {conta} em Historico")
        if conta.sacar(self._valor):
            conta.registrar_transacao(self)
            print(f"Sucesso")
        else:
            print(f"Falha")

    def __str__(self) -> str:
        return f"Saque de {self._valor}"


class Historico:
    def __init__(self) -> None:
        self._transacoes = []

    def adicionar_transacao(self, transacao) -> None:
        self._transacoes.append(transacao)

    def registro_transacoes(self):
        return self._transacoes


class Conta:
    def __init__(self, cliente, numero) -> None:
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    def __str__(self) -> str:
        return f"Conta: {self._agencia} - {self._numero} de {self._cliente}"

    @property
    def saldo(self):
        return self._saldo

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)

    def registrar_transacao(self, transacao):
        print(f"Registrou")
        self._historico.adicionar_transacao(transacao)

    def sacar(self, valor):
        if valor <= self._saldo:
            self._saldo -= valor
            return True
        else:
            return False

    def depositar(self, valor):
        self._saldo += valor
        return True

    def extrato(self):
        print("------- Extrato -------")
        for registro in self._historico.registro_transacoes():
            print(registro)
        print("-----------------------")


class ContaCorrente(Conta):
    def __init__(self, cliente, numero, limite=500.0, limite_saques=3) -> None:
        super().__init__(cliente, numero)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        if valor > self._limite:
            return False
        total_saques = sum(
            1
            for transacao in self._historico._transacoes
            if isinstance(transacao, Saque)
        )
        if total_saques > self._limite_saques:
            return False
        return super().sacar(valor)


class Cliente:
    def __init__(self, endereco) -> None:
        self._endereco = endereco
        self._contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, *, endereco, cpf, nome, data_nascimento) -> None:
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    def __str__(self) -> str:
        return f"{self._nome}"


# Test code
cliente = PessoaFisica(
    endereco="Rua Teste", cpf="123", nome="Ze", data_nascimento="1/1/1111"
)
conta = ContaCorrente.nova_conta(cliente, 1)
deposito = Deposito(1000)
cliente.realizar_transacao(conta, deposito)
saque = Saque(998)
cliente.realizar_transacao(conta, saque)
print(conta.saldo)
conta.extrato()
