# BTP2 Network Monitor

This is simple network monitor. It gathers links status from BMC contracts
based on the configuration file. And it shows network status based on
the gathered information.


## Network Configuration

Network configuration is stored in `networks.json` containing a list of
network informations.

**Network Information**

| Name       | Type    | Optional | Description                                         |
|:-----------|:--------|:--------:|:----------------------------------------------------|
| `type`     | string  |          | Network type (`eth`, `icon`)                        |
| `endpoint` | string  |          | End-point URL for RPC                               |
| `network`  | string  |          | BTP Network Address for the network                 |
| `name`     | string  |   YES    | Name of the network to use in UI                    |
| `bmc`      | string  |          | Contract address of the BMC                         |
| `bmcm`     | string  |   YES    | Contract address of the BMC Management              |
| `bmcs`     | string  |   YES    | Contract address of the BMC Service                 |
| `rx_limit` | integer |   YES    | Time limit to receive message after the transaction |
| `tx_limit` | integer |   YES    | Time limit to get finality to transmit message      |
| `symbol`   | string  |   YES    | Symbol for native coin for fee                      |
| `decimal`  | integer |   YES    | Number of decimals in the fee (default: 19)         |

So, estimated time limit after sending TX to send a message is sum of the followings.
* `rx_limit` of source chain : to request message delivery with user's transaction 
* `tx_limit` of source chain : to confirm message delivery request on the source.
* `rx_limit` of destination chain : to receive message by relay's transaction

It's estimated time limit. So sometimes it can't shorten or extended by network condition.
It assumes that the network has a problem if it exceeds.

**Example**
```json
[
    {
        "type": "icon",
        "endpoint": "https://berlin.net.solidwallet.io/api/v3/icon_dex",
        "network": "0x7.icon",
        "name": "ICON Berlin",
        "bmc": "cxf1b0808f09138fffdb890772315aeabb37072a8a",
        "rx_limit": 4,
        "symbol" : "tICX"
    },
    {
        "type": "icon",
        "endpoint": "https://ctz.altair.havah.io/api/v3/icon_dex",
        "network": "0x111.icon",
        "name": "HAVAH BTP",
        "bmc": "cx683a92f72cc2fe9a7a617019a8d6fcba6b6c06b7",
        "rx_limit": 4,
        "symbol" : "tHVH"
    }
]
```

## Network Status

Every BMC provides a list of Links. The Link is BTP Adress of the connected BMC.
With it, we can query a status of the Link.
It includes following information.

| Name              | Descripion                                  |
|:------------------|:--------------------------------------------|
| `tx_seq`          | Next sequence number for sending messages   |
| `rx_seq`          | Next sequence number for receiving messages |
| `current_height`  | Block height of the query                   |
| `verifier.height` | Last verified height of the block           |
| `verifier.extra`  | Extra data to present verifier status       |

After founding new TX sequence in the source, the RX sequence should
increase accordingly if the relay works well.
Otherwise, the RX sequence number of the target chain will remain lower
then the TX sequence number of the source.

The monitor records timestamp for when it sees new sending sequence number
from source, then it waits for increment of receiving sequence number
in `rx_limit` of the source + `tx_limit` of the destination.

## CUI Installation

You should check out the source with git or other tools.
Then enter the directory then continue.

```shell
pip install .
```

## CUI Usage

To print status information for once.
```shell
btp2-monitor --networks networks.json status
```

To monitor with CUI.
```shell
btp2-monitor --networks networks.json monitor
```

## WebUI Installation

To use web service, you recommend for you to install docker first.
Then checkout the source with git or other tools.
Then enter the directory then continue.

```shell
./build.sh
```

## WebUI Usage

Make a directory (ex: `data`) and put configuration file.

```shell
mkdir data
cp networks.json data/
```

Then start container consider followings.
* Mount the data directory containing the configuration to `/app/data` folder.
* Decide port to access it.

```shell
docker run -it -d --name btp2-monitor \
    -v data:/app/data \
    -p 8000:<my_port> btp2-monitor
```

Then bring up your browser, then enter URL `http://localhost:<my_port>`

For OpenAPIs, use `http://localhost:<my_port>/docs`.

## WebUI developer usage

You can start local server for debug. It automatically updates
web page according to python code changes and web content changes.

```shell
./run.sh
```