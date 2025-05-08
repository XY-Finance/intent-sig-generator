# Intent Signature Generator

An useful tool for testing and generating SuperIntent EIP-712 signatures for the SuperIntentRouter contract, with advanced utilities for calldata encoding, permit signatures, and more.

## Features

- **MetaMask wallet integration**
- **Customizable type definitions** (INTENT_TYPEHASH, ACTIONS_TYPEHASH, RELAY_FEE_TYPEHASH)
- **Type hash calculation** for custom EIP-712 structures
- **Multi-action management**: Deposit, Withdraw, Swap (add/remove multiple actions)
- **EIP-712 signature generation and verification**
- **Digest and signature display**: Copyable message hash and signature
- **Signature verification**: Check signatures against digests and recover signer address
- **Inputs Calldata Encoder**: Encode arbitrary calldata for contract calls, including support for custom types (e.g., MarketParams)
- **Permit1 (EIP-2612) signature tool**: Generate and parse permit signatures for ERC20 tokens
- **Permit Struct calldata encoder**: ABI-encode permit struct for contract calls
- **BuildAndExecuteCallValue struct encoder**: ABI-encode advanced call structs for integrations

## Quick Start

```bash
cd intent-sig-generator
npm install
npm start
```

The application will open automatically at http://localhost:3000

## Usage Guide

### 1. Wallet Connection
- Connect your MetaMask wallet using the "Connect MetaMask" button.

### 2. TypeHash Customization (optional)
- Enable custom TypeHash with the toggle switch
- Modify hash definitions as needed
- Calculate and view resulting hash values

### 3. Domain Configuration
- Chain ID: Auto-detected from connected network (editable)
- Verifying Contract: Input a valid contract address (use example contracts for common networks)

### 4. Intent Parameters
- Owner: Your wallet address (auto-filled)
- Nonce: Unique transaction identifier
- Deadline: Expiration timestamp (defaults to current time + 1 hour)

### 5. Action Configuration
- Add multiple actions with the "Add Action" button
- Configure each action (Deposit, Withdraw, Swap)
- Additional fields appear for Swap operations
- Set protocol name/address, chain ID, tokens, amounts, receiver, slippage, etc.

### 6. Fee Settings
- Specify the token address and amount for relay fees

### 7. Input Data
- Add hexadecimal input data as needed for complex operations
- Use the Calldata Encoder to generate ABI-encoded input data

### 8. Signature Generation
- Click "Sign Intent" to initiate MetaMask signature request
- View the resulting EIP-712 message digest (the hash that was signed)
- Copy the digest for verification with smart contracts
- View and copy the complete signature result

### 9. Signature Verification
- Enter a digest and signature to verify
- Recover the signer address and check against your connected wallet

### 10. Calldata Encoder
- Encode calldata for any contract function
- Enter function signature or selector, add parameters (including MarketParams)
- Encode and copy the result, or use as input for intent

### 11. MarketParams Encoder
- Encode a list of MarketParams tuples for DeFi protocols
- Fill in loanToken, collateralToken, oracle, irm, lltv fields
- Encode and copy the result

### 12. Permit1 (EIP-2612) Signature Tool
- Fill in owner, spender, value, nonce, deadline, chain ID, verifying contract, token name, and version
- Generate a permit signature (v, r, s)
- Copy v/r/s to Permit Struct encoder

### 13. Permit Struct Calldata Encoder
- Fill in all permit struct fields (token, owner, value, deadline, v, r, s, relayFee)
- Encode and copy the calldata for contract calls

### 14. BuildAndExecuteCallValue Struct Encoder
- Fill in all struct fields (tokenOutPercent, tokenOut, target, value, protocol, action, receiver, adaptorData)
- Encode and copy the calldata for contract calls

## Debugging Tools

The browser console provides detailed information about:
- Domain data structure
- Type definitions
- Complete signature payload
- EIP-712 digest calculation
