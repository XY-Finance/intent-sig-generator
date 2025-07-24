import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Button, Card, Alert } from 'react-bootstrap';
import { ethers } from 'ethers';

function App() {
  // Connection status
  const [isConnected, setIsConnected] = useState(false);
  const [signer, setSigner] = useState(null);
  const [account, setAccount] = useState('');

  // Intent related fields
  const [owner, setOwner] = useState('');
  const [nonce, setNonce] = useState('0');
  const [deadline, setDeadline] = useState('0');
  const [actionsList, setActionsList] = useState([
    {
      action: 'Deposit',
      protocol: '',
      protocolAddress: '',
      chainId: '1', // Default to Ethereum mainnet
      tokenIn: '',
      amountIn: '0',
      tokenOut: ethers.constants.AddressZero,
      amountOut: '0',
      receiver: ethers.constants.AddressZero,
      slippage: '0'
    }
  ]);
  const [relayFee, setRelayFee] = useState({
    token: '',
    amount: '0'
  });
  const [inputs, setInputs] = useState(['0x']);

  // Signature results
  const [signature, setSignature] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [digest, setDigest] = useState('');
  
  // Verification related fields
  const [verifyDigest, setVerifyDigest] = useState('');
  const [verifySignature, setVerifySignature] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [verifiedAddress, setVerifiedAddress] = useState('');
  const [normalizedRecoveredAddress, setNormalizedRecoveredAddress] = useState('');
  const [normalizedAccount, setNormalizedAccount] = useState('');
  const [verifyError, setVerifyError] = useState('');
  
  // DomainData
  const [chainId, setChainId] = useState('');
  const [verifyingContract, setVerifyingContract] = useState('');
  // Example contract addresses - These are some well-known contracts for testing
  const exampleContracts = {
    '1': '0xbF955e4370210697E768dCCeD7866c4456C26849', // Custom Mainnet Example
    '137': '0xd9145CCE52D386f254917e481eB44e9943F39138', // Uniswap v3 on Polygon
    '56': '0x10ED43C718714eb63d5aA57B78B54704E256024E', // PancakeSwap on BSC
    '42161': '0x000000000000ad05ccc4f10045630fb830b95127', // Camelot on Arbitrum
  };

  // Calldata encoding related fields
  const [functionSelector, setFunctionSelector] = useState('');
  const [isFunctionSignature, setIsFunctionSignature] = useState(true);
  const [calldataParams, setCalldataParams] = useState([{ type: 'address', value: '' }]);
  const [encodedCalldata, setEncodedCalldata] = useState('');
  const [calldataError, setCalldataError] = useState('');
  
  // Data types for calldata parameters
  const dataTypes = [
    'address',
    'uint256',
    'uint128',
    'uint64',
    'uint32',
    'uint16',
    'uint8',
    'int256',
    'int128',
    'int64',
    'int32',
    'bytes32',
    'bytes',
    'string',
    'bool',
    'MarketParams'
  ];

  // INTENT_TYPEHASH customization
  const [useCustomTypehash, setUseCustomTypehash] = useState(false);
  const [intentTypehash, setIntentTypehash] = useState(
    "Intent(address owner,uint256 nonce,uint256 deadline,Actions[] actions,RelayFee relayFee,bytes[] inputs)" +
    "Actions(string action,string protocol,address protocolAddress,uint256 chainId,address tokenIn,uint256 amountIn,address tokenOut,uint256 amountOut,address receiver,uint256 slippage)" +
    "RelayFee(address token,uint256 amount)"
  );
  const [actionsTypehash, setActionsTypehash] = useState(
    "Actions(string action,string protocol,address protocolAddress,uint256 chainId,address tokenIn,uint256 amountIn,address tokenOut,uint256 amountOut,address receiver,uint256 slippage)"
  );
  const [relayFeeTypehash, setRelayFeeTypehash] = useState(
    "RelayFee(address token,uint256 amount)"
  );

  // Add MarketParams state
  const [marketParamsList, setMarketParamsList] = useState([
    {
      loanToken: '',
      collateralToken: '',
      oracle: '',
      irm: '',
      lltv: ''
    }
  ]);

  // Permit1 signature related fields
  const [permitOwner, setPermitOwner] = useState('');
  const [permitSpender, setPermitSpender] = useState('');
  const [permitValue, setPermitValue] = useState('');
  const [permitNonce, setPermitNonce] = useState('');
  const [permitDeadline, setPermitDeadline] = useState('');
  const [permitChainId, setPermitChainId] = useState('');
  const [permitVerifyingContract, setPermitVerifyingContract] = useState('');
  const [permitName, setPermitName] = useState('');
  const [permitVersion, setPermitVersion] = useState('1');
  const [permitResult, setPermitResult] = useState({ v: '', r: '', s: '' });
  const [permitError, setPermitError] = useState('');

  // Permit Struct Calldata Encoder
  const [permitStruct, setPermitStruct] = useState({
    token: '',
    owner: '',
    value: '',
    deadline: '',
    v: '',
    r: '',
    s: '',
    relayFee: ''
  });
  const [permitStructCalldata, setPermitStructCalldata] = useState('');
  const [permitStructError, setPermitStructError] = useState('');

  // BuildAndExecuteCallValue struct related fields
  const [buildAndExecuteCallValue, setBuildAndExecuteCallValue] = useState({
    tokenOutPercent: '',
    tokenOut: '',
    target: '',
    value: '',
    protocol: '',
    action: '',
    receiver: '',
    adaptorData: ''
  });
  const [buildAndExecuteCallCalldata, setBuildAndExecuteCallCalldata] = useState('');
  const [buildAndExecuteCallError, setBuildAndExecuteCallError] = useState('');

  // DCA Intent State
  const [dcaIntent, setDcaIntent] = useState({
    chainId: '',
    srcToken: '',
    dstToken: '',
    amount: '',
    interval: '',
    priceImpact: '',
    epoch: ''
  });
  const [dcaSignature, setDcaSignature] = useState('');
  const [dcaSignError, setDcaSignError] = useState('');

  // User Tag
  const [userTagAddress, setUserTagAddress] = useState('');
  const [userTagResult, setUserTagResult] = useState(null);
  const [userTagError, setUserTagError] = useState('');

  // Connect MetaMask
  const connectWallet = async () => {
    try {
      if (window.ethereum) {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        await provider.send("eth_requestAccounts", []);
        const signer = provider.getSigner();
        const address = await signer.getAddress();
        
        // Get current network chainId (directly in number format)
        const chainIdHex = await provider.send("eth_chainId", []);
        const networkChainId = parseInt(chainIdHex, 16).toString();
        
        console.log("Connected to network with chainId:", networkChainId);
        
        setSigner(signer);
        setAccount(address);
        setOwner(address);
        setChainId(networkChainId);
        setIsConnected(true);
        
        // Update chainId in all actions
        setActionsList(prev => prev.map(action => ({
          ...action,
          chainId: networkChainId
        })));
        
        // Automatically set the example contract address for the current network
        if (exampleContracts[networkChainId]) {
          setVerifyingContract(exampleContracts[networkChainId]);
        }
      } else {
        setError('Please install MetaMask');
      }
    } catch (error) {
      console.error(error);
      setError('Failed to connect wallet: ' + error.message);
    }
  };

  // Check if address is a contract address
  const isContractAddress = async (address) => {
    try {
      if (!ethers.utils.isAddress(address)) return false;
      
      // If it's one of the example contract addresses, consider it a contract
      for (const chainId in exampleContracts) {
        if (exampleContracts[chainId].toLowerCase() === address.toLowerCase()) {
          return true;
        }
      }
      
      if (window.ethereum) {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const code = await provider.getCode(address);
        // If there's code at the address, it's a contract
        return code !== '0x';
      }
      return true; // If unable to check, assume it's a contract
    } catch (error) {
      console.error("Failed to check contract address:", error);
      return false;
    }
  };

  // Add new Action
  const addAction = () => {
    setActionsList([
      ...actionsList,
      {
        action: 'Deposit',
        protocol: '',
        protocolAddress: '',
        chainId: chainId || '1',
        tokenIn: '',
        amountIn: '0',
        tokenOut: ethers.constants.AddressZero,
        amountOut: '0',
        receiver: ethers.constants.AddressZero,
        slippage: '0'
      }
    ]);
  };

  // Update specific Action
  const updateAction = (index, field, value) => {
    const updatedActions = [...actionsList];
    
    // Update the field
    updatedActions[index][field] = value;
    
    setActionsList(updatedActions);
  };

  // Remove Action
  const removeAction = (index) => {
    setActionsList(actionsList.filter((_, i) => i !== index));
  };

  // Update RelayFee
  const updateRelayFee = (field, value) => {
    setRelayFee({
      ...relayFee,
      [field]: value
    });
  };

  // Update Input
  const updateInput = (index, value) => {
    const updatedInputs = [...inputs];
    updatedInputs[index] = value;
    setInputs(updatedInputs);
  };

  // Add Input
  const addInput = () => {
    setInputs([...inputs, '0x']);
  };

  // Remove Input
  const removeInput = (index) => {
    setInputs(inputs.filter((_, i) => i !== index));
  };

  // Get domain data for EIP-712 signature
  const getDomainData = () => {
    return {
      name: 'SuperIntentRouter',
      version: 'v1',
      chainId: parseInt(chainId),
      verifyingContract: verifyingContract
    };
  };

  // Get types for EIP-712 signature
  const getTypes = () => {
    // Parse Actions from custom field
    const parseActions = () => {
      try {
        return [
          { name: 'action', type: 'string' },
          { name: 'protocol', type: 'string' },
          { name: 'protocolAddress', type: 'address' },
          { name: 'chainId', type: 'uint256' },
          { name: 'tokenIn', type: 'address' },
          { name: 'amountIn', type: 'uint256' },
          { name: 'tokenOut', type: 'address' },
          { name: 'amountOut', type: 'uint256' },
          { name: 'receiver', type: 'address' },
          { name: 'slippage', type: 'uint256' }
        ];
      } catch (error) {
        console.error('Error parsing actions:', error);
        return [];
      }
    };

    // Parse RelayFee type
    const parseRelayFeeType = () => {
      try {
        const relayFeeRegex = /RelayFee\((.*?)\)/;
        const match = relayFeeTypehash.match(relayFeeRegex);
        if (match && match[1]) {
          const fields = match[1].split(',');
          return fields.map(field => {
            const [type, name] = field.trim().split(' ');
            return { name, type };
          });
        }
      } catch (error) {
        console.error('Error parsing relay fee type:', error);
      }
      
      // Default fields
      return [
        { name: 'token', type: 'address' },
        { name: 'amount', type: 'uint256' }
      ];
    };
    
    return {
      Intent: [
        { name: 'owner', type: 'address' },
        { name: 'nonce', type: 'uint256' },
        { name: 'deadline', type: 'uint256' },
        { name: 'actions', type: 'Actions[]' },
        { name: 'relayFee', type: 'RelayFee' },
        { name: 'inputs', type: 'bytes[]' }
      ],
      Actions: parseActions(),
      RelayFee: parseRelayFeeType()
    };
  };

  // Create signature data
  const getSignatureData = () => {
    // Ensure all addresses are in the correct format
    const formattedActions = actionsList.map(action => ({
      ...action,
      protocolAddress: ethers.utils.getAddress(action.protocolAddress || ethers.constants.AddressZero),
      tokenIn: ethers.utils.getAddress(action.tokenIn || ethers.constants.AddressZero),
      tokenOut: ethers.utils.getAddress(action.tokenOut || ethers.constants.AddressZero),
      receiver: ethers.utils.getAddress(action.receiver || ethers.constants.AddressZero)
    }));
    
    return {
      owner: ethers.utils.getAddress(owner || ethers.constants.AddressZero),
      nonce,
      deadline,
      actions: formattedActions,
      relayFee: {
        token: ethers.utils.getAddress(relayFee.token || ethers.constants.AddressZero),
        amount: relayFee.amount
      },
      inputs
    };
  };

  // Calculate TypeHash
  const calculateTypeHash = (typehashStr) => {
    return ethers.utils.keccak256(ethers.utils.toUtf8Bytes(typehashStr));
  };

  // Show calculated result
  const showCalculatedTypeHash = () => {
    try {
      const intentHash = calculateTypeHash(intentTypehash);
      const actionsHash = calculateTypeHash(actionsTypehash);
      const relayFeeHash = calculateTypeHash(relayFeeTypehash);
      
      alert(`INTENT_TYPEHASH: ${intentHash}\nACTIONS_TYPEHASH: ${actionsHash}\nRELAY_FEE_TYPEHASH: ${relayFeeHash}`);
    } catch (error) {
      setError('Failed to calculate TypeHash: ' + error.message);
    }
  };

  // Signature function
  const signIntent = async () => {
    try {
      // Clear previous errors and success messages
      setError('');
      setSuccessMessage('');
      setDigest('');
      
      if (!signer) {
        setError('Please connect wallet first');
        return;
      }

      // Validate fields
      if (!verifyingContract) {
        setError('Please enter verifying contract address');
        return;
      }
      
      // Verify contract address is not the current connected account address
      const currentAccount = await signer.getAddress();
      if (verifyingContract.toLowerCase() === currentAccount.toLowerCase()) {
        setError('Verifying contract address cannot be the currently connected account address. Please use a real contract address');
        
        // Provide an example contract address for the current network
        if (exampleContracts[chainId]) {
          setVerifyingContract(exampleContracts[chainId]);
        }
        return;
      }
      
      // Verify contract address must be a valid contract address
      const isContract = await isContractAddress(verifyingContract);
      if (!isContract) {
        setError('Please enter a valid contract address. The current address may be an external account (EOA) and not a contract');
        return;
      }
      
      if (!chainId || chainId === '0') {
        setError('Please enter a valid Chain ID');
        return;
      }

      for (let i = 0; i < actionsList.length; i++) {
        const action = actionsList[i];
        if (!ethers.utils.isAddress(action.protocolAddress)) {
          setError(`Invalid protocol address for Action ${i+1}`);
          return;
        }
        if (!ethers.utils.isAddress(action.tokenIn)) {
          setError(`Invalid token address for Action ${i+1}`);
          return;
        }
      }

      if (!ethers.utils.isAddress(relayFee.token)) {
        setError('Invalid RelayFee token address');
        return;
      }

      // Prepare signature data
      const domain = getDomainData();
      const types = getTypes();
      const value = getSignatureData();

      console.log('Domain:', domain);
      console.log('Types:', types);
      console.log('Value:', value);

      // Calculate EIP-712 digest
      const domainSeparator = ethers.utils._TypedDataEncoder.hashDomain(domain);
      
      // Match the contract's hashing method
      // 1. Calculate INTENT_TYPEHASH, ACTIONS_TYPEHASH, RELAY_FEE_TYPEHASH
      const INTENT_TYPEHASH = calculateTypeHash(intentTypehash);
      const ACTIONS_TYPEHASH = calculateTypeHash(actionsTypehash);
      const RELAY_FEE_TYPEHASH = calculateTypeHash(relayFeeTypehash);
      
      console.log('INTENT_TYPEHASH:', INTENT_TYPEHASH);
      console.log('ACTIONS_TYPEHASH:', ACTIONS_TYPEHASH);
      console.log('RELAY_FEE_TYPEHASH:', RELAY_FEE_TYPEHASH);
      
      // 2. Hash each action using the same logic as in the contract
      const actionsHashes = value.actions.map(action => {
        return ethers.utils.keccak256(ethers.utils.defaultAbiCoder.encode(
          ['bytes32', 'bytes32', 'bytes32', 'address', 'uint256', 'address', 'uint256', 'address', 'uint256', 'address', 'uint256'],
          [
            ACTIONS_TYPEHASH,
            ethers.utils.keccak256(ethers.utils.toUtf8Bytes(action.action)),
            ethers.utils.keccak256(ethers.utils.toUtf8Bytes(action.protocol)),
            action.protocolAddress,
            action.chainId,
            action.tokenIn,
            action.amountIn,
            action.tokenOut,
            action.amountOut,
            action.receiver,
            action.slippage
          ]
        ));
      });
      
      // 3. Hash the actions array
      const actionsArrayHash = ethers.utils.keccak256(
        ethers.utils.solidityPack(
          Array(actionsHashes.length).fill('bytes32'),
          actionsHashes
        )
      );
      
      // 4. Hash the inputs array
      const inputsHashes = value.inputs.map(input => {
        return ethers.utils.keccak256(
          ethers.utils.solidityPack(['bytes'], [input])
        );
      });
      
      const inputsArrayHash = ethers.utils.keccak256(
        ethers.utils.solidityPack(
          Array(inputsHashes.length).fill('bytes32'),
          inputsHashes
        )
      );
      
      // 5. Hash the relay fee struct
      const relayFeeHash = ethers.utils.keccak256(ethers.utils.defaultAbiCoder.encode(
        ['bytes32', 'address', 'uint256'],
        [RELAY_FEE_TYPEHASH, value.relayFee.token, value.relayFee.amount]
      ));
      
      // 6. Hash the intent struct
      const structHash = ethers.utils.keccak256(ethers.utils.defaultAbiCoder.encode(
        ['bytes32', 'address', 'uint256', 'uint256', 'bytes32', 'bytes32', 'bytes32'],
        [
          INTENT_TYPEHASH,
          value.owner,
          value.nonce,
          value.deadline,
          actionsArrayHash,
          relayFeeHash,
          inputsArrayHash
        ]
      ));
      
      console.log('Actions Array Hash:', actionsArrayHash);
      console.log('Inputs Array Hash:', inputsArrayHash);
      console.log('Relay Fee Hash:', relayFeeHash);
      console.log('Struct Hash:', structHash);
      
      // Calculate final digest as per EIP-712
      const calculatedDigest = ethers.utils.keccak256(
        ethers.utils.solidityPack(
          ['string', 'bytes32', 'bytes32'],
          ['\x19\x01', domainSeparator, structHash]
        )
      );

      // Standard ethers.js way - using _TypedDataEncoder directly
      const standardStructHash = ethers.utils._TypedDataEncoder.hash(domain, types, value);
      console.log('Standard struct hash:', standardStructHash);
      console.log('Custom struct hash:', structHash);
      console.log('Are hashes equal:', standardStructHash === structHash);

      // Execute signature (using ethers v5's _signTypedData)
      const signature = await signer._signTypedData(domain, types, value);
      setSignature(signature);
      setDigest(calculatedDigest);
      setError('');
      setSuccessMessage('Signature successful!');
    } catch (error) {
      console.error(error);
      setError('Signature failed: ' + error.message);
    }
  };

  // Verify Intent function
  const verifyIntent = async () => {
    try {
      // Clear previous verification results
      setVerificationResult(null);
      setVerifiedAddress('');
      setVerifyError('');
      
      // Validate inputs
      if (!verifyDigest || !verifySignature) {
        setVerifyError('Please enter both the digest and signature for verification');
        return;
      }
      
      // Check that digest is a valid hex string
      if (!ethers.utils.isHexString(verifyDigest) || verifyDigest.length !== 66) {
        setVerifyError('Invalid digest format. Must be a 32-byte hex string with 0x prefix');
        return;
      }
      
      // Check that signature is a valid hex string
      if (!ethers.utils.isHexString(verifySignature)) {
        setVerifyError('Invalid signature format. Must be a hex string with 0x prefix');
        return;
      }
      
      // Split the signature into its components (r, s, v)
      const splitSig = ethers.utils.splitSignature(verifySignature);
      
      // The digest already includes the domain separator and struct hash
      // So we can directly recover the address
      const recoveredAddress = ethers.utils.recoverAddress(verifyDigest, splitSig);
      
      setVerifiedAddress(recoveredAddress);
      setVerificationResult(true);
      
      // Debug information
      console.log("Recovered address:", recoveredAddress);
      console.log("Connected account:", account);
      console.log("isConnected status:", isConnected);
      
      // Normalize addresses for comparison (convert to lowercase)
      const normalizedRecovered = recoveredAddress.toLowerCase();
      const normalizedCurrentAccount = account.toLowerCase();
      
      setNormalizedRecoveredAddress(normalizedRecovered);
      setNormalizedAccount(normalizedCurrentAccount);
      
      console.log("Normalized recovered address:", normalizedRecovered);
      console.log("Normalized account:", normalizedCurrentAccount);
      console.log("Addresses match:", normalizedRecovered === normalizedCurrentAccount);
      
      // Compare with current account if connected
      if (isConnected && account) {
        setSuccessMessage('Verification successful!');
      } else {
        setSuccessMessage('Verification successful!');
      }
    } catch (error) {
      console.error("Verification error:", error);
      setVerificationResult(false);
      setVerifyError('Verification failed: ' + error.message);
    }
  };

  // Use current signature and digest for verification
  const useCurrentSignature = () => {
    if (digest && signature) {
      setVerifyDigest(digest);
      setVerifySignature(signature);
    } else {
      setVerifyError('No current signature available. Please sign an intent first.');
    }
  };

  // Set current time plus 1 hour as default deadline time
  useEffect(() => {
    const oneHourLater = Math.floor(Date.now() / 1000) + 3600;
    setDeadline(oneHourLater.toString());
  }, []);

  // Listen for MetaMask network changes
  useEffect(() => {
    if (window.ethereum && isConnected) {
      const handleChainChanged = async (chainIdHex) => {
        console.log("Network changed to:", chainIdHex);
        // Update chainId
        const newChainId = parseInt(chainIdHex, 16).toString();
        setChainId(newChainId);
        
        // Reconnect wallet to refresh signer
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        setSigner(signer);
        
        // Automatically set the example contract address for the current network
        if (exampleContracts[newChainId]) {
          setVerifyingContract(exampleContracts[newChainId]);
        }
      };

      window.ethereum.on('chainChanged', handleChainChanged);
      
      // Clean up listener
      return () => {
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      };
    }
  }, [isConnected, exampleContracts]);

  // Add parameter for calldata
  const addCalldataParam = () => {
    setCalldataParams([...calldataParams, { type: 'address', value: '' }]);
  };

  // Remove parameter from calldata
  const removeCalldataParam = (index) => {
    const updatedParams = calldataParams.filter((_, i) => i !== index);
    setCalldataParams(updatedParams);
  };

  // Update calldata parameter
  const updateCalldataParam = (index, field, value) => {
    const updatedParams = [...calldataParams];
    if (updatedParams[index].type === 'MarketParams') {
      if (field === 'value') {
        updatedParams[index].value = value;
      } else {
        updatedParams[index].value = { ...updatedParams[index].value, [field]: value };
      }
    } else {
      updatedParams[index][field] = value;
      if (field === 'type' && value === 'MarketParams') {
        updatedParams[index].value = {
          loanToken: '',
          collateralToken: '',
          oracle: '',
          irm: '',
          lltv: ''
        };
      }
    }
    setCalldataParams(updatedParams);
  };

  // Helper: getSelectorFromSignature
  function getSelectorFromSignature(signature) {
    try {
      // signature: 'liquidate((address,address,address,address,uint256),address,uint256,uint256,uint256,bytes)'
      const fn = `function ${signature}`;
      const iface = new ethers.utils.Interface([fn]);
      const name = signature.split('(')[0];
      return iface.getSighash(name);
    } catch (e) {
      return '';
    }
  }

  // Replace signatureToSelector
  const signatureToSelector = (signature) => {
    try {
      return getSelectorFromSignature(signature);
    } catch (error) {
      console.error("Failed to convert signature to selector:", error);
      setCalldataError("Invalid function signature format");
      return "";
    }
  };

  // Format parameter value based on its type
  const formatParamValue = (type, value) => {
    try {
      if (type.startsWith('uint') || type.startsWith('int')) {
        // Handle integer types
        return ethers.BigNumber.from(value);
      } else if (type === 'address') {
        // Handle address type
        if (!ethers.utils.isAddress(value)) {
          throw new Error(`Invalid address: ${value}`);
        }
        return value;
      } else if (type === 'bool') {
        // Handle boolean type
        return value === 'true' || value === '1' || value === true;
      } else if (type === 'bytes32') {
        // Handle bytes32 type
        if (!ethers.utils.isHexString(value) && value.length !== 66) {
          throw new Error(`Invalid bytes32: ${value}`);
        }
        return value;
      } else if (type === 'bytes') {
        // Handle dynamic bytes
        if (!ethers.utils.isHexString(value)) {
          throw new Error(`Invalid bytes: ${value}`);
        }
        return value;
      } else if (type === 'string') {
        // Handle string type
        return value;
      } else {
        throw new Error(`Unsupported type: ${type}`);
      }
    } catch (error) {
      throw new Error(`Error formatting ${type} value: ${error.message}`);
    }
  };

  // Encode calldata
  const encodeCalldata = () => {
    try {
      setCalldataError('');
      setEncodedCalldata('');
      let selector;
      if (isFunctionSignature) {
        selector = signatureToSelector(functionSelector);
      } else {
        if (!functionSelector.startsWith('0x')) {
          selector = '0x' + functionSelector;
        } else {
          selector = functionSelector;
        }
        if (selector.length !== 10 || !ethers.utils.isHexString(selector)) {
          throw new Error("Invalid function selector format. Should be 4 bytes (e.g., 0xa9059cbb)");
        }
      }
      // Prepare types and values arrays
      const types = calldataParams.map(param =>
        param.type === 'MarketParams'
          ? 'tuple(address loanToken,address collateralToken,address oracle,address irm,uint256 lltv)'
          : param.type
      );
      const values = calldataParams.map(param => {
        if (param.type === 'MarketParams') {
          const v = param.value || {};
          return [v.loanToken, v.collateralToken, v.oracle, v.irm, v.lltv];
        } else {
          return formatParamValue(param.type, param.value);
        }
      });
      const encodedParams = ethers.utils.defaultAbiCoder.encode(types, values);
      const encodedParamsWithoutPrefix = encodedParams.slice(2);
      const result = selector + encodedParamsWithoutPrefix;
      setEncodedCalldata(result);
      setSuccessMessage("Calldata encoded successfully!");
    } catch (error) {
      console.error("Calldata encoding error:", error);
      setCalldataError(`Encoding failed: ${error.message}`);
    }
  };

  // Use encoded calldata as input
  const useEncodedCalldata = () => {
    if (encodedCalldata) {
      // Update the inputs array with the encoded calldata
      updateInput(0, encodedCalldata);
      setSuccessMessage("Encoded calldata added to inputs!");
    } else {
      setCalldataError("No encoded calldata available. Please encode calldata first.");
    }
  };

  // MarketParams encoding function
  const encodeMarketParams = () => {
    try {
      const abiCoder = ethers.utils.defaultAbiCoder;
      return abiCoder.encode(
        [
          'tuple(address loanToken,address collateralToken,address oracle,address irm,uint256 lltv)[]'
        ],
        [
          marketParamsList.map(params => [
            params.loanToken,
            params.collateralToken,
            params.oracle,
            params.irm,
            params.lltv
          ])
        ]
      );
    } catch (err) {
      return '';
    }
  };

  // Sign Permit function
  const signPermit = async () => {
    try {
      setPermitError('');
      setPermitResult({ v: '', r: '', s: '' });
      if (!signer) throw new Error('Please connect your wallet');
      if (!permitOwner || !permitSpender || !permitValue || !permitNonce || !permitDeadline || !permitChainId || !permitVerifyingContract || !permitName) {
        throw new Error('Please fill all the fields');
      }
      const domain = {
        name: permitName,
        version: permitVersion,
        chainId: parseInt(permitChainId),
        verifyingContract: permitVerifyingContract
      };
      const types = {
        Permit: [
          { name: 'owner', type: 'address' },
          { name: 'spender', type: 'address' },
          { name: 'value', type: 'uint256' },
          { name: 'nonce', type: 'uint256' },
          { name: 'deadline', type: 'uint256' }
        ]
      };
      const value = {
        owner: permitOwner,
        spender: permitSpender,
        value: permitValue,
        nonce: permitNonce,
        deadline: permitDeadline
      };
      const sig = await signer._signTypedData(domain, types, value);
      // Parse v, r, s
      const sigBytes = ethers.utils.arrayify(sig);
      const r = ethers.utils.hexlify(sigBytes.slice(0, 32));
      const s = ethers.utils.hexlify(sigBytes.slice(32, 64));
      const v = sigBytes[64];
      setPermitResult({ v, r, s });
    } catch (err) {
      setPermitError(err.message);
    }
  };

  // Update Permit Struct
  const updatePermitStruct = (field, value) => {
    setPermitStruct(prev => ({ ...prev, [field]: value }));
  };

  // Encode Permit Struct
  const encodePermitStruct = () => {
    setPermitStructError('');
    try {
      const abiCoder = ethers.utils.defaultAbiCoder;
      if (permitStruct.r && permitStruct.r.length !== 66) throw new Error('r must be 32 bytes (0x...)');
      if (permitStruct.s && permitStruct.s.length !== 66) throw new Error('s must be 32 bytes (0x...)');
      const encoded = abiCoder.encode(
        [
          'tuple(address token,address owner,uint256 value,uint256 deadline,uint8 v,bytes32 r,bytes32 s,uint256 relayFee)'
        ],
        [
          [
            permitStruct.token,
            permitStruct.owner,
            permitStruct.value,
            permitStruct.deadline,
            permitStruct.v,
            permitStruct.r,
            permitStruct.s,
            permitStruct.relayFee
          ]
        ]
      );
      setPermitStructCalldata(encoded);
    } catch (err) {
      setPermitStructError(err.message);
      setPermitStructCalldata('');
    }
  };

  // Update BuildAndExecuteCallValue
  const updateBuildAndExecuteCallValue = (field, value) => {
    setBuildAndExecuteCallValue(prev => ({ ...prev, [field]: value }));
  };

  // Encode BuildAndExecuteCallValue
  const encodeBuildAndExecuteCallValue = () => {
    setBuildAndExecuteCallError('');
    try {
      const abiCoder = ethers.utils.defaultAbiCoder;
      let adaptorData = buildAndExecuteCallValue.adaptorData;
      if (adaptorData && !adaptorData.startsWith('0x')) {
        throw new Error('adaptorData must start with 0x');
      }
      const encoded = abiCoder.encode(
        [
          'tuple(uint256 tokenOutPercent,address tokenOut,address target,uint256 value,string protocol,string action,address receiver,bytes adaptorData)'
        ],
        [
          [
            buildAndExecuteCallValue.tokenOutPercent,
            buildAndExecuteCallValue.tokenOut,
            buildAndExecuteCallValue.target,
            buildAndExecuteCallValue.value,
            buildAndExecuteCallValue.protocol,
            buildAndExecuteCallValue.action,
            buildAndExecuteCallValue.receiver,
            buildAndExecuteCallValue.adaptorData
          ]
        ]
      );
      setBuildAndExecuteCallCalldata(encoded);
    } catch (err) {
      setBuildAndExecuteCallError(err.message);
      setBuildAndExecuteCallCalldata('');
    }
  };

  // EIP-712 DCA Intent Type
  const DCA_EIP712_DOMAIN = (chainId) => ({
    name: 'DCAIntent',
    version: '1',
    chainId: parseInt(chainId || '1'),
    verifyingContract: '0x0000000000000000000000000000000000000000', // 可根據實際合約調整
  });

  const DCA_EIP712_TYPES = {
    DCAIntent: [
      { name: 'chainId', type: 'uint256' },
      { name: 'srcToken', type: 'address' },
      { name: 'dstToken', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'interval', type: 'uint256' },
      { name: 'priceImpact', type: 'uint256' },
      { name: 'epoch', type: 'uint256' },
    ],
  };

  const handleDcaInputChange = (e) => {
    const { name, value } = e.target;
    setDcaIntent((prev) => ({ ...prev, [name]: value }));
  };

  // 產生 EIP-712 Typed Data
  const getDcaTypedData = () => {
    return {
      types: DCA_EIP712_TYPES,
      domain: DCA_EIP712_DOMAIN(dcaIntent.chainId),
      primaryType: 'DCAIntent',
      message: {
        chainId: dcaIntent.chainId ? parseInt(dcaIntent.chainId) : 1,
        srcToken: dcaIntent.srcToken,
        dstToken: dcaIntent.dstToken,
        amount: dcaIntent.amount ? dcaIntent.amount.toString() : '0',
        interval: dcaIntent.interval ? dcaIntent.interval.toString() : '0',
        priceImpact: dcaIntent.priceImpact ? dcaIntent.priceImpact.toString() : '0',
        epoch: dcaIntent.epoch ? dcaIntent.epoch.toString() : '0',
      },
    };
  };

  // EIP-712 簽名
  const signDcaIntent = async () => {
    setDcaSignError('');
    setDcaSignature('');
    try {
      if (!window.ethereum || !account) {
        setDcaSignError('請先連接錢包');
        return;
      }
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const signer = provider.getSigner();
      const typedData = getDcaTypedData();
      const from = account;
      // MetaMask 需要 JSON 字串
      const data = JSON.stringify(typedData);
      const signature = await window.ethereum.request({
        method: 'eth_signTypedData_v4',
        params: [from, data],
      });
      setDcaSignature(signature);
    } catch (err) {
      setDcaSignError(err.message || '簽名失敗');
    }
  };

  // query get_user_tag API
  const fetchUserTag = async () => {
    setUserTagError('');
    setUserTagResult(null);
    if (!userTagAddress) {
      setUserTagError('Please enter an address');
      return;
    }
    try {
      const resp = await fetch('http://localhost:3001/get_user_tag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: userTagAddress })
      });
      const data = await resp.json();
      if (data.tags) {
        setUserTagResult(data.tags);
      } else {
        setUserTagError(data.result || 'No tags found');
      }
    } catch (err) {
      setUserTagError('API error: ' + err.message);
    }
  };

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col>
          <h1 className="text-center">Intent Signature Generator</h1>
          <p className="text-center text-muted">Sign and verify SuperIntent EIP-712 signature with MetaMask</p>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Connect Wallet</Card.Title>
              {isConnected ? (
                <div>
                  <p className="text-success">Connected: {account}</p>
                </div>
              ) : (
                <Button variant="primary" onClick={connectWallet}>
                  Connect MetaMask
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col>
          <Card className="border-primary">
            <Card.Header className="bg-primary text-white">
              <h4 className="mb-0">Sign Intent</h4>
            </Card.Header>
            <Card.Body>
              <p className="text-muted mb-4">Configure and sign an EIP-712 intent with the parameters below</p>
              
              {/* Custom INTENT_TYPEHASH */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title className="d-flex justify-content-between align-items-center">
                    Custom INTENT_TYPEHASH
                    <Form.Check 
                      type="switch"
                      id="custom-switch"
                      label="Use Custom TypeHash"
                      checked={useCustomTypehash}
                      onChange={(e) => setUseCustomTypehash(e.target.checked)}
                    />
                  </Card.Title>

                  {useCustomTypehash && (
                    <>
                      <Form.Group className="mb-3">
                        <Form.Label>INTENT_TYPEHASH</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={3}
                          value={intentTypehash}
                          onChange={(e) => setIntentTypehash(e.target.value)}
                          placeholder="Intent TypeHash string"
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>ACTIONS_TYPEHASH</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={2}
                          value={actionsTypehash}
                          onChange={(e) => setActionsTypehash(e.target.value)}
                          placeholder="Actions TypeHash string"
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>RELAY_FEE_TYPEHASH</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={1}
                          value={relayFeeTypehash}
                          onChange={(e) => setRelayFeeTypehash(e.target.value)}
                          placeholder="RelayFee TypeHash string"
                        />
                      </Form.Group>

                      <Button variant="info" onClick={showCalculatedTypeHash}>
                        Calculate TypeHash
                      </Button>
                    </>
                  )}
                </Card.Body>
              </Card>

              {/* EIP-712 Domain Data */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title>EIP-712 Domain Data</Card.Title>
                  <Form.Group className="mb-3">
                    <Form.Label>Chain ID</Form.Label>
                    <Form.Control
                      type="text"
                      value={chainId}
                      onChange={(e) => setChainId(e.target.value)}
                      placeholder="Chain ID"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Verifying Contract</Form.Label>
                    <div className="d-flex">
                      <Form.Control
                        type="text"
                        value={verifyingContract}
                        onChange={(e) => setVerifyingContract(e.target.value)}
                        placeholder="Verifying contract address"
                      />
                      <Button 
                        variant="outline-secondary" 
                        className="ms-2"
                        onClick={() => {
                          if (exampleContracts[chainId]) {
                            setVerifyingContract(exampleContracts[chainId]);
                          } else {
                            setError('No example contract address for current network');
                          }
                        }}
                      >
                        Use Example Contract
                      </Button>
                    </div>
                    <Form.Text className="text-muted">
                      Must be a contract address, not a regular account address
                    </Form.Text>
                  </Form.Group>
                </Card.Body>
              </Card>

              {/* Intent Basic Info */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title>Intent Basic Info</Card.Title>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Owner</Form.Label>
                    <Form.Control
                      type="text"
                      value={owner}
                      onChange={(e) => setOwner(e.target.value)}
                      placeholder="Owner address"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Nonce</Form.Label>
                    <Form.Control
                      type="text"
                      value={nonce}
                      onChange={(e) => setNonce(e.target.value)}
                      placeholder="Nonce"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Deadline</Form.Label>
                    <Form.Control
                      type="text"
                      value={deadline}
                      onChange={(e) => setDeadline(e.target.value)}
                      placeholder="Unix timestamp (seconds)"
                    />
                    <Form.Text className="text-muted">
                      Current value: {new Date(parseInt(deadline) * 1000).toLocaleString()}
                    </Form.Text>
                  </Form.Group>
                </Card.Body>
              </Card>

              {/* Actions */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title className="d-flex justify-content-between align-items-center">
                    Actions
                    <Button variant="success" size="sm" onClick={addAction}>
                      Add Action
                    </Button>
                  </Card.Title>

                  {actionsList.map((action, index) => (
                    <Card key={index} className="mb-3">
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                          <h5>Action #{index + 1}</h5>
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => removeAction(index)}
                            disabled={actionsList.length <= 1}
                          >
                            Remove
                          </Button>
                        </div>

                        <Form.Group className="mb-3">
                          <Form.Label>Action</Form.Label>
                          <Form.Select
                            value={action.action}
                            onChange={(e) => updateAction(index, 'action', e.target.value)}
                          >
                            <option value="Deposit">Deposit</option>
                            <option value="Withdraw">Withdraw</option>
                            <option value="Swap">Swap</option>
                            <option value="Liquidate">Liquidate</option>
                          </Form.Select>
                        </Form.Group>

                        {/* Show tokenOut and amountOut fields for Swap actions */}
                        {action.action === 'Swap' && (
                          <>
                            <Form.Group className="mb-3">
                              <Form.Label>Token Out</Form.Label>
                              <Form.Control
                                type="text"
                                placeholder="Token Out Address"
                                value={action.tokenOut}
                                onChange={(e) => updateAction(index, 'tokenOut', e.target.value)}
                              />
                            </Form.Group>
                            <Form.Group className="mb-3">
                              <Form.Label>Amount Out</Form.Label>
                              <Form.Control
                                type="text"
                                placeholder="Amount Out"
                                value={action.amountOut}
                                onChange={(e) => updateAction(index, 'amountOut', e.target.value)}
                              />
                            </Form.Group>
                          </>
                        )}

                        <Form.Group className="mb-3">
                          <Form.Label>Protocol Name</Form.Label>
                          <Form.Control
                            type="text"
                            value={action.protocol}
                            onChange={(e) => updateAction(index, 'protocol', e.target.value)}
                            placeholder="Protocol name (e.g., Uniswap, Aave)"
                          />
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>Protocol Address</Form.Label>
                          <Form.Control
                            type="text"
                            value={action.protocolAddress}
                            onChange={(e) => updateAction(index, 'protocolAddress', e.target.value)}
                            placeholder="Protocol contract address"
                          />
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>Chain ID</Form.Label>
                          <Form.Control
                            type="text"
                            value={action.chainId}
                            onChange={(e) => updateAction(index, 'chainId', e.target.value)}
                            placeholder="Chain ID for this action"
                          />
                          <Form.Text className="text-muted">
                            Chain ID where this protocol is deployed (default: current chain)
                          </Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>Token In</Form.Label>
                          <Form.Control
                            type="text"
                            value={action.tokenIn}
                            onChange={(e) => updateAction(index, 'tokenIn', e.target.value)}
                            placeholder="Input token address"
                          />
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>Amount In</Form.Label>
                          <Form.Control
                            type="text"
                            value={action.amountIn}
                            onChange={(e) => updateAction(index, 'amountIn', e.target.value)}
                            placeholder="Input amount"
                          />
                        </Form.Group>

                        {['Swap', 'Deposit', 'Withdraw', 'Liquidate'].includes(action.action) && (
                          <Form.Group className="mb-3">
                            <Form.Label>Receiver Address</Form.Label>
                            <Form.Control
                              type="text"
                              value={action.receiver}
                              onChange={(e) => updateAction(index, 'receiver', e.target.value)}
                              placeholder="Receiver address"
                            />
                          </Form.Group>
                        )}
                        {action.action === 'Swap' && (
                          <Form.Group className="mb-3">
                            <Form.Label>Slippage</Form.Label>
                            <Form.Control
                              type="text"
                              value={action.slippage}
                              onChange={(e) => updateAction(index, 'slippage', e.target.value)}
                              placeholder="Slippage"
                            />
                          </Form.Group>
                        )}
                      </Card.Body>
                    </Card>
                  ))}
                </Card.Body>
              </Card>

              {/* RelayFee */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title>RelayFee</Card.Title>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Token Address</Form.Label>
                    <Form.Control
                      type="text"
                      value={relayFee.token}
                      onChange={(e) => updateRelayFee('token', e.target.value)}
                      placeholder="Token address"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Amount</Form.Label>
                    <Form.Control
                      type="text"
                      value={relayFee.amount}
                      onChange={(e) => updateRelayFee('amount', e.target.value)}
                      placeholder="Amount"
                    />
                  </Form.Group>
                </Card.Body>
              </Card>

              {/* Inputs */}
              <Card className="mb-4">
                <Card.Body>
                  <Card.Title className="d-flex justify-content-between align-items-center">
                    Inputs
                    <Button variant="success" size="sm" onClick={addInput}>
                      Add Input
                    </Button>
                  </Card.Title>

                  {inputs.map((input, index) => (
                    <div key={index} className="mb-3 d-flex">
                      <Form.Control
                        type="text"
                        value={input}
                        onChange={(e) => updateInput(index, e.target.value)}
                        placeholder="Input data (hex)"
                      />
                      <Button
                        variant="danger"
                        className="ms-2"
                        onClick={() => removeInput(index)}
                        disabled={inputs.length <= 1}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </Card.Body>
              </Card>

              {/* Sign Button */}
              <div className="d-grid mt-4">
                <Button variant="primary" size="lg" onClick={signIntent}>
                  Sign Intent
                </Button>
              </div>
              
              {error && (
                <Alert variant="danger" className="mt-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <Alert.Heading>Signature Failed</Alert.Heading>
                    <Button variant="outline-danger" size="sm" onClick={() => setError('')}>
                      Close
                    </Button>
                  </div>
                  <p>{error}</p>
                  {error.includes('contract address') && (
                    <div>
                      <hr />
                      <p className="mb-0">
                        Tip: Click the "Use Example Contract" button above to use a valid contract address.
                      </p>
                    </div>
                  )}
                  {error.includes('protocol address') && (
                    <div>
                      <hr />
                      <p className="mb-0">
                        Tip: Protocol address must be a valid Ethereum address, for example: 0x1234...abcd.
                      </p>
                    </div>
                  )}
                  {error.includes('token address') && (
                    <div>
                      <hr />
                      <p className="mb-0">
                        Tip: Token address must be a valid Ethereum address. You can use {ethers.constants.AddressZero} for testing.
                      </p>
                    </div>
                  )}
                  {error.includes('Chain ID') && (
                    <div>
                      <hr />
                      <p className="mb-0">
                        Tip: Please make sure MetaMask is connected and the Chain ID field is valid.
                      </p>
                    </div>
                  )}
                  {error.includes('network') && (
                    <div>
                      <hr />
                      <p className="mb-0">
                        Tip: Network connection issue. Please make sure MetaMask is connected to the correct network.
                      </p>
                    </div>
                  )}
                </Alert>
              )}
              
              {successMessage && !verificationResult && (
                <Alert variant="success" className="mt-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <span>{successMessage}</span>
                    <Button variant="outline-success" size="sm" onClick={() => setSuccessMessage('')}>
                      Close
                    </Button>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Show digest only when it exists and there's no error */}
      {digest && !error && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Body>
                <Card.Title>Digest Result</Card.Title>
                <p className="text-muted small">This is the <strong>message hash</strong> that was signed according to EIP-712 standard</p>
                <Form.Group>
                  <div className="d-flex">
                    <Form.Control
                      value={digest}
                      readOnly
                    />
                    <Button
                      variant="outline-secondary"
                      className="ms-2"
                      onClick={() => {
                        navigator.clipboard.writeText(digest);
                        setSuccessMessage('Digest copied to clipboard!');
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Show signature only when it exists and there's no error */}
      {signature && !error && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Body>
                <Card.Title>Signature Result</Card.Title>
                <p className="text-muted small">This is the <strong>signed message</strong> according to EIP-712 standard</p>
                <Form.Group>
                  <div className="d-flex">
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={signature}
                      readOnly
                    />
                    <Button
                      variant="outline-secondary"
                      className="ms-2"
                      onClick={() => {
                        navigator.clipboard.writeText(signature);
                        setSuccessMessage('Signature copied to clipboard!');
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </Form.Group>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Visual Separator - only show when there are results to display */}
      {((digest && !error) || (signature && !error)) && (
        <Row className="my-5">
          <Col>
            <div className="d-flex align-items-center">
              <div className="flex-grow-1 border-top border-secondary"></div>
              <h3 className="mx-3 text-secondary">Verification Section</h3>
              <div className="flex-grow-1 border-top border-secondary"></div>
            </div>
          </Col>
        </Row>
      )}

      {/* Verify Intent Section */}
      <Row className="mb-4">
        <Col>
          <Card className="border-info">
            <Card.Header className="bg-info text-white">
              <h4 className="mb-0">Verify Intent</h4>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">Verify a signature by entering the digest and signature</p>
              
              <Form.Group className="mb-3">
                <Form.Label>Digest</Form.Label>
                <Form.Control
                  type="text"
                  value={verifyDigest}
                  onChange={(e) => setVerifyDigest(e.target.value)}
                  placeholder="Enter the message hash digest (0x...)"
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Signature</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={verifySignature}
                  onChange={(e) => setVerifySignature(e.target.value)}
                  placeholder="Enter the signature (0x...)"
                />
              </Form.Group>

              <div className="d-flex gap-2">
                <Button variant="info" onClick={verifyIntent}>
                  Verify Intent
                </Button>
                <Button variant="outline-info" onClick={useCurrentSignature}>
                  Use Current Signature
                </Button>
              </div>

              {verifyError && (
                <Alert variant="danger" className="mt-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <Alert.Heading>Verification Failed</Alert.Heading>
                    <Button variant="outline-danger" size="sm" onClick={() => setVerifyError('')}>
                      Close
                    </Button>
                  </div>
                  <p>{verifyError}</p>
                </Alert>
              )}

              {verificationResult !== null && (
                <Alert variant={verificationResult ? "success" : "danger"} className="mt-3">
                  {verificationResult ? (
                    <div>
                      <strong>Verification successful!</strong>
                      <p>Recovered signer address: {verifiedAddress}</p>
                      {isConnected && account && normalizedRecoveredAddress === normalizedAccount ? (
                        <p className="mb-0 mt-2 text-success">The signature matches your connected wallet address.</p>
                      ) : (
                        isConnected && account && (
                          <p className="mb-0 mt-2 text-warning">The signature is from a different address than your connected wallet.</p>
                        )
                      )}
                    </div>
                  ) : (
                    <div>
                      <strong>Verification failed!</strong>
                      <p>The signature could not be verified for the given digest.</p>
                    </div>
                  )}
                </Alert>
              )}
              
              {successMessage && verificationResult && (
                <Alert variant="success" className="mt-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <span>{successMessage}</span>
                    <Button variant="outline-success" size="sm" onClick={() => setSuccessMessage('')}>
                      Close
                    </Button>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Visual Separator for Calldata Encoder */}
      <Row className="my-5">
        <Col>
          <div className="d-flex align-items-center">
            <div className="flex-grow-1 border-top border-secondary"></div>
            <h3 className="mx-3 text-secondary">Inputs Calldata Encoder Section</h3>
            <div className="flex-grow-1 border-top border-secondary"></div>
          </div>
        </Col>
      </Row>

      {/* Calldata Encoder Section - moved to the bottom */}
      <Row className="mb-4">
        <Col>
          <Card className="border-success">
            <Card.Header className="bg-success text-white">
              <h4 className="mb-0">Calldata Encoder</h4>
            </Card.Header>
            <Card.Body>
              <p className="text-muted mb-4">Generate encoded calldata for smart contract interactions</p>
              
              {/* Function Selector/Signature Input */}
              <Form.Group className="mb-3">
                <Form.Label>
                  <Form.Check
                    inline
                    type="radio"
                    label="Function Signature"
                    name="selectorType"
                    checked={isFunctionSignature}
                    onChange={() => setIsFunctionSignature(true)}
                  />
                  <Form.Check
                    inline
                    type="radio"
                    label="Function Selector"
                    name="selectorType"
                    checked={!isFunctionSignature}
                    onChange={() => setIsFunctionSignature(false)}
                  />
                </Form.Label>
                <Form.Control
                  type="text"
                  value={functionSelector}
                  onChange={(e) => setFunctionSelector(e.target.value)}
                  placeholder={isFunctionSignature ? "e.g. transfer(address,uint256)" : "e.g. 0xa9059cbb"}
                />
                <Form.Text className="text-muted">
                  {isFunctionSignature 
                    ? "Enter the function signature (e.g., 'transfer(address,uint256)')" 
                    : "Enter the 4-byte function selector (e.g., '0xa9059cbb')"}
                </Form.Text>
              </Form.Group>
              
              {/* Parameters */}
              <Card className="mb-3">
                <Card.Body>
                  <Card.Title className="d-flex justify-content-between align-items-center">
                    Parameters
                    <Button variant="success" size="sm" onClick={addCalldataParam}>
                      Add Parameter
                    </Button>
                  </Card.Title>
                  
                  {calldataParams.map((param, index) => (
                    <div key={index} className="mb-3 d-flex gap-2 align-items-center">
                      <Form.Select 
                        style={{ width: '180px' }}
                        value={param.type}
                        onChange={(e) => updateCalldataParam(index, 'type', e.target.value)}
                      >
                        {dataTypes.map((type) => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </Form.Select>
                      {param.type === 'MarketParams' ? (
                        <div className="d-flex flex-wrap gap-2 align-items-center" style={{ flexGrow: 1 }}>
                          <Form.Control
                            style={{ minWidth: 120 }}
                            type="text"
                            value={param.value?.loanToken || ''}
                            onChange={e => updateCalldataParam(index, 'loanToken', e.target.value)}
                            placeholder="loanToken"
                          />
                          <Form.Control
                            style={{ minWidth: 120 }}
                            type="text"
                            value={param.value?.collateralToken || ''}
                            onChange={e => updateCalldataParam(index, 'collateralToken', e.target.value)}
                            placeholder="collateralToken"
                          />
                          <Form.Control
                            style={{ minWidth: 120 }}
                            type="text"
                            value={param.value?.oracle || ''}
                            onChange={e => updateCalldataParam(index, 'oracle', e.target.value)}
                            placeholder="oracle"
                          />
                          <Form.Control
                            style={{ minWidth: 120 }}
                            type="text"
                            value={param.value?.irm || ''}
                            onChange={e => updateCalldataParam(index, 'irm', e.target.value)}
                            placeholder="irm"
                          />
                          <Form.Control
                            style={{ minWidth: 120 }}
                            type="text"
                            value={param.value?.lltv || ''}
                            onChange={e => updateCalldataParam(index, 'lltv', e.target.value)}
                            placeholder="lltv"
                          />
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            onClick={() =>
                              updateCalldataParam(index, 'value', {
                                loanToken: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                                collateralToken: '0x35D8949372D46B7a3D5A56006AE77B215fc69bC0',
                                oracle: '0x1325Eb089Ac14B437E78D5D481e32611F6907eF8',
                                irm: '0x870aC11D48B15DB9a138Cf899d20F13F79Ba00BC',
                                lltv: '860000000000000000'
                              })
                            }
                            style={{ minWidth: 80 }}
                          >
                            Example
                          </Button>
                        </div>
                      ) : (
                        <Form.Control
                          style={{ flexGrow: 1 }}
                          type="text"
                          value={param.value}
                          onChange={(e) => updateCalldataParam(index, 'value', e.target.value)}
                          placeholder={`Value for ${param.type}`}
                        />
                      )}
                      <Button
                        variant="danger"
                        onClick={() => removeCalldataParam(index)}
                        disabled={calldataParams.length <= 1}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </Card.Body>
              </Card>
              
              {/* Encode Button */}
              <div className="d-flex gap-2">
                <Button variant="success" onClick={encodeCalldata}>
                  Encode Calldata
                </Button>
                <Button 
                  variant="outline-success" 
                  onClick={useEncodedCalldata}
                  disabled={!encodedCalldata}
                >
                  Use as Input
                </Button>
              </div>
              
              {/* Display encoded calldata */}
              {encodedCalldata && (
                <Card className="mt-3">
                  <Card.Body>
                    <Card.Title>Encoded Calldata</Card.Title>
                    <div className="d-flex mt-2">
                      <Form.Control
                        as="textarea"
                        rows={2}
                        value={encodedCalldata}
                        readOnly
                      />
                      <Button
                        variant="outline-secondary"
                        className="ms-2"
                        onClick={() => {
                          navigator.clipboard.writeText(encodedCalldata);
                          setSuccessMessage('Calldata copied to clipboard!');
                        }}
                      >
                        Copy
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              )}
              
              {/* Error display */}
              {calldataError && (
                <Alert variant="danger" className="mt-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <Alert.Heading>Encoding Failed</Alert.Heading>
                    <Button variant="outline-danger" size="sm" onClick={() => setCalldataError('')}>
                      Close
                    </Button>
                  </div>
                  <p>{calldataError}</p>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Calldata Encoder Section - MarketParams */}
      <Row className="mb-4">
        <Col>
          <Card className="border-success">
            <Card.Header className="bg-success text-white">
              <h4 className="mb-0">Permit1 Signature Tool (EIP-2612)</h4>
            </Card.Header>
            <Card.Body>
              {/* Example Button */}
              <Button
                variant="secondary"
                className="mb-3"
                onClick={() => {
                  setPermitOwner('0x2B93633F740412DD96F003eEEBf830369945ceBe');
                  setPermitSpender('0x508D256b14072A37B5ab94257984fAc2d2B772bB');
                  setPermitValue('1718652102');
                  setPermitNonce('0');
                  setPermitDeadline('1800000000');
                  setPermitChainId('1');
                  setPermitVerifyingContract('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48');
                  setPermitName('USD Coin');
                  setPermitVersion('2');
                }}
              >
                Example
              </Button>
              {/* Permit1 input fields */}
              <Form.Group className="mb-2">
                <Form.Label>Owner</Form.Label>
                <Form.Control type="text" value={permitOwner} onChange={e => setPermitOwner(e.target.value)} placeholder="Owner address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Spender</Form.Label>
                <Form.Control type="text" value={permitSpender} onChange={e => setPermitSpender(e.target.value)} placeholder="Spender address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Value</Form.Label>
                <Form.Control type="text" value={permitValue} onChange={e => setPermitValue(e.target.value)} placeholder="Value (uint256)" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Nonce</Form.Label>
                <Form.Control type="text" value={permitNonce} onChange={e => setPermitNonce(e.target.value)} placeholder="Nonce (uint256)" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Deadline</Form.Label>
                <Form.Control type="text" value={permitDeadline} onChange={e => setPermitDeadline(e.target.value)} placeholder="Deadline (uint256)" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Chain ID</Form.Label>
                <Form.Control type="text" value={permitChainId} onChange={e => setPermitChainId(e.target.value)} placeholder="Chain ID" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Verifying Contract</Form.Label>
                <Form.Control type="text" value={permitVerifyingContract} onChange={e => setPermitVerifyingContract(e.target.value)} placeholder="Verifying contract address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Token Name</Form.Label>
                <Form.Control type="text" value={permitName} onChange={e => setPermitName(e.target.value)} placeholder="Token Name (EIP-712 domain)" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Version</Form.Label>
                <Form.Control type="text" value={permitVersion} onChange={e => setPermitVersion(e.target.value)} placeholder="Version (default 1)" />
              </Form.Group>
              <Button variant="success" className="mt-2" onClick={signPermit}>Sign Permit</Button>
              {permitError && (
                <Alert variant="danger" className="mt-3">{permitError}</Alert>
              )}
              {(permitResult.v && permitResult.r && permitResult.s) && (
                <Alert variant="success" className="mt-3">
                  <div>v: {permitResult.v}</div>
                  <div>r: {permitResult.r}</div>
                  <div>s: {permitResult.s}</div>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    className="mt-2"
                    onClick={() => setPermitStruct(prev => ({
                      ...prev,
                      v: permitResult.v,
                      r: permitResult.r,
                      s: permitResult.s
                    }))}
                  >
                    Copy v r s to Permit Struct
                  </Button>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Permit Struct Calldata Encoder */}
      <Row className="mb-4">
        <Col>
          <Card className="border-info">
            <Card.Header className="bg-info text-white">
              <h4 className="mb-0">Permit Struct Calldata Encoder</h4>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-2">
                <Form.Label>Token</Form.Label>
                <Form.Control type="text" value={permitStruct.token} onChange={e => updatePermitStruct('token', e.target.value)} placeholder="address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Owner</Form.Label>
                <Form.Control type="text" value={permitStruct.owner} onChange={e => updatePermitStruct('owner', e.target.value)} placeholder="address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Value</Form.Label>
                <Form.Control type="text" value={permitStruct.value} onChange={e => updatePermitStruct('value', e.target.value)} placeholder="uint256" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Deadline</Form.Label>
                <Form.Control type="text" value={permitStruct.deadline} onChange={e => updatePermitStruct('deadline', e.target.value)} placeholder="uint256" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>V</Form.Label>
                <Form.Control type="text" value={permitStruct.v} onChange={e => updatePermitStruct('v', e.target.value)} placeholder="uint8" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>R</Form.Label>
                <Form.Control type="text" value={permitStruct.r} onChange={e => updatePermitStruct('r', e.target.value)} placeholder="bytes32" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>S</Form.Label>
                <Form.Control type="text" value={permitStruct.s} onChange={e => updatePermitStruct('s', e.target.value)} placeholder="bytes32" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>RelayFee</Form.Label>
                <Form.Control type="text" value={permitStruct.relayFee} onChange={e => updatePermitStruct('relayFee', e.target.value)} placeholder="uint256" />
              </Form.Group>
              <Button variant="primary" className="mt-2" onClick={encodePermitStruct}>Encode Calldata</Button>
              {permitStructError && (
                <Alert variant="danger" className="mt-3">{permitStructError}</Alert>
              )}
              {permitStructCalldata && (
                <Alert variant="success" className="mt-3">
                  <div className="d-flex align-items-center">
                    <Form.Control as="textarea" rows={2} value={permitStructCalldata} readOnly />
                    <Button
                      variant="outline-secondary"
                      className="ms-2"
                      onClick={() => navigator.clipboard.writeText(permitStructCalldata)}
                    >
                      Copy
                    </Button>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* BuildAndExecuteCallValue Struct Calldata Encoder */}
      <Row className="mb-4">
        <Col>
          <Card className="border-info">
            <Card.Header className="bg-info text-white">
              <h4 className="mb-0">BuildAndExecuteCallValue Struct Calldata Encoder</h4>
            </Card.Header>
            <Card.Body>
              {/* Example Button */}
              <Button
                variant="secondary"
                className="mb-3"
                onClick={() => setBuildAndExecuteCallValue({
                  tokenOutPercent: '10000',
                  tokenOut: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                  target: '0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb',
                  value: '0',
                  protocol: 'Morpho',
                  action: 'Liquidate',
                  receiver: '0x2B93633F740412DD96F003eEEBf830369945ceBe',
                  adaptorData: '0x'
                })}
              >
                Example
              </Button>
              <Form.Group className="mb-2">
                <Form.Label>TokenOutPercent</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.tokenOutPercent} onChange={e => updateBuildAndExecuteCallValue('tokenOutPercent', e.target.value)} placeholder="uint256" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>TokenOut</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.tokenOut} onChange={e => updateBuildAndExecuteCallValue('tokenOut', e.target.value)} placeholder="address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Target</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.target} onChange={e => updateBuildAndExecuteCallValue('target', e.target.value)} placeholder="address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Value</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.value} onChange={e => updateBuildAndExecuteCallValue('value', e.target.value)} placeholder="uint256" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Protocol</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.protocol} onChange={e => updateBuildAndExecuteCallValue('protocol', e.target.value)} placeholder="string" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Action</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.action} onChange={e => updateBuildAndExecuteCallValue('action', e.target.value)} placeholder="string" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Receiver</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.receiver} onChange={e => updateBuildAndExecuteCallValue('receiver', e.target.value)} placeholder="address" />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>AdaptorData</Form.Label>
                <Form.Control type="text" value={buildAndExecuteCallValue.adaptorData} onChange={e => updateBuildAndExecuteCallValue('adaptorData', e.target.value)} placeholder="bytes (0x...)" />
              </Form.Group>
              <Button variant="primary" className="mt-2" onClick={encodeBuildAndExecuteCallValue}>Encode Calldata</Button>
              {buildAndExecuteCallError && (
                <Alert variant="danger" className="mt-3">{buildAndExecuteCallError}</Alert>
              )}
              {buildAndExecuteCallCalldata && (
                <Alert variant="success" className="mt-3">
                  <div className="d-flex align-items-center">
                    <Form.Control as="textarea" rows={2} value={buildAndExecuteCallCalldata} readOnly />
                    <Button
                      variant="outline-secondary"
                      className="ms-2"
                      onClick={() => navigator.clipboard.writeText(buildAndExecuteCallCalldata)}
                    >
                      Copy
                    </Button>
                  </div>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* DCA Intent Section */}
      <Card className="mb-4">
        <Card.Header><b>Sign DCA Intent (EIP-712)</b></Card.Header>
        <Card.Body>
          <Form>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Chain ID</Form.Label></Col>
              <Col md={8}><Form.Control name="chainId" value={dcaIntent.chainId} onChange={handleDcaInputChange} placeholder="e.g. 1" /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Source Token (address)</Form.Label></Col>
              <Col md={8}><Form.Control name="srcToken" value={dcaIntent.srcToken} onChange={handleDcaInputChange} placeholder="0x..." /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Destination Token (address)</Form.Label></Col>
              <Col md={8}><Form.Control name="dstToken" value={dcaIntent.dstToken} onChange={handleDcaInputChange} placeholder="0x..." /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Amount</Form.Label></Col>
              <Col md={8}><Form.Control name="amount" value={dcaIntent.amount} onChange={handleDcaInputChange} placeholder="Unit: wei" /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Interval (days)</Form.Label></Col>
              <Col md={8}><Form.Control name="interval" value={dcaIntent.interval} onChange={handleDcaInputChange} placeholder="e.g. 7 days" /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Price Impact </Form.Label></Col>
              <Col md={8}><Form.Control name="priceImpact" value={dcaIntent.priceImpact} onChange={handleDcaInputChange} placeholder="e.g. 100 = 1%" /></Col>
            </Row>
            <Row className="mb-2">
              <Col md={4}><Form.Label>Epoch</Form.Label></Col>
              <Col md={8}><Form.Control name="epoch" value={dcaIntent.epoch} onChange={handleDcaInputChange} placeholder="e.g. 4 runs" /></Col>
            </Row>
            <Button variant="primary" onClick={signDcaIntent} className="mt-2">Sign DCA Intent</Button>
          </Form>
          {dcaSignature && (
            <Alert variant="success" className="mt-3">
              <b>Signature Result:</b>
              <div style={{ wordBreak: 'break-all' }}>{dcaSignature}</div>
            </Alert>
          )}
          {dcaSignError && (
            <Alert variant="danger" className="mt-3">{dcaSignError.replace('請先連接錢包', 'Please connect your wallet').replace('簽名失敗', 'Signature failed')}</Alert>
          )}
        </Card.Body>
      </Card>

      {/* User Tag Section */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Get User Tag</Card.Title>
              <Form.Group className="mb-3">
                <Form.Label>Address</Form.Label>
                <Form.Control
                  type="text"
                  value={userTagAddress}
                  onChange={e => setUserTagAddress(e.target.value)}
                  placeholder="Enter user address"
                />
              </Form.Group>
              <Button variant="primary" onClick={fetchUserTag}>
                Query Tags
              </Button>
              {userTagError && (
                <Alert variant="danger" className="mt-3">{userTagError}</Alert>
              )}
              {userTagResult && (
                <Alert variant="success" className="mt-3">
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                    {JSON.stringify(userTagResult, null, 2)}
                  </pre>
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default App; 