import brownie
import pytest
from brownie import chain, D21, accounts, exceptions
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

TIME_7_DAYS = 7 * 24 * 60 * 60

def test_addSubject():
    contract = D21.deploy({'from': accounts[0]})
    contract.addVoter(accounts[0], {'from': accounts[0]})
    contract.addSubject("Test1", {'from': accounts[0]})
    with brownie.reverts():
        contract.addSubject("Test2", {'from': accounts[0]})


def test_addVoter():
    contract = D21.deploy({'from': accounts[0]})
    with brownie.reverts():
        contract.addVoter(accounts[1], {'from': accounts[1]})

def test_getSubjects():
    contract = D21.deploy({'from': accounts[0]})
    contract.getSubjects({'from': accounts[1]})

def test_getSubject():
    contract = D21.deploy({'from': accounts[0]})
    contract.addVoter(accounts[0], {'from': accounts[0]})
    contract.addSubject("Test1", {'from': accounts[0]})
    with brownie.reverts():
        contract.getSubject(accounts[1], {'from': accounts[1]})
    contract.getSubject(accounts[0], {'from': accounts[0]})


def test_time_limit():
    contract = D21.deploy({'from': accounts[0]})
    contract.addVoter(accounts[0], {'from': accounts[0]})
    chain.sleep((TIME_7_DAYS + 1 ) * 1000)
    with brownie.reverts():
        contract.votePositive(accounts[0], {'from': accounts[0]})

def test_getRemainingTime():
    contract = D21.deploy({'from': accounts[0]})
    time_to_wait = 1000
    chain.sleep(time_to_wait)
    chain.mine()
    assert contract.getRemainingTime({'from': accounts[0]}) == int(TIME_7_DAYS - time_to_wait)
    time_to_wait = 10000000000
    chain.sleep(time_to_wait)
    chain.mine()
    assert contract.getRemainingTime({'from': accounts[0]}) == int(0)


def test_getResults():
    contract = D21.deploy({'from': accounts[0]})

    contract.addVoter(accounts[0], {'from': accounts[0]})
    contract.addVoter(accounts[1], {'from': accounts[0]})
    contract.addVoter(accounts[2], {'from': accounts[0]})
    contract.addVoter(accounts[3], {'from': accounts[0]})
    contract.addVoter(accounts[4], {'from': accounts[0]})
    contract.addVoter(accounts[5], {'from': accounts[0]})
    contract.addVoter(accounts[6], {'from': accounts[0]})

    contract.addSubject("Test0", {'from': accounts[0]})
    contract.getResults({'from': accounts[0]})
    contract.addSubject("Test1", {'from': accounts[1]})
    contract.addSubject("Test2", {'from': accounts[2]})
    contract.addSubject("Test3", {'from': accounts[3]})
    contract.addSubject("Test4", {'from': accounts[4]})
    contract.addSubject("Test5", {'from': accounts[5]})
    contract.addSubject("Test6", {'from': accounts[6]})

    contract.votePositive(accounts[0], {'from': accounts[0]})
    contract.votePositive(accounts[1], {'from': accounts[0]})
    contract.voteNegative(accounts[5], {'from': accounts[0]})

    contract.votePositive(accounts[0], {'from': accounts[1]})
    with brownie.reverts():
        contract.voteNegative(accounts[5], {'from': accounts[1]})
    contract.votePositive(accounts[1], {'from': accounts[1]})
    contract.voteNegative(accounts[5], {'from': accounts[1]})
    
    contract.votePositive(accounts[0], {'from': accounts[2]})
    contract.votePositive(accounts[2], {'from': accounts[2]})
    contract.voteNegative(accounts[5], {'from': accounts[2]})
    
    contract.votePositive(accounts[1], {'from': accounts[3]})
    contract.votePositive(accounts[3], {'from': accounts[3]})
    contract.voteNegative(accounts[5], {'from': accounts[3]})

    contract.votePositive(accounts[3], {'from': accounts[4]})
    contract.votePositive(accounts[4], {'from': accounts[4]})
    contract.voteNegative(accounts[5], {'from': accounts[4]})

    contract.votePositive(accounts[0], {'from': accounts[5]})
    contract.votePositive(accounts[4], {'from': accounts[5]})
    contract.voteNegative(accounts[5], {'from': accounts[5]})

    contract.votePositive(accounts[0], {'from': accounts[6]})
    contract.votePositive(accounts[6], {'from': accounts[6]})
    contract.voteNegative(accounts[5], {'from': accounts[6]})

    contract.getResults({'from': accounts[0]})

def test_only_owner():
    contract = D21.deploy({'from': accounts[0]})
    with brownie.reverts():
        contract.addVoter(accounts[0], {'from': accounts[1]})

def test_vote_same_subject():
    contract = D21.deploy({'from': accounts[0]})
    contract.addVoter(accounts[1], {'from': accounts[0]})
    contract.addSubject("Test1", {'from': accounts[1]})
    contract.votePositive(accounts[1], {'from': accounts[1]})
    with brownie.reverts():
        contract.voteNegative(accounts[1], {'from': accounts[1]})




