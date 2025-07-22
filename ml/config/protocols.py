PROTOCOLS = {
    1: {
        "0xc3d688b66703497daa19211eedff47f25384cdc3": {
            "name": "COMPOUND_V3_USDC",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",  # supply
        },
        "0xa17581a9e3356d9a858b789d68b4d866e593ae94": {
            "name": "COMPOUND_V3_ETH",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",  # supply
        },
        "0x3afdc9bca9213a35503b077a6072f3d0d5ab0840": {
            "name": "COMPOUND_V3_USDT",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",  # supply
        },
        "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": {
            "name": "AAVE_V3_POOL",
            "type": "Lending",
            "key_method": "0x617ba037",  # supply
        },
        "0xd63070114470f685b75b74d60eec7c1113d33a3d": {
            "name": "MORPHO_USUAL_BOOSTED_USDC",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0xbeef01735c132ada46aa9aa4c54623caa92a64cb": {
            "name": "MORPHO_STEAKHOUSE_USDC",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0x8eb67a509616cd6a7c1b3c8c21d48ff57df3d458": {
            "name": "MORPHO_GAUNTLET_USDC_CORE",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0x0f359fd18bda75e9c49bc027e7da59a4b01bf32a": {
            "name": "MORPHO_RELEND_USDC",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0xbeef047a543e45807105e51a8bbefcc5950fcfba": {
            "name": "MORPHO_STEAKHOUSE_USDT",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0xdd0f28e19c1780eb6396170735d45153d261490d": {
            "name": "MORPHO_GAUNTLET_USDC_PRIME",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0x8cb3649114051ca5119141a34c200d65dc0faa73": {
            "name": "MORPHO_GAUNTLET_USDT_PRIME",
            "type": "Lending",
            "key_method": "0x6e553f65",  # deposit
        },
        "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
            "name": "USDC",
            "type": "StableCoin",
            "key_method": "",
        },
        "0xdac17f958d2ee523a2206206994597c13d831ec7": {
            "name": "USDT",
            "type": "StableCoin",
            "key_method": "",
        },
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
            "name": "WETH",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x6b175474e89094c44da98b954eedeac495271d0f": {
            "name": "DAI",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": {
            "name": "UNISWAP_V2_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0xe592427a0aece92de3edee1f18e0157c05861564": {
            "name": "UNISWAP_V3_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0x66a9893cc07d91d95644aedd05d03f95e1dba8af": {
            "name": "UNISWAP_V4_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0x1111111254eeb25477b68fb85ed929f73a960582": {
            "name": "1INCH_V5",
            "type": "Dex",
            "key_method": "",
        },
        "0x11111112542d85b3ef69ae05771c2dccff4faa26": {
            "name": "1INCH_V3",
            "type": "Dex",
            "key_method": "",
        },
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f": {
            "name": "SUSHISWAP",
            "type": "Dex",
            "key_method": "",
        },
        "0xba12222222228d8ba445958a75a0704d566bf2c8": {
            "name": "BALANCER_V2_VAULT",
            "type": "Dex",
            "key_method": "",
        },
        "0xdef171fe48cf0115b1d80b88dc8eab59176fee57": {
            "name": "PARASWAP_V5",
            "type": "Dex",
            "key_method": "",
        },
        "0x6131b5fae19ea4f9d964eac0408e4408b66337b5": {
            "name": "KYBERSWAP_V2",
            "type": "Dex",
            "key_method": "",
        },
        "0x7e7a0e201fd38d3adaa9523da6c109a07118c96a": {
            "name": "SYNAPSE_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x5427fefa711eff984124bfbb1ab6fbf5e3da1820": {
            "name": "CELER_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5": {
            "name": "ACROSS_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x0e83ded9f80e1c92549615d96842f5cb64a08762": {
            "name": "OWLTO_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": {
            "name": "POLYGON_POS_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x4dbd4fc535ac27206064b68ffcf827b0a60bab3f": {
            "name": "ARBITRUM_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x0654874eb7f59c6f5b39931fc45dc45337c967c3": {
            "name": "MAYAN_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x77b2043768d28e9c9ab44e1abfc95944bce57931": {
            "name": "STARGATE_V2_BRIDGE_ETH",
            "type": "Bridge",
            "key_method": "",
        },
        "0xc026395860db2d07ee33e05fe50ed7bd583189c7": {
            "name": "STARGATE_V2_BRIDGE_USDC",
            "type": "Bridge",
            "key_method": "",
        },
        "0x933597a323eb81cae705c5bc29985172fd5a3973": {
            "name": "STARGATE_V2_BRIDGE_USDT",
            "type": "Bridge",
            "key_method": "",
        },
        "0x6065a982f04f759b7d2d042d2864e569fad84214": {
            "name": "CELER_CCTP_PROXY",
            "type": "Bridge",
            "key_method": "",
        },
    },
    42161: {
        "0x9c4ec768c28520b50860ea7a15bd7213a9ff58bf": {
            "name": "COMPOUND_V3_USDC",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0x6f7d514bbd4aff3bcd1140b7344b32f063dee486": {
            "name": "COMPOUND_V3_ETH",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0xd98be00b5d27fc98112bde293e487f8d4ca57d07": {
            "name": "COMPOUND_V3_USDT",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0xa5edbdd9646f8dff606d7448e414884c7d905dca": {
            "name": "COMPOUND_V3_USDC_E",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0x794a61358d6845594f94dc1db02a252b5b4814ad": {
            "name": "AAVE_V3_POOL",
            "type": "Lending",
            "key_method": "0x617ba037",
        },
        "0xb5ee21786d28c5ba61661550879475976b707099": {
            "name": "AAVE_V3_WRAPPED_TOKEN_GATEWAY",
            "type": "Lending",
            "key_method": "0x474cf53d",
        },
        "0x5283beced7adf6d003225c13896e536f2d4264ff": {
            "name": "AAVE_V3_WRAPPED_TOKEN_GATEWAY_NEW",
            "type": "Lending",
            "key_method": "0x474cf53d",
        },
        "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24": {
            "name": "UNISWAP_V2_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0xe592427a0aece92de3edee1f18e0157c05861564": {
            "name": "UNISWAP_V3_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0xa51afafe0263b40edaef0df8781ea9aa03e381a3": {
            "name": "UNISWAP_V4_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0xf2614a233c7c3e7f08b1f887ba133a13f1eb2c55": {
            "name": "SUSHISWAP_ROUTER",
            "type": "Dex",
            "key_method": "",
        },
        "0xaf88d065e77c8cc2239327c5edb3a432268e5831": {
            "name": "USDC",
            "type": "StableCoin",
            "key_method": "",
        },
        "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9": {
            "name": "USDT",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1": {
            "name": "WETH",
            "type": "StableCoin",
            "key_method": "",
        },
        "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1": {
            "name": "DAI",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x4dbd4fc535ac27206064b68ffcf827b0a60bab3f": {
            "name": "ARBITRUM_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x7e7a0e201fd38d3adaa9523da6c109a07118c96a": {
            "name": "SYNAPSE_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x5427fefa711eff984124bfbb1ab6fbf5e3da1820": {
            "name": "CELER_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5": {
            "name": "ACROSS_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0x0e83ded9f80e1c92549615d96842f5cb64a08762": {
            "name": "OWLTO_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0xa0c68c638235ee32657e8f720a23cec1bfc77c77": {
            "name": "POLYGON_POS_BRIDGE",
            "type": "Bridge",
            "key_method": "",
        },
        "0xc026395860db2d07ee33e05fe50ed7bd583189c7": {
            "name": "STARGATE_V2_BRIDGE_USDC",
            "type": "Bridge",
            "key_method": "",
        },
        "0x933597a323eb81cae705c5bc29985172fd5a3973": {
            "name": "STARGATE_V2_BRIDGE_USDT",
            "type": "Bridge",
            "key_method": "",
        },
        "0x6065a982f04f759b7d2d042d2864e569fad84214": {
            "name": "CELER_CCTP_PROXY",
            "type": "Bridge",
            "key_method": "",
        },
    },
    8453: {
        "0xb125e6687d4313864e53df431d5425969c15eb2f": {
            "name": "COMPOUND_V3_USDC",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0x46e6b214b524310239732d51387075e0e70970bf": {
            "name": "COMPOUND_V3_ETH",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0x9c4ec768c28520b50860ea7a15bd7213a9ff58bf": {
            "name": "COMPOUND_V3_USDBC",
            "type": "Lending",
            "key_method": "0xf2b9fdb8",
        },
        "0xa238dd80c259a72e81d7e4664a9801593f98d1c5": {
            "name": "AAVE_V3_POOL",
            "type": "Lending",
            "key_method": "0x617ba037",
        },
        "0xbeef010f9cb27031ad51e3333f9af9c6b1228183": {
            "name": "MORPHO_STEAKHOUSE_USDC",
            "type": "Lending",
            "key_method": "0x6e553f65",
        },
        "0xc0c5689e6f4d256e861f65465b691aeecc0deb12": {
            "name": "MORPHO_GAUNTLET_USDC_CORE",
            "type": "Lending",
            "key_method": "0x6e553f65",
        },
        "0xee8f4ec5672f09119b96ab6fb59c27e1b7e44b61": {
            "name": "MORPHO_GAUNTLET_USDC_PRIME",
            "type": "Lending",
            "key_method": "0x6e553f65",
        },
        "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": {
            "name": "USDC",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x4200000000000000000000000000000000000006": {
            "name": "WETH",
            "type": "StableCoin",
            "key_method": "",
        },
        "0x50c5725949a6f0c72e6c4a641f24049a917db0cb": {
            "name": "DAI",
            "type": "StableCoin",
            "key_method": "",
        },
    },
}
