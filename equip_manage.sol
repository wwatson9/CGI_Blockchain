// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EquipmentManagementSystem {
    // Enum for equipment status using string-like representation
    enum EquipmentStatus {
        Available,
        CheckedOut,
        Maintenance,
        Lost,
        Removed
    }

    // Struct to store equipment details with user name
    struct Equipment {
        uint256 id;
        string equipment_name;
        string description;
        string equipmentType;
        EquipmentStatus status;
        address currentBorrower;
        string currentBorrowerName;
        uint256 addedTimestamp;
        uint256 lastCheckedOutTimestamp;
        uint256 lastReturnedTimestamp;
        bool isRemoved;
    }

    // Events for enhanced tracking
    event EquipmentAdded(
        uint256 indexed id, 
        string equipment_name, 
        string description, 
        string equipmentType
    );

    event EquipmentRemoved(
        uint256 indexed id,
        string equipment_name,
        string removalReason
    );
    
    event EquipmentRetrieved(
        uint256[] ids, 
        string[] equipment_names, 
        string[] borrowerNames
    );
    
    event UserCheckoutsRetrieved(
        address user, 
        uint256[] ids, 
        string[] equipment_names, 
        string[] borrowerNames
    );
    
    event EquipmentStatusChanged(
        uint256 indexed id, 
        string newStatus,
        string statusChangeReason
    );

    event EquipmentCheckedOut(
        uint256 indexed id, 
        address indexed borrower, 
        string borrowerName,
        uint256 checkoutTimestamp
    );
    
    event EquipmentReturned(
        uint256 indexed id, 
        address indexed borrower, 
        string borrowerName,
        uint256 returnTimestamp
    );

    // Mapping to store equipment
    mapping(uint256 => Equipment) public equipmentRegistry;
    
    // Tracking equipment IDs
    uint256[] public equipmentList;

    // Mapping to track user's checked out equipment
    mapping(address => uint256[]) public userCheckouts;

    // Add new equipment with name
    function addEquipment(
        uint256 _id, 
        string memory _equipment_name,
        string memory _description, 
        string memory _equipmentType
    ) public {
        // Check if equipment with this ID already exists
        require(
            equipmentRegistry[_id].id == 0, 
            "Equipment with this ID already exists"
        );

        // Create new equipment
        equipmentRegistry[_id] = Equipment({
            id: _id,
            equipment_name: _equipment_name,
            description: _description,
            equipmentType: _equipmentType,
            status: EquipmentStatus.Available,
            currentBorrower: address(0),
            currentBorrowerName: "",
            addedTimestamp: block.timestamp,
            lastCheckedOutTimestamp: 0,
            lastReturnedTimestamp: 0,
            isRemoved: false
        });

        // Add to equipment list
        equipmentList.push(_id);

        // Emit event
        emit EquipmentAdded(_id, _equipment_name, _description, _equipmentType);
    }

    // Remove equipment function
    function removeEquipment(
        uint256 _id,
        string memory _removalReason
    ) public {
        Equipment storage equipment = equipmentRegistry[_id];
        
        require(equipment.id != 0, "Equipment does not exist");
        require(!equipment.isRemoved, "Equipment is already removed");
        require(
            equipment.status == EquipmentStatus.Available, 
            "Cannot remove checked out equipment"
        );

        equipment.isRemoved = true;
        equipment.status = EquipmentStatus.Removed;

        emit EquipmentRemoved(
            _id, 
            equipment.equipment_name, 
            _removalReason
        );
    }

    // Checkout equipment with borrower name
    function checkoutEquipment(
        uint256 _id, 
        string memory _borrowerName
    ) public {
        Equipment storage equipment = equipmentRegistry[_id];
        
        require(equipment.id != 0, "Equipment does not exist");
        require(!equipment.isRemoved, "Equipment has been removed from system");
        require(
            equipment.status == EquipmentStatus.Available, 
            "Equipment is not available"
        );

        equipment.status = EquipmentStatus.CheckedOut;
        equipment.currentBorrower = msg.sender;
        equipment.currentBorrowerName = _borrowerName;
        equipment.lastCheckedOutTimestamp = block.timestamp;

        // Track user's checkouts
        userCheckouts[msg.sender].push(_id);

        // Emit events
        emit EquipmentStatusChanged(
            _id, 
            "CheckedOut",
            "Equipment checked out by user"
        );
        emit EquipmentCheckedOut(
            _id, 
            msg.sender, 
            _borrowerName, 
            block.timestamp
        );
    }

    // Return equipment
    function returnEquipment(uint256 _id) public {
        Equipment storage equipment = equipmentRegistry[_id];
        
        require(equipment.id != 0, "Equipment does not exist");
        require(!equipment.isRemoved, "Equipment has been removed from system");
        require(
            equipment.status == EquipmentStatus.CheckedOut, 
            "Equipment is not checked out"
        );
        require(
            equipment.currentBorrower == msg.sender, 
            "Only the borrower can return this equipment"
        );

        string memory borrowerName = equipment.currentBorrowerName;

        equipment.status = EquipmentStatus.Available;
        equipment.lastReturnedTimestamp = block.timestamp;

        // Remove from user's checkouts
        _removeUserCheckout(msg.sender, _id);

        // Reset borrower
        equipment.currentBorrower = address(0);
        equipment.currentBorrowerName = "";

        // Emit events
        emit EquipmentStatusChanged(
            _id, 
            "Available",
            "Equipment returned by user"
        );
        emit EquipmentReturned(
            _id, 
            msg.sender, 
            borrowerName, 
            block.timestamp
        );
    }

    // Internal function to remove equipment from user's checkouts
    function _removeUserCheckout(address _user, uint256 _id) internal {
        uint256[] storage userEquipment = userCheckouts[_user];
        for (uint256 i = 0; i < userEquipment.length; i++) {
            if (userEquipment[i] == _id) {
                userEquipment[i] = userEquipment[userEquipment.length - 1];
                userEquipment.pop();
                break;
            }
        }
    }

    // Modified getAllEquipment to include names and borrower info
    function getAllEquipment() public {
        uint256[] memory ids = new uint256[](equipmentList.length);
        string[] memory equipment_names = new string[](equipmentList.length);
        string[] memory borrowerNames = new string[](equipmentList.length);
        uint256 activeCount = 0;

        for (uint256 i = 0; i < equipmentList.length; i++) {
            Equipment memory equipment = equipmentRegistry[equipmentList[i]];
            if (!equipment.isRemoved) {
                ids[activeCount] = equipment.id;
                equipment_names[activeCount] = equipment.equipment_name;
                borrowerNames[activeCount] = equipment.currentBorrowerName;
                activeCount++;
            }
        }

        // Create new arrays with only active equipment
        uint256[] memory activeIds = new uint256[](activeCount);
        string[] memory activeNames = new string[](activeCount);
        string[] memory activeBorrowers = new string[](activeCount);
        
        for (uint256 i = 0; i < activeCount; i++) {
            activeIds[i] = ids[i];
            activeNames[i] = equipment_names[i];
            activeBorrowers[i] = borrowerNames[i];
        }

        emit EquipmentRetrieved(activeIds, activeNames, activeBorrowers);
    }

    // Modified getUserCheckouts to include equipment names
    function getUserCheckouts(address _user) public {
        uint256[] memory ids = userCheckouts[_user];
        string[] memory equipment_names = new string[](ids.length);
        string[] memory borrowerNames = new string[](ids.length);

        for (uint256 i = 0; i < ids.length; i++) {
            Equipment memory equipment = equipmentRegistry[ids[i]];
            equipment_names[i] = equipment.equipment_name;
            borrowerNames[i] = equipment.currentBorrowerName;
        }

        emit UserCheckoutsRetrieved(_user, ids, equipment_names, borrowerNames);
    }

    // Modified updateEquipmentStatus to accept string status
    function updateEquipmentStatus(
        uint256 _id, 
        string memory _newStatus,
        string memory _statusReason
    ) public {
        Equipment storage equipment = equipmentRegistry[_id];
        
        require(equipment.id != 0, "Equipment does not exist");
        require(!equipment.isRemoved, "Equipment has been removed from system");
        
        // Only borrower can update status if equipment is checked out
        if (equipment.status == EquipmentStatus.CheckedOut) {
            require(
                equipment.currentBorrower == msg.sender,
                "Only borrower can update status of checked out equipment"
            );
        }

        emit EquipmentStatusChanged(
            _id, 
            _newStatus,
            _statusReason
        );
    }

    // Get equipment details
    function getEquipmentDetails(uint256 _id) public view returns (
        uint256 id,
        string memory equipment_name,
        string memory description,
        string memory equipmentType,
        EquipmentStatus status,
        address currentBorrower,
        string memory currentBorrowerName,
        bool isRemoved
    ) {
        require(equipmentRegistry[_id].id != 0, "Equipment does not exist");
        Equipment memory equipment = equipmentRegistry[_id];
        return (
            equipment.id,
            equipment.equipment_name,
            equipment.description,
            equipment.equipmentType,
            equipment.status,
            equipment.currentBorrower,
            equipment.currentBorrowerName,
            equipment.isRemoved
        );
    }
}