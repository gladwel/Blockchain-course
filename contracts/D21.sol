// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

import "../interfaces/IVoteD21.sol";

contract D21 is IVoteD21{
    mapping (address => Subject) internal subjects;
    mapping (address => uint) internal votes;
    mapping (address => address[]) internal subjectsVoters;
    address[] internal subjectAddresses;
    uint createdAt;
    uint finishAt;
    uint constant TIME_7_DAYS = 7 * 24 * 60 * 60;
    address private _owner;
    bool internal locked;

    constructor() {
        transferOwnership(msg.sender);
        createdAt = block.timestamp;
        finishAt = createdAt + TIME_7_DAYS;
    }
    
    modifier limitedTime() {
        require((finishAt - block.timestamp) > 0, "Time is over!");
        _;
    }
    
    // Re-Entrancy preventation modifier
    // https://solidity-by-example.org/hacks/re-entrancy/
    modifier noReentrant() {
        require(!locked, "No re-entrancy");
        locked = true;
        _;
        locked = false;
    }

    // Implementing onlyOwner functionality
    // OpenZeppelin Contracts (last updated v4.7.0) (access/Ownable.sol)
    modifier onlyOwner() {
        checkOwner();
        _;
    }

    function transferOwnership(address newOwner) internal virtual {
        _owner = newOwner;
    }

    function checkOwner() internal view virtual {
        require(owner() == msg.sender, "Ownable: caller is not the owner");
    }

    function owner() internal view virtual returns (address) {
        return _owner;
    }

    function isAddressEmpty(address addr) internal pure returns (bool) {
        return addr==address(0);
    }

    function isStringEmpty(string memory text) internal pure returns (bool) {
        return bytes(text).length == 0;    
    }

    function addSubject(string memory name) external noReentrant{
        require(!isAddressEmpty(msg.sender), "Address is empty");
        require(!isStringEmpty(name), "Enter valid name");
        require(isStringEmpty(subjects[msg.sender].name), "You already registered a subject");
        subjects[msg.sender] = Subject(name, 0);
        subjectAddresses.push(msg.sender);
    }

    function addVoter(address addr) external onlyOwner{
        votes[addr] = 1;
    }

    function getSubjects() external view returns(address[] memory){
        return subjectAddresses;
    }

    function getSubject(address addr) external view returns(Subject memory){
        require(!isAddressEmpty(addr), "Address is empty!");
        require(!isStringEmpty(subjects[addr].name), "Subject does not exists!");
        return subjects[addr];
    }
    
    function requireVoter (address addr) internal view{
        require(!isAddressEmpty(msg.sender), "Voter address is empty");
        require(!isAddressEmpty(addr), "Subject address is empty");
        require(votes[addr]!=0, "This voter was not registred!");
        bool voted = false;
        for(uint i = 0 ; i<subjectsVoters[addr].length; i++) {
            if (subjectsVoters[addr][i] == msg.sender){
                voted = true;
            }
        }
        require (!voted, "You already voted for this subject");
    }

    function votePositive(address addr) external noReentrant limitedTime{
        requireVoter(addr);
        require(votes[msg.sender] < 3, "You can't vote positive anymore!");
        votes[msg.sender]++;
        subjects[addr].votes ++;
        subjectsVoters[addr].push(msg.sender);
    }

    function voteNegative(address addr) external limitedTime{
        requireVoter(addr);
        require(votes[msg.sender] == 3, "You can't vote negative now");
        votes[msg.sender]++;
        subjects[addr].votes --;
        subjectsVoters[addr].push(msg.sender);
    }

    function getRemainingTime() external view returns(uint){
        int timeRemaining = int(finishAt) - int(block.timestamp);
        return timeRemaining > 0 ? uint(timeRemaining) : 0;
    }

    function sort() internal view returns(Subject [] memory) {
        Subject [] memory subjects_sort = new Subject[](subjectAddresses.length);
        for(uint i = 0 ; i<subjectAddresses.length; i++) {
            subjects_sort[i]=subjects[subjectAddresses[i]];
        }
        quickSort(subjects_sort, int(0), int(subjectAddresses.length - 1));
        return subjects_sort;
    }

    function quickSort(Subject[] memory arr, int left, int right) internal view{
        int i = left;
        int j = right;
        if (i == j) return;
        int pivot = arr[uint(left + (right - left) / 2)].votes;

        while (i <= j) {
            while (subjects[subjectAddresses[uint(i)]].votes > pivot) i++;
            while (pivot > subjects[subjectAddresses[uint(j)]].votes) j--;
            if (i <= j) {
                (arr[uint(i)], arr[uint(j)]) = (arr[uint(j)], arr[uint(i)]);
                i++;
                j--;
            }
        }
        if (left < j)
            quickSort(arr, left, j);
        if (i < right)
            quickSort(arr, i, right);
    }

    function getResults() external view returns(Subject[] memory){
        return sort();
    }
}