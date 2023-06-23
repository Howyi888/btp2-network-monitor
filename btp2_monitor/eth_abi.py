#!/usr/bin/env python3

BMCPeriphery = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "_src",
          "type": "string"
        },
        {
          "indexed": True,
          "internalType": "int256",
          "name": "_nsn",
          "type": "int256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "_next",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "_event",
          "type": "string"
        }
      ],
      "name": "BTPEvent",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "_sender",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "_receiver",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "_amount",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "int256",
          "name": "_nsn",
          "type": "int256"
        }
      ],
      "name": "ClaimReward",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "_sender",
          "type": "address"
        },
        {
          "indexed": True,
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "int256",
          "name": "_nsn",
          "type": "int256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "_result",
          "type": "uint256"
        }
      ],
      "name": "ClaimRewardResult",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint8",
          "name": "version",
          "type": "uint8"
        }
      ],
      "name": "Initialized",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "_next",
          "type": "string"
        },
        {
          "indexed": True,
          "internalType": "uint256",
          "name": "_seq",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "bytes",
          "name": "_msg",
          "type": "bytes"
        }
      ],
      "name": "Message",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "_prev",
          "type": "string"
        },
        {
          "indexed": True,
          "internalType": "uint256",
          "name": "_seq",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "bytes",
          "name": "_msg",
          "type": "bytes"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "_ecode",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "_emsg",
          "type": "string"
        }
      ],
      "name": "MessageDropped",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_receiver",
          "type": "string"
        }
      ],
      "name": "claimReward",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "clearSeq",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_prev",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_seq",
          "type": "uint256"
        },
        {
          "components": [
            {
              "internalType": "string",
              "name": "src",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "dst",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "svc",
              "type": "string"
            },
            {
              "internalType": "int256",
              "name": "sn",
              "type": "int256"
            },
            {
              "internalType": "bytes",
              "name": "message",
              "type": "bytes"
            },
            {
              "internalType": "int256",
              "name": "nsn",
              "type": "int256"
            },
            {
              "components": [
                {
                  "internalType": "string",
                  "name": "network",
                  "type": "string"
                },
                {
                  "internalType": "uint256[]",
                  "name": "values",
                  "type": "uint256[]"
                }
              ],
              "internalType": "struct Types.FeeInfo",
              "name": "feeInfo",
              "type": "tuple"
            }
          ],
          "internalType": "struct Types.BTPMessage",
          "name": "_msg",
          "type": "tuple"
        }
      ],
      "name": "dropMessage",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_sender",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "internalType": "int256",
          "name": "_nsn",
          "type": "int256"
        },
        {
          "internalType": "uint256",
          "name": "_result",
          "type": "uint256"
        }
      ],
      "name": "emitClaimRewardResult",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getBtpAddress",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_to",
          "type": "string"
        },
        {
          "internalType": "bool",
          "name": "_response",
          "type": "bool"
        }
      ],
      "name": "getFee",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getNetworkAddress",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getNetworkSn",
      "outputs": [
        {
          "internalType": "int256",
          "name": "",
          "type": "int256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "getReward",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "getStatus",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "rxSeq",
              "type": "uint256"
            },
            {
              "internalType": "uint256",
              "name": "txSeq",
              "type": "uint256"
            },
            {
              "components": [
                {
                  "internalType": "uint256",
                  "name": "height",
                  "type": "uint256"
                },
                {
                  "internalType": "bytes",
                  "name": "extra",
                  "type": "bytes"
                }
              ],
              "internalType": "struct IBMV.VerifierStatus",
              "name": "verifier",
              "type": "tuple"
            },
            {
              "internalType": "uint256",
              "name": "currentHeight",
              "type": "uint256"
            }
          ],
          "internalType": "struct Types.LinkStatus",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_prev",
          "type": "string"
        },
        {
          "internalType": "bytes",
          "name": "_msg",
          "type": "bytes"
        }
      ],
      "name": "handleRelayMessage",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_network",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_bmcManagementAddr",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_bmcServiceAddr",
          "type": "address"
        }
      ],
      "name": "initialize",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_next",
          "type": "string"
        },
        {
          "internalType": "bytes",
          "name": "_msg",
          "type": "bytes"
        }
      ],
      "name": "sendInternal",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_to",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_svc",
          "type": "string"
        },
        {
          "internalType": "int256",
          "name": "_sn",
          "type": "int256"
        },
        {
          "internalType": "bytes",
          "name": "_msg",
          "type": "bytes"
        }
      ],
      "name": "sendMessage",
      "outputs": [
        {
          "internalType": "int256",
          "name": "",
          "type": "int256"
        }
      ],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "receive"
    }
  ]

BMCManagement = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint8",
          "name": "version",
          "type": "uint8"
        }
      ],
      "name": "Initialized",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "initialize",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "setBMCPeriphery",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getBMCPeriphery",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "setBMCService",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getBMCService",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "addOwner",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "removeOwner",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_owner",
          "type": "address"
        }
      ],
      "name": "isOwner",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_svc",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "addService",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_svc",
          "type": "string"
        }
      ],
      "name": "removeService",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getServices",
      "outputs": [
        {
          "components": [
            {
              "internalType": "string",
              "name": "svc",
              "type": "string"
            },
            {
              "internalType": "address",
              "name": "addr",
              "type": "address"
            }
          ],
          "internalType": "struct Types.Service[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_net",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "addVerifier",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_net",
          "type": "string"
        }
      ],
      "name": "removeVerifier",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getVerifiers",
      "outputs": [
        {
          "components": [
            {
              "internalType": "string",
              "name": "net",
              "type": "string"
            },
            {
              "internalType": "address",
              "name": "addr",
              "type": "address"
            }
          ],
          "internalType": "struct Types.Verifier[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "addLink",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "removeLink",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getLinks",
      "outputs": [
        {
          "internalType": "string[]",
          "name": "",
          "type": "string[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "addRelay",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "removeRelay",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "getRelays",
      "outputs": [
        {
          "internalType": "address[]",
          "name": "",
          "type": "address[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_dst",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        }
      ],
      "name": "addRoute",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_dst",
          "type": "string"
        }
      ],
      "name": "removeRoute",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getRoutes",
      "outputs": [
        {
          "components": [
            {
              "internalType": "string",
              "name": "dst",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "next",
              "type": "string"
            }
          ],
          "internalType": "struct Types.Route[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string[]",
          "name": "_dst",
          "type": "string[]"
        },
        {
          "internalType": "uint256[][]",
          "name": "_value",
          "type": "uint256[][]"
        }
      ],
      "name": "setFeeTable",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string[]",
          "name": "_dst",
          "type": "string[]"
        }
      ],
      "name": "getFeeTable",
      "outputs": [
        {
          "internalType": "uint256[][]",
          "name": "_feeTable",
          "type": "uint256[][]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_to",
          "type": "string"
        },
        {
          "internalType": "bool",
          "name": "_response",
          "type": "bool"
        }
      ],
      "name": "getFee",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        },
        {
          "internalType": "uint256[]",
          "name": "",
          "type": "uint256[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "setFeeHandler",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getFeeHandler",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_src",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_seq",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "_svc",
          "type": "string"
        },
        {
          "internalType": "int256",
          "name": "_sn",
          "type": "int256"
        },
        {
          "internalType": "int256",
          "name": "_nsn",
          "type": "int256"
        },
        {
          "internalType": "string",
          "name": "_feeNetwork",
          "type": "string"
        },
        {
          "internalType": "uint256[]",
          "name": "_feeValues",
          "type": "uint256[]"
        }
      ],
      "name": "dropMessage",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_svc",
          "type": "string"
        }
      ],
      "name": "getService",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_net",
          "type": "string"
        }
      ],
      "name": "getVerifier",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_link",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "isLinkRelay",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_dst",
          "type": "string"
        }
      ],
      "name": "resolveNext",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_from",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_reachable",
          "type": "string"
        }
      ],
      "name": "addReachable",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_from",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_reachable",
          "type": "string"
        }
      ],
      "name": "removeReachable",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_dst",
          "type": "string"
        }
      ],
      "name": "getHop",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
  ]