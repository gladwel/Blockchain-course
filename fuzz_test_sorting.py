import brownie
import random
from woke.fuzzer.campaign import Campaign
from woke.fuzzer.decorators import flow, invariant, weight
from woke.fuzzer.random import random_account
from brownie import accounts


class Subject:
    def __init__(self, address, votes, name):
        self.address = address
        self.votes = votes
        self.name = name
        self.voters = []
        
class Test:
    def __init__(self, contract_type) -> None:
        self.owner = accounts[0]
        self.contract = contract_type.deploy({"from": self.owner})
        self.subjects = []
        self.counter = 0
        self.counter_subject = 0
        self.positiveVotes = {}
        self.negativeVotes = {}
        for i in range(0, 40):
            accounts.add()
        for i in range(0, 40):
            self.contract.addVoter(accounts[i], {'from': self.owner})
            self.positiveVotes[accounts[i]] = 0
            self.negativeVotes[accounts[i]] = 0

    @flow
    def vote_positive(self):
        if len(self.subjects) > 0:
            subject = self.subjects[random.randint(0, len(self.subjects) - 1)]
            account = 0
            for acc in self.positiveVotes.keys():
                if acc not in subject.voters and self.positiveVotes[acc] < 2:
                    account = acc
                    break
            tx = self.contract.votePositive(subject.address, {'from': account})
            for e in tx.events:
                print(e)
            subject.votes += 1
            self.positiveVotes[account] += 1
            subject.voters.append(account)
        
    @flow
    def vote_negative(self):
        if len(self.subjects) > 0:
            # More than 2 positive votes check
            potential_accounts_2 = []
            for account in self.positiveVotes.keys():
                if self.positiveVotes[account] >= 2:
                    potential_accounts_2.append(account)
            potential_accounts = []
            # More than 1 negative vote check
            for account in potential_accounts_2:
                if self.negativeVotes[account] == 0:
                    potential_accounts.append(account)
            # No potential accounts - return
            if len(potential_accounts) == 0:
                return
            # Get random subject
            subject = self.subjects[random.randint(0, len(self.subjects) - 1)]
            # Find account that can be used, else return
            account = 0
            for acc in potential_accounts:
                if acc not in subject.voters:
                    account = acc
            if account == 0:
                return
            # Make a negative vote
            tx = self.contract.voteNegative(subject.address, {'from': account})
            for e in tx.events:
                print(e)
            # Update state variables
            subject.votes -= 1
            subject.voters.append(account)
            self.negativeVotes[account] = 1

    @flow
    def add_subject(self):
        self.contract.addSubject(f"Subject no. {self.counter_subject}", {'from': accounts[self.counter_subject]})
        self.subjects.append(Subject(name=f"Subject no. {self.counter_subject}", votes=0, address=accounts[self.counter_subject]))
        self.counter_subject += 1

    @invariant
    def check_if_sorted(self):
        self.subjects = sorted(self.subjects, key=lambda s: s.votes, reverse=True)
        contract_subjects = self.contract.getResults()
        for s1, s2 in zip(self.subjects, contract_subjects):
            assert s1.votes == s2[1]
            print(f"{s1.name}     {s2[0]}")
            print(f"{s1.votes}     {s2[1]}")



def test_sort(D21):
    print(len(accounts))
    campaign = Campaign(lambda: Test(D21))
    campaign.run(100, 40)